import os
import subprocess
from mr.developer.svn import SVNWorkingCopy
from bda.recipe.deployment.common import DeploymentError
from bda.recipe.deployment.common import DeploymentPackage
import logging

log = logging.getLogger('bda.recipe.deployment svn')


class SVNConnector(SVNWorkingCopy):

    def __init__(self, package):
        if not package.package_uri.endswith('trunk') \
           and '/branches/' not in package.package_uri:
            msg = u"Invalid repository structure. Could only handle " + \
                  u"packages contained either in 'svn_url/trunk' or " + \
                  u"in 'svn_url/branches/NAME'"
            raise DeploymentError(msg)
        self.package = package
        self.source = dict()
        self.source['name'] = package.package
        self.source['path'] = package.package_path
        self.source['url'] = package.package_uri

    @property
    def rc_source(self):
        return 'svn %s' % self._rc_uri

    def commit(self, resource, message):
        url = self.package.package_uri
        resource = os.path.join(self.package.config.sources_dir,
                                self.package.package,
                                resource)
        args = ["svn", "ci", resource, '-m"%s"' % message]
        kwargs = {}
        msg = ' '.join(args)
        log.info(msg)
        stdout, stderr, returncode = self._svn_communicate(args, url,
                                                           **kwargs)

    def commit_buildout(self, resource, message):
        self.commit(resource, message)

    def merge(self, resource=None):
        """
        svn ci path/to/foo -m 'RC Merge'
        svn merge https://foo/branches/rc https://foo/trunk .
        """
        self.commit('', 'RC Merge')
        from_resource = self.package.package_uri
        to_resource = self._rc_uri
        wc_resource = os.path.join(self.package.config.sources_dir,
                                   self.package.package)
        if resource is not None:
            from_resource = '/'.join([from_resource, resource])
            to_resource = '/'.join([to_resource, resource])
            wc_resource = os.path.join(wc_resource, resource)
        args = ["svn", "merge", to_resource, from_resource, wc_resource]
        log.info(' '.join(args))
        kwargs = {}
        stdout, stderr, returncode = self._svn_communicate(args, from_resource,
                                                           **kwargs)
        if returncode != 0:
            msg = "Subversion merge for '%s' failed.\n%s" % (resource, stderr)
            raise DeploymentError(msg)
        if kwargs.get('verbose', False):
            return stdout

    def creatercbranch(self):
        source_uri = self.package.package_uri
        branches_path = '%s/branches' % self._svn_base_path
        if not self._svn_exists(branches_path):
            msg = "'Create branches directory for %s'" % self.package.package
            log.info(msg)
            args = ["svn", "mkdir", branches_path, '-m', msg]
            kwargs = {}
            stdout, stderr, returncode = self._svn_communicate(args,
                                                               source_uri,
                                                               **kwargs)
            if returncode != 0:
                msg = u"'Cannot create directory %s'" % branches_path
                raise DeploymentError(msg)
        if not self._svn_exists(self._rc_uri):
            msg = "'Create RC branch for %s'" % self.package.package
            log.info(msg)
            self._svn_copy(source_uri, self._rc_uri, msg)
        else:
            msg = "'RC branch for %s already exists. Use merge script in " + \
                  "RC environment to synchronize resources.'"
            msg = msg % self.package.package
            log.info(msg)

    def tag(self):
        msg = "'Tag %s version %s'" % (self.package.package,
                                       self.package.version)
        log.info(msg)
        if self._svn_exists(self._tag_uri):
            msg = "Tagging for '%s' failed. Version %s already exists" % (
                self.package.package, self.package.version
            )
            raise DeploymentError(msg)
        self.commit('', 'RC Tag')
        tags_path = '%s/tags' % self._svn_base_path
        if not self._svn_exists(tags_path):
            url = self.package.package_uri
            msg = "'Create tags directory for %s'" % self.package.package
            log.info(msg)
            args = ["svn", "mkdir", tags_path, '-m', msg]
            kwargs = {}
            stdout, stderr, returncode = self._svn_communicate(args, url,
                                                               **kwargs)
            if returncode != 0:
                msg = u"'Cannot create directory %s'" % tags_path
                raise DeploymentError(msg)
        msg = "'Tag %s version'" % self.package.version
        self._svn_copy(self.package.package_uri, self._tag_uri, msg)

    def _svn_exists(self, uri):
        log.info("Check for %s" % uri)
        cmd = subprocess.Popen(["svn", "ls", "--non-interactive", uri],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            log.info("...not found %s" % uri)
            return False
        log.info("...found %s" % uri)
        return True

    def _svn_copy(self, source, target, message):
        url = self.package.package_uri
        args = ["svn", "cp", source, target, '-m', message]
        log.info(' '.join(args))
        kwargs = {}
        stdout, stderr, returncode = self._svn_communicate(args, url, **kwargs)
        if returncode != 0:
            msg = "Subversion copy failed.\n%s -> %s\n%s" % (source,
                                                             target, stderr)
            raise DeploymentError(msg)
        if kwargs.get('verbose', False):
            return stdout

    @property
    def _svn_base_path(self):
        uri = self.package.package_uri
        idx = uri.find('/trunk')
        if idx < 1:
            idx = idx = uri.find('/branches/')
        if idx < 1:
            raise ValueError(
                'URI not valid (trunk or branches needed): %s' % uri
            )
        return uri[:idx]

    @property
    def _rc_uri(self):
        uri = '{0}/branches/{1}'.format(
            self._svn_base_path,
            self.package.branches_path
        )
        if self.package.package_uri.endswith('/trunk'):
            return uri
        idx = self.package.package_uri.rfind('/') + 1
        uri += '-%s' % self.package.package_uri[idx:]
        return uri

    @property
    def _tag_uri(self):
        return '%s/tags/%s' % (self._svn_base_path, self.package.version)

DeploymentPackage.connectors['svn'] = SVNConnector
