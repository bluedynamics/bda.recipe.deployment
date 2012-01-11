import os
import subprocess
from mr.developer.git import gitWorkingCopyFactory
from bda.recipe.deployment.common import DeploymentError
from bda.recipe.deployment.common import DeploymentPackage
import logging

class GitConnector(object):
    
    def __init__(self, package):
        self.package = package
        self.source = dict()
        self.source['name'] = package.package
        self.source['path'] = package.package_path
        self.source['url'] = package.package_uri
        self.git_wc = gitWorkingCopyFactory(self.source)
                       
    def commit(self, resource='-a', message='bda.recipe.deployment run'):
        """Commit means here a commit and push in one
        """
        cmd = self.git_wc.run_git(["commit", resource, "--quiet", '-m', 
                                   message], cwd=self.source['path'])
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            raise DeploymentError("git commit of '%s' failed.\n%s" % \
                                  (resource, stderr))
        cmd = self.git_wc.run_git(["push", "--quiet"], cwd=self.source['path'])
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            raise DeploymentError("git push of '%s' failed.\n%s" % \
                                  (resource, stderr))        
    
    def merge(self, resource):
        """merges changes from dev branch to rc branch"""
        raise NotImplementedError('TODO')
    
    def creatercbranch(self):
        """creates rc branch if not exists"""
        # check if clean, if not commit
        # check if branch already exists
        # if yes, log and return direct        
        # create local branch
        # push branch to server
        raise NotImplementedError('TODO')
    
    def tag(self):
        """Tag package from rc  with version. Use version of
        package ``setup.py``
        """
        # check if clean, if not commit
        # check if tag for current version exists
        # if yes raise DeploymentError
        # set tag for current rc branch revision 
        raise NotImplementedError('TODO')
        
DeploymentPackage.connectors['git'] = GitConnector