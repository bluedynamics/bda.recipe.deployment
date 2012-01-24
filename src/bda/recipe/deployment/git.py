import os
import subprocess
from mr.developer.git import gitWorkingCopyFactory
from bda.recipe.deployment.common import DeploymentError
from bda.recipe.deployment.common import DeploymentPackage
import logging

log = logging.getLogger('bda.recipe.deployment git')

CLEAN, DIRTY = 'clean', 'dirty'

class GitConnector(object):
    
    def __init__(self, package):
        self.package = package
        self.source = dict()
        self.source['name'] = package.package
        self.source['path'] = package.package_path
        self.source['url'] = package.package_uri
        self.git_wc = gitWorkingCopyFactory(self.source)
    
    def _rungit(self, command, msg=''):
        cmd = self.git_wc.run_git(command, cwd=self.source['path'])
        stdout, stderr = cmd.communicate()
        if cmd.returncode == 0:
            return stdout, stderr, cmd
        log.error(msg)
        command = 'git %s' % ' '.join(command)
        message = '\n'.join([command, msg, stdout, stderr]) 
        raise DeploymentError('Failed command: %s' % message)

    def _pull(self, branch='master'):
        log.info('Initiate pull origin %s' % branch)
        cmd = ['pull', 'origin', branch]
        stdout, stderr, cmd = self._rungit(cmd)
        log.info('Pull done.')                        
                       
    def commit(self, resource='-a', message='bda.recipe.deployment run'):
        """Commit means here a commit and push in one
        """
        log.info('Initiate commit  %s' % (resource == '-a' and 'all' or 
                                          resource))
        stdout, stderr, cmd = self._rungit(["commit", resource, '-m', message])
        stdout, stderr, cmd = self._rungit(["push"])
        log.info('Commit done.')                        

    def _has_rc_branch(self, remote=False):
        branches = self._get_branches()
        context = remote and 'origin' or None
        return bool([_ for _ in branches 
                     if _['branch']=='rc' and _['remote']==context])
        
    def _current_branch(self):
        return [_['branch'] for _ in self._get_branches() if _['current']][0]
    
    def _get_branches(self):
        """a list with value as dict with:
            * key=branch: branch-name
            * key=remote: remote-name or None (for local)
            * key=current: (bool) (only possible for local)
            * key=alias: (string or None) this branch is the HEAD or other alias
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
                if item['branch'] != branchname or item['remote'] != remotename:
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
            log.info('Remote rc branch exists, checkout')
            stdout, stderr, cmd = self._rungit(["checkout", "-b", "rc", 
                                                "origin/rc"])
            return True
        else:
            log.info('No remote rc branch, checkout new and push')
            stdout, stderr, cmd = self._rungit(["checkout", "-b", "rc"])
            stdout, stderr, cmd = self._rungit(["push", "-u", "origin", "rc"])
            return True
    
    def merge(self, resource=None):
        """merges changes from dev branch to rc branch"""
        if self.status == DIRTY:
            self.commit(message='bda.recipe.deployment pre merge commit')
        if self.status == DIRTY:
            raise DeploymentError('Not clean after pre merge commit: %s' %\
                                  self.source['name'])
        if not self._has_rc_branch():
            self.creatercbranch()
        self._pull()
        self._pull('rc')
        stdout, stderr, cmd = self._rungit(["checkout", "rc"])
        stdout, stderr, cmd = self._rungit(["merge", "master"])
    
    
    def tag(self):
        """Tag package from rc  with version. Use version of
        package ``setup.py``
        """
        # check if clean, if not commit
        # check if tag for current version exists, if yes raise DeploymentError
        # set tag for current rc branch revision 
        # commit (needed for a tag, need to figure out) 
        # push changes to server  
        raise NotImplementedError('TODO')
    
    # proxy method
    @property
    def status(self):
        return self.git_wc.status()
        
DeploymentPackage.connectors['git'] = GitConnector