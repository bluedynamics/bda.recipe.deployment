import os
import sys
import logging
from bda.recipe.deployment import env
from bda.recipe.deployment.common import (
    DeploymentError,
    Config,
    ReleaseRC,
    PackageVersion,
    PWDManager,
    DeploymentPackage,
)

log = logging.getLogger('bda.recipe.deployment')

def repopasswd(*args):
    args = args or sys.argv[1:]
    if len(args) != 1:
        log.error("Usage: repopasswd [servername]")
        sys.exit(2)
    log.info("Set user and password for server")
    server = args[0]
    config = Config(env.CONFIG_PATH)
    if not config.config.has_option('distserver', server):
        msg = "Cannot find desired server. Available servers are:\n"
        for k, v in config.config.items('distserver'):
            msg += "  * %s\n" % k
        log.error(msg)
        sys.exit(2)
    pwdmgr = PWDManager(server)
    pwdmgr.set()

def version(*args):
    args = args or sys.argv[1:]
    if len(args) != 2:
        if len(args)==1:
            return showversion(*args)
        log.error("Usage: version PACKAGE [VERSION]")
        sys.exit(2)
    log.info("Set version for package")
    package, version = args
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage._check_environment('set_version', 'dev')
    except DeploymentError, e:
        log.error("Cannot set version: %s" % e)
        return
    path = os.path.join(config.sources_dir, package, 'setup.py')
    if not os.path.exists(path):
        log.error("Invalid package name %s" % package)
    pv = PackageVersion(path)
    pv.version = version
    
def showversion(*args):    
    args = args or sys.argv[1:]
    if len(args) != 1:
        log.error("Usage: showversion [PACKAGE] ")
        sys.exit(2)
    log.debug("Show version")
    package = args[0]
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    log.info("Version: %s = %s" % (package, deploymentpackage.version))

def commit(*args):
    args = args or sys.argv[1:]
    if len(args) != 3:
        log.error("Usage: commit [package] [resource] [message]")
        sys.exit(2)
    log.info("Commit resource")
    package, resource, message = args
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage.commit(resource, message)
    except DeploymentError, e:
        log.error("Committing failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)

def merge(*args):
    args = args or sys.argv[1:]
    if len(args) < 1:
        log.error("Usage: merge PACKAGE [RESOURCE]")
        sys.exit(2)
    log.info("Merge resource to RC")
    package = args[0]
    resource = len(args) > 1 and args[1] or None
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage.merge(resource)
    except DeploymentError, e:
        log.error("Merging failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)
    
def creatercbranch(*args):
    args = args or sys.argv[1:]
    if len(args) < 1:
        log.error("Usage: creatercbranch [--all] | [package] [package2] ... ")
        sys.exit(2)
    config = Config(env.CONFIG_PATH)
    if args[0].strip() == '--all':        
        packages = config.as_dict('packages').keys()
    else: 
        packages = args
    for package in packages:
        deploymentpackage = DeploymentPackage(config, package)
        try:
            deploymentpackage.creatercbranch()
        except DeploymentError, e:
            log.error("Creating RC branch failed: %s" % e)
            continue
        except Exception, e:
            log.error("An error occured: %s" % e)      
    
def tag(*args):
    args = args or sys.argv[1:]
    if len(args) != 1:
        log.error("Usage: tag [package]")
        sys.exit(2)
    log.info("Tag package")
    package = args[0]
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage.tag()
    except DeploymentError, e:
        log.error("Tagging failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)

def release(*args):
    args = args or sys.argv[1:]
    if len(args) != 1:
        log.error("Usage: release [packagename]")
        sys.exit(2)
    log.info("Release package")
    package = args[0]
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage.release()
    except DeploymentError, e:
        log.error("Releasing failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)

def exportliveversion(*args):
    args = args or sys.argv[1:]
    if len(args) != 1:
        log.error("Usage: exportliveversion [packagename]")
        sys.exit(2)
    log.info("Export live version")
    package = args[0]
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage.export_version()
    except DeploymentError, e:
        log.error("Exporting failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)

def exportrcsource(*args):
    args = args or sys.argv[1:]
    if len(args) != 1:
        log.error("Usage: exportrcsource [--all] | [packagename]")
        sys.exit(2)
    config = Config(env.CONFIG_PATH)
    if args[0].strip() == '--all':        
        packages = config.as_dict('packages').keys()
    else: 
        packages = args
    log.info("Export rc source")
    for package in packages:        
        deploymentpackage = DeploymentPackage(config, package)
        try:
            deploymentpackage.export_rc()
        except DeploymentError, e:
            log.error("Exporting failed: %s" % e)
            continue
        except Exception, e:
            log.error("An error occured: %s" % e)
    
def deploycandidate():
    """deploy to release candidate
     
    ./bin/deployrc PACKAGENAME VERSIONNUMBER
    
    - set version
    - commit setup.py
    - create rc branch if not exist
    - export rc sources
    - commit rc sources    
    """
    if len(sys.argv) != 3:
        log.error("Usage: %s [packagename] [version]" % sys.argv[0])
        sys.exit(2)    
    package = sys.argv[1]
    newversion = sys.argv[2]
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage._check_environment('deploycandidate', 'dev')
    except DeploymentError, e:
        log.error("Cannot deploy candidate: %s" % e)
        return
    log.info("Complete deployment of release candidate %s with version %s" % 
             (package, newversion))
    version(package, newversion)
    commit(package, 'setup.py', 'Version Change')
    creatercbranch(package)
    exportrcsource(package)
    deploymentpackage.commit_rc_source()

def deployrelease():
    """deploy to release on package index
    
    ./bin/deployrelease [packagename]
    
    - tag version
    - export live version
    - release to package index server
    - commit live versions   
    """
    if len(sys.argv) != 2:
        log.error("Usage: %s [packagename]" % sys.argv[0])
        sys.exit(2)
    package = sys.argv[1]
    config = Config(env.CONFIG_PATH)
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage._check_environment('deploycandidate', 'rc')
    except DeploymentError, e:
        log.error("Cannot deploy release: %s" % e)
        return 
    log.info("Complete deployment of final package %s" % package)
    try:
        deploymentpackage.tag()
    except DeploymentError, e:
        log.error("Tagging failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)
    try:
        deploymentpackage.export_version()
    except DeploymentError, e:
        log.error("Exporting failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)
    try:
        deploymentpackage.release()
    except DeploymentError, e:
        log.error("Releasing failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)
    try:
        deploymentpackage.commit_live_versions()
    except Exception, e:
        log.error("An error occured: %s" % e)
        
def showall():
    config = Config(env.CONFIG_PATH)
    packages = sorted(config.as_dict('packages').keys())
    maxlen = max([len(_) for _ in packages])
    def fill(msg, ml=maxlen):
        return "%s%s" % (msg, ' ' * (ml-len(msg)))
    cols = ("%s " * 5)
    log.info(cols % (maxlen*'-', 10*'-', 10*'-', 10*'-', 10*'-'))
    log.info(cols % (fill('package'), 
                     fill('location', 10),                      
                     fill('release', 10), 
                     fill('svn (%s)' % config.env, 10),
                     fill('rc-branch', 10)))
    log.info(cols % (maxlen*'-', 10*'-', 10*'-', 10*'-', 10*'-'))
    for package in sorted(config.as_dict('packages').keys(), key=str.lower):
        dp = DeploymentPackage(config, package)        
        log.info(cols % (fill(package), 
                         fill(config.package(package), 10),
                         fill(dp.live_version or 'not set', 10),
                         fill(dp.version, 10),
                         fill(dp.rc_source and 'yes' or 'no', 10)))
    log.info(cols % (maxlen*'-', 10*'-', 10*'-', 10*'-', 10*'-'))
        
        