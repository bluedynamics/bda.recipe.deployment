import os
import logging
from argparse import ArgumentParser
from bda.recipe.deployment import env
from bda.recipe.deployment.common import (
    DeploymentError,
    Config,
    PackageVersion,
    PWDManager,
    DeploymentPackage,
)

log = logging.getLogger('bda.recipe.deployment')

config = Config(env.CONFIG_PATH)

#------------------------------------------------------------------------------

epilog = 'Current configured environment: '
epilog += (config.check_env('dev') and 'DEVELOPMENT') or \
          (config.check_env('rc') and 'RELEASE CANDIDATE') or \
          'NOT SET!'

#------------------------------------------------------------------------------

deployparser = ArgumentParser(description='BDA Deployment Process',
                              epilog=epilog)
deploy_subparsers = deployparser.add_subparsers(help='commands')


def deploy():
    args = deployparser.parse_args()
    args.func(args)
#------------------------------------------------------------------------------

singleparser = ArgumentParser(description='BDA Deployment Process: '
                                          'Helper Scripts',
                              epilog=epilog)
single_subparsers = singleparser.add_subparsers(help='commands')


def deploy_single():
    args = singleparser.parse_args()
    args.func(args)
#------------------------------------------------------------------------------


def repopasswd(arguments):
    log.info("Set user and password for server")
    pwdmgr = PWDManager(arguments.distserver[0])
    pwdmgr.set()

sub_rp = deploy_subparsers.add_parser('repopasswd',
                               help='Set user and password for server')
sub_rp.add_argument('distserver', nargs=1,
                   choices=[k for k,v in config.config.items('distserver')],
                   help='name of the distserver')
sub_rp.set_defaults(func=repopasswd)
#------------------------------------------------------------------------------


def _set_version(package, version):
    log.info("Set version for package")
    deploymentpackage = DeploymentPackage(config, package)
    path = os.path.join(config.sources_dir, package, 'setup.py')
    if not os.path.exists(path):
        log.error("Invalid package name %s" % package)
    pv = PackageVersion(path)
    pv.version = version


def _show_version(package):
    deploymentpackage = DeploymentPackage(config, package)
    log.info("Version: %s = %s" % (package, deploymentpackage.version))


def version(args):
    if config.check_env('dev') and args.version[0] is not 'show':
        return _set_version(args.package[0], args.version[0])
    return _show_version(args.package[0])

if config.check_env('dev'):
    sub_ver = deploy_subparsers.add_parser(
        'version',
        help='Shows or sets version of package'
    )
    sub_ver.add_argument('package', nargs=1, help='name of package')
    sub_ver.add_argument(
        'version', nargs='?', help='new version',
        default='show'
    )
    sub_ver.set_defaults(func=version)
if config.check_env('rc'):
    sub_ver = deploy_subparsers.add_parser(
        'version',
        help='Shows version of package'
    )
    sub_ver.add_argument('package', nargs=1, help='name of package')
    sub_ver.set_defaults(func=version)
#------------------------------------------------------------------------------


def info(args):
    packages = sorted(config.as_dict('packages').keys())
    maxlen = max([len(_) for _ in packages])

    def fill(msg, ml=maxlen):
        return "%s%s" % (msg, ' ' * (ml-len(msg)))
    cols = ("%s " * 5)
    log.info(cols % (maxlen*'-', 10*'-', 10*'-', 10*'-', 10*'-'))
    log.info(cols % (fill('package'),
                     fill('repo (%s)' % config.env, 10),
                     fill('live', 10),
                     fill('rc-branch', 10),
                     fill('location', 10),))
    log.info(cols % (maxlen*'-', 10*'-', 10*'-', 10*'-', 10*'-'))
    for package in sorted(config.as_dict('packages').keys(), key=str.lower):
        dp = DeploymentPackage(config, package)
        p_env = dp.package_options['env']
        rc = dp.rc_source and 'yes' or (p_env == 'rc' and p_env or '---')
        log.info(cols % (fill(package),
                         fill(dp.version, 10),
                         fill(dp.live_version or 'not set', 10),
                         fill(rc, 10),
                         fill(config.package(package), 10),))
    log.info(cols % (maxlen*'-', 10*'-', 10*'-', 10*'-', 10*'-'))

sub_inf = deploy_subparsers.add_parser(
    'info',
    help='Show information about current state.'
)
sub_inf.set_defaults(func=info)
#------------------------------------------------------------------------------


def _commit(package, resource, message):
    log.info("Commit resource")
    deploymentpackage = DeploymentPackage(config, package)
    try:
        deploymentpackage.commit(resource, message)
    except DeploymentError, e:
        log.error("Committing failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)


def commit(args):
    return _commit(args.package[0], args.resource[0], args.message[0])

sub_ci = single_subparsers.add_parser('commit',
                                      help='Commit (and push) a resource.')
sub_ci.add_argument('package', nargs=1, help='name of package')
sub_ci.add_argument('resource', nargs='?', help='path to resource')
sub_ci.add_argument('message', nargs='?', help='commit message')
sub_ci.set_defaults(func=commit, resource=None,
                    message='manual deployment commit')
#------------------------------------------------------------------------------


def merge(cargs):
    log.info("Merge resource to RC")
    deploymentpackage = DeploymentPackage(config, cargs.package[0])
    resource = None
    if cargs.resource:
        resource = cargs.resource[0]
    try:
        deploymentpackage.merge(resource)
    except DeploymentError, e:
        log.error("Merging failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)

if config.check_env('rc'):
    sub_merge = deploy_subparsers.add_parser('merge',
                                             help='Merge resource to RC')
    sub_merge.add_argument('package', nargs=1, help='name of package')
    sub_merge.add_argument('resource', nargs='?', help='path to resource')
    sub_merge.set_defaults(func=merge, resource=None)
#------------------------------------------------------------------------------


def _creatercbranch(all, packages):
    if all:
        packages = config.as_dict('packages').keys()
    for package in packages:
        deploymentpackage = DeploymentPackage(config, package)
        deploymentpackage.check_env("rc")
        try:
            deploymentpackage.creatercbranch()
        except DeploymentError, e:
            log.error("Creating RC branch failed: %s" % e)
            continue
        except Exception, e:
            log.error("An error occured: %s" % e)


def creatercbranch(args):
    return _creatercbranch(args.all, args.package)


if config.check_env('dev'):
    sub_crc = single_subparsers.add_parser(
        'creatercbranch',
        help='Create RC branch for one or more '
             'or all managed packages.')
    sub_crc_group = sub_crc.add_mutually_exclusive_group()
    sub_crc_group.add_argument('--all', '-a', action='store_true',
                               help='all managed packages')
    sub_crc_group.add_argument('--package', '-p', nargs='+', help='package(s)')
    sub_crc.set_defaults(func=creatercbranch)
#------------------------------------------------------------------------------


def tag(args):
    log.info("Tag package")
    deploymentpackage = DeploymentPackage(config, args.package[0])
    deploymentpackage.check_env(config.env)
    try:
        deploymentpackage.tag()
    except DeploymentError, e:
        log.error("Tagging failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)

sub_tag = single_subparsers.add_parser('tag', help='Tag a package')
sub_tag.add_argument('package', nargs=1, help='name of package')
sub_tag.set_defaults(func=tag)
#------------------------------------------------------------------------------


def release(cargs):
    log.info("Release package")
    deploymentpackage = DeploymentPackage(config, cargs.package[0])
    deploymentpackage.check_env(config.env)
    try:
        deploymentpackage.release()
    except DeploymentError, e:
        log.error("Releasing failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)

sub_rel = single_subparsers.add_parser('release', help='Release package')
sub_rel.add_argument('package', nargs=1, help='name of package')
sub_rel.set_defaults(func=release)
#------------------------------------------------------------------------------


def exportliveversion(*args):
    log.info("Export live version")
    deploymentpackage = DeploymentPackage(config, args.package[0])
    deploymentpackage.check_env(config.env)
    try:
        deploymentpackage.export_version()
    except DeploymentError, e:
        log.error("Exporting failed: %s" % e)
        return
    except Exception, e:
        log.error("An error occured: %s" % e)

if config.check_env('rc'):
    sub_elv = single_subparsers.add_parser('exportliveversion',
                                           help='Export live version cfg file')
    sub_elv.add_argument('package', nargs=1, help='name of package')
    sub_rel.set_defaults(func=exportliveversion)
#------------------------------------------------------------------------------


def _exportrcsource(_all, packages):
    if _all:
        packages = config.as_dict('packages').keys()
    log.info("Export rc source")
    for package in packages:
        #XXX check env of package match
        deploymentpackage = DeploymentPackage(config, package)
        try:
            deploymentpackage.export_rc()
        except DeploymentError, e:
            log.error("Exporting failed: %s" % e)
            continue
        except Exception, e:
            log.error("An error occured: %s" % e)


def exportrcsource(args):
    return _exportrcsource(args.all, args.package)


if config.check_env('dev'):
    sub_ers = single_subparsers.add_parser('exportrcsource',
                                           help='Export RC source cfg file')
    sub_ers_group = sub_ers.add_mutually_exclusive_group()
    sub_ers_group.add_argument('--all', '-a', action='store_true',
                               help='all managed packages')
    sub_ers_group.add_argument('--package', '-p', nargs='+', help='package(s)')
    sub_ers.set_defaults(func=exportrcsource)
#------------------------------------------------------------------------------


def candidate(args):
    """deploy to release candidate

    ./bin/deploy candidate PACKAGENAME VERSIONNUMBER

    - set version
    - commit setup.py
    - create rc branch if not exist
    - export rc sources
    - commit rc sources
    """
    package, newversion = args.package[0], args.version[0]
    deploymentpackage = DeploymentPackage(config, package)
    deploymentpackage.check_env("rc")
    log.info("Complete deployment of release candidate %s with version %s" %
             (package, newversion))
    try:
        _set_version(package, newversion)
        deploymentpackage.commit('setup.py', 'Version Change')
        deploymentpackage.creatercbranch()
        deploymentpackage.export_rc()
        deploymentpackage.commit_rc_source()
    except DeploymentError, e:
        log.error("Candidate deployment failed: %s" % e)
    except Exception, e:
        log.error("An error occured: %s" % e)
        raise

if config.check_env('dev'):
    sub_can = deploy_subparsers.add_parser(
        'candidate',
        help='Deploy package to release candidate')
    sub_can.add_argument('package', nargs=1, help='name of package')
    sub_can.add_argument('version', nargs=1, help='new version number')
    sub_can.set_defaults(func=candidate)
#------------------------------------------------------------------------------


def fullrelease(args):
    """deploy to release on package index

    ./bin/deploy release [packagename]

    - tag version
    - export live version
    - release to package index server
    - commit live versions
    """
    package = args.package[0]
    deploymentpackage = DeploymentPackage(config, package)
    deploymentpackage.check_env(config.env)
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
        deploymentpackage.commit_versions()
    except Exception, e:
        log.error("An error occured: %s" % e)

sub_rls = deploy_subparsers.add_parser(
    'release',
    help='Deploy release to package index'
)
sub_rls.add_argument('package', nargs=1, help='name of package')
sub_rls.set_defaults(func=fullrelease)
