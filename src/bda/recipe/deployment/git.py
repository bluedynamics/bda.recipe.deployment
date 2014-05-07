from mr.developer.git import GitWorkingCopy
from bda.recipe.deployment.common import DeploymentError
from bda.recipe.deployment.common import DeploymentPackage
import logging

log = logging.getLogger('bda.recipe.deployment git')

CLEAN, DIRTY = 'clean', 'dirty'


class GitConnector(object):

    def __init__(self, package):
        self.package = package

    @property
    def rc_source(self):
        return 'git {0} branch={1}'.format(
            self.package.package_uri,
            self.package.branchname
        )

    def source(self, context="package"):
        if context == 'package':
            return dict(name=self.package.package,
                        path=self.package.package_path,
                        url=self.package.package_uri)
        elif context == 'buildout':
            return dict(name='buildout',
                        path=self.package.buildout_base,
                        url=None)
        else:
            raise DeploymentError('Commit context "%s" not allowed.' % context)

    def git_wc(self, context="package"):
        return GitWorkingCopy(self.source(context=context))

    def _rungit(self, command, msg='', context='package'):
        """runs git command in a given context

        command
            list of strings (paramters) after git

        msg
            error message if command fails

        context
            string, one of 'package', 'buildout'

        """
        wc = self.git_wc(context=context)
        if context == 'package':
            cwd = self.package.package_path
        else:
            cwd = self.package.buildout_base
        cmd = wc.run_git(command, cwd=cwd)
        stdout, stderr = cmd.communicate()
        if cmd.returncode == 0:
            return stdout, stderr, cmd
        log.error(msg)
        command = '%s' % ' '.join(command)
        message = '\n'.join([command, msg, stdout, stderr])
        raise DeploymentError('Failed command: %s' % message)

    def _fetch(self):
        stdout, stderr, cmd = self._rungit(['fetch', 'origin'])

    def _rebase(self, branch='master'):
        log.info('Rebase %s' % branch)
        cmd = ['rebase', branch]
        stdout, stderr, cmd = self._rungit(cmd)
        log.info('Rebase done.')

    def commit(self, resource='-a', message='bda.recipe.deployment commit'):
        """Commit means here a commit and push in one
        """
        if self.status == CLEAN:
            log.info(
                'Abort commit %s, working directory is clean' %
                (resource == '-a' and 'all' or resource)
            )
            return
        log.info('Initiate commit %s' % (
            resource == '-a' and 'all' or resource))
        if resource != '-a':
            stdout, stderr, cmd = self._rungit(["add", resource])
        message = '"%s"' % message
        stdout, stderr, cmd = self._rungit(["commit", resource, '-m', message])
        stdout, stderr, cmd = self._rungit(["push"])
        log.info('Commit done.')

    def commit_buildout(self, resource='-a',
                        message='bda.recipe.deployment buildout commit'):
        if self.status_buildout == CLEAN:
            log.info(
                'Abort buildout commit  %s, working directory is clean' %
                (resource == '-a' and 'all' or resource)
            )
            return
        log.info(
            'Initiate buildout commit  %s' %
            (resource == '-a' and 'all' or resource)
        )
        if resource != '-a':
            stdout, stderr, cmd = self._rungit(["add", resource],
                                               context='buildout')
        stdout, stderr, cmd = self._rungit(["commit", resource, '-m', message],
                                           context='buildout')
        stdout, stderr, cmd = self._rungit(["push"], context='buildout')
        log.info('Commit done.')

    def _has_rc_branch(self, remote=False):
        branches = self._get_branches()
        context = remote and 'origin' or None
        return bool(
            [_ for _ in branches
             if _['branch'] == self.package.branch_name
             and _['remote'] == context]
        )

    def _current_branch(self):
        return [_['branch'] for _ in self._get_branches() if _['current']][0]

    def _get_branches(self):
        """a list with value as dict with:
            * key=branch: branch-name
            * key=remote: remote-name or None (for local)
            * key=current: (bool) (only possible for local)
            * key=alias: (string or None) this branch is the HEAD or other
                         alias
        """
        stdout, stderr, cmd = self._rungit(["branch", "-a"])
        result = list()
        aliases = dict()

        def _location_split(loc):
            if loc.startswith('remotes'):
                prefix, remotename, branchname = loc.split('/')
            elif '/' in loc:
                remotename, branchname = loc.split('/')
            else:
                remotename, branchname = None, loc
            return remotename, branchname

        for line in stdout.split('\n'):
            if not line:
                continue
            current = line.startswith('*')
            line = line[2:]
            if '->' in line:
                key, target = line.split('->')
                key = '/'.join(_location_split(key.strip()))
                aliases[key] = target.strip()
                continue
            if line.startswith('remotes'):
                prefix, remotename, branchname = line.split('/')
            else:
                remotename, branchname = None, line
            result.append(dict(branch=branchname,
                               remote=remotename,
                               current=current,
                               alias=None))

        for alias, target in aliases.items():
            remote, branchname = _location_split(target)

            for item in result:
                if item['branch'] != branchname or\
                        item['remote'] != remotename:
                    continue
                item['alias'] = alias
        return result

    def creatercbranch(self):
        """creates rc branch if not exists"""
        log.info('Initiate creation of RC branch')
        # check if clean, if not commit
        if self.status == DIRTY:
            self.commit(message='bda.recipe.deployment pre create rc branch')
        # check if branch already exists, if yes, log and return direct
        if self._has_rc_branch():
            log.warning('RC branch already exist, abort create.')
            # here (not sure) we might check if a remote branch exists and if
            # yes, connect it to the local branch, but OTOH this can be wrong
            return False
        if self._has_rc_branch(remote=True):
            log.info(
                'Remote rc branch '
                '{0} exists, checkout'.format(self.package.branch_name)
            )
            stdout, stderr, cmd = self._rungit(
                ["checkout", "-b", self.package.branch_name,
                 "origin/{0}".format(self.package.branch_name)]
            )
            stdout, stderr, cmd = self._rungit(["checkout", "master"])
            return True
        else:
            log.info('No remote rc branch, checkout new and push')
            stdout, stderr, cmd = self._rungit(
                ["checkout", "-b", self.package.branch_name]
            )
            stdout, stderr, cmd = self._rungit(
                ["push", "-u", "origin", self.package.branch_name]
            )
            stdout, stderr, cmd = self._rungit(["checkout", "master"])
            return True

    def merge(self, resource=None):
        """merges changes from dev branch to rc branch"""
        log.info('Merge master into rc branch')
        if self.status == DIRTY:
            self.commit(message='bda.recipe.deployment pre merge commit')
        if self.status == DIRTY:
            raise DeploymentError(
                'Not clean after pre merge commit: %s' % self.package.package
            )
        if not self._has_rc_branch():
            # hmm, do we need this?
            self.creatercbranch()

        stdout, stderr, cmd = self._rungit(["fetch"])
        self._rebase(self.package.branch_name)

        # Fetch changes
        stdout, stderr, cmd = self._rungit(
            ["merge", "origin/master", "-m",
             "RC Merge ({0})".format(self.package.branch_name)]
        )
        stdout, stderr, cmd = self._rungit(
            ["push", "-u", "origin", self.package.branch_name]
        )
        log.info('Merge done')

    def _tags(self):
        stdout, stderr, cmd = self._rungit(["tag"])
        return [_.strip() for _ in stdout.split('\n') if _.strip()]

    def _tag(self, version, msg):
        stdout, stderr, cmd = self._rungit(["tag", '-a', version, '-m', msg])

    def tag(self):
        """Tag package from rc  with version. Use version of
        package ``setup.py``
        """
        version = self.package.version
        log.info('Tag version %s' % version)
        if self.status == DIRTY:
            self.commit(message='bda.recipe.deployment pre tag commit')
        if version in self._tags():
            raise DeploymentError('Tag %s already exist for %s.' %
                                  (version, self.package.package))
        self._tag(version, 'version tag set by bda.recipe.deployment')
        stdout, stderr, cmd = self._rungit(["push", "--tags"])
        log.info('Tagging done')

    # proxy method
    @property
    def status(self):
        wc = self.git_wc()
        return wc.status()

    @property
    def status_buildout(self):
        wc = self.git_wc(context='buildout')
        return wc.status()

DeploymentPackage.connectors['git'] = GitConnector
