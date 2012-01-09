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
                
                
    def commit(self, resource, message):
        """Commit means here a commit and push in one
        """
        cmd = self.git_wc.run_git(["commit", resource, "--quiet", '-m', message])
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            raise DeploymentError("git commit of '%s' failed.\n%s" % \
                                  (resource, stderr))
        cmd = self.git_wc.run_git(["push", "--quiet"])
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            raise DeploymentError("git push of '%s' failed.\n%s" % \
                                  (resource, stderr))        
    
    def merge(self, resource):
        """merges changes from dev branch to rc branch"""
        raise NotImplementedError('TODO')
    
    def creatercbranch(self):
        """creates rc branch if not exists"""
        raise NotImplementedError('TODO')
    
    def tag(self):
        """Tag package from rc  with version. Use version of
        package ``setup.py``
        """
        raise NotImplementedError('TODO')
        
DeploymentPackage.connectors['git'] = GitConnector