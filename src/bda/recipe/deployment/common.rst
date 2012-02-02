Test common stuff
=================

Create dummy environment::

    >>> import os
    >>> os.mkdir(os.path.join(tempdir, 'sources'))
    >>> os.mkdir(os.path.join(tempdir, 'sources', 'foo.bar'))
    >>> os.mkdir(os.path.join(tempdir, 'sources', 'bar.baz'))

For version tagging and releasing, parameter ``version`` is expected in
``setup.py``::

    >>> SETUP_TMPL = """from setuptools import setup, find_packages
    ... import sys, os
    ...
    ... version = "1.0"
    ...
    ... setup(name="%(package)s",
    ...     version=version,
    ...     )
    ... """

    >>> path = os.path.join(tempdir, 'sources', 'foo.bar', 'setup.py')
    >>> file = open(path, 'w')
    >>> file.write(SETUP_TMPL % { 'package': 'foo.bar' })
    >>> file.close()

    >>> path = os.path.join(tempdir, 'sources', 'bar.baz', 'setup.py')
    >>> file = open(path, 'w')
    >>> file.write(SETUP_TMPL % { 'package': 'bar.baz' })
    >>> file.close()

Config gets stored in '.bda.recipe.deployment.cfg' by default::

    >>> path = os.path.join(tempdir, '.bda.recipe.deployment.cfg')
    >>> path
    '...bda.recipe.deployment.cfg'

Import Config::

    >>> from bda.recipe.deployment.common import Config

Define settings::

    >>> distserver = {
    ...     'bda': 'http://bda.org',
    ...     'pypi': 'http://pypi.org'
    ... }
    >>> packages = {
    ...     'foo.bar': 'bda env=dev',
    ...     'bar.baz': 'pypi',
    ... }
    >>> sources = {
    ...     'foo.bar': 'svn https://svn.plone.org/svn/collective/foo.bar/trunk',
    ...     'bar.baz': 'svn https://svn.plone.org/svn/collective/bar.baz/trunk',
    ... }
    >>> rc = os.path.join(tempdir, 'rc-sources.cfg')
    >>> live = os.path.join(tempdir, 'live-versions.cfg')
    >>> env = 'dev'
    >>> sources_dir = os.path.join(tempdir, 'sources')

Create new config::

    >>> buildout_base = '/home/USERNAME/bdarecipedeploymenttest'

    >>> config = Config(path, buildout_base, distserver, packages, sources, rc,
    ...                 live, env, sources_dir)

Query deployment information::

    >>> config.rc
    '/.../rc-sources.cfg'

    >>> config.live
    '/.../live-versions.cfg'

    >>> config.env
    'dev'

    >>> config.sources_dir
    '/.../sources'

    >>> config.distserver('bda')
    'http://bda.org'

    >>> config.distserver('pypi')
    'http://pypi.org'

    >>> config.distserver('inexistent')

    >>> config.package('foo.bar')
    'bda'

    >>> config.package_options('foo.bar')
    {'env': 'dev'}

    >>> config.package('bar.baz')
    'pypi'

    >>> config.package_options('bar.baz')
    {'env': 'rc'}

    >>> config.package('inexistent')

    >>> config.source('foo.bar')
    'svn https://svn.plone.org/svn/collective/foo.bar/trunk'

    >>> config.source('bar.baz')
    'svn https://svn.plone.org/svn/collective/bar.baz/trunk'

    >>> config.as_dict('distserver')
    {'bda': 'http://bda.org', 'pypi': 'http://pypi.org'}

    >>> config.as_dict('packages')
    {'bar.baz': 'pypi', 'foo.bar': 'bda env=dev'}

    >>> config.as_dict('sources')
    {'bar.baz': 'svn https://svn.plone.org/svn/collective/bar.baz/trunk',
    'foo.bar': 'svn https://svn.plone.org/svn/collective/foo.bar/trunk'}

``__call__`` dumps config file::

    >>> config()
    >>> file = open(path)
    >>> lines = [l for l in file.readlines()]
    >>> file.close()
    >>> lines
    ['[sources]\n',
    'bar.baz = svn https://svn.plone.org/svn/collective/bar.baz/trunk\n',
    'foo.bar = svn https://svn.plone.org/svn/collective/foo.bar/trunk\n',
    '\n',
    '[distserver]\n',
    'bda = http://bda.org\n',
    'pypi = http://pypi.org\n',
    '\n',
    '[packages]\n',
    'bar.baz = pypi\n',
    'foo.bar = bda env=dev\n',
    '\n',
    '[settings]\n',
    'buildout_base = /home/USERNAME/bdarecipedeploymenttest\n',
    'live = /.../live-versions.cfg\n',
    'sources_dir = /.../sources\n',
    'env = dev\n',
    'rc = /.../rc-sources.cfg\n',
    '\n']


Create config with existing content::

    >>> config = Config(path)
    >>> config.distserver(config.package('bar.baz'))
    'http://pypi.org'

Check ``PackageVersion`` object::

    >>> from bda.recipe.deployment.common import PackageVersion
    >>> path = os.path.join(config.sources_dir, 'foo.bar', 'setup.py')
    >>> version = PackageVersion(path)
    >>> version.version
    '1.0'

    >>> version.version = '1.1'
    >>> version.version
    '1.1'

    >>> file = open(path)
    >>> lines = [l for l in file.readlines()]
    >>> file.close()
    >>> lines
    ['from setuptools import setup, find_packages\n',
    'import sys, os\n',
    '\n',
    'version = "1.1"\n',
    '\n',
    'setup(name="foo.bar",\n',
    '    version=version,\n',
    '    )\n']

Check ``RcSourcesCFG`` object::

    >>> from bda.recipe.deployment.common import RcSourcesCFG
    >>> rcsources = RcSourcesCFG(config.rc)
    >>> rcsources.set('foo.bar',
    ...               'svn https://example.com/svn/foo.bar/branches/rc')
    >>> rcsources()
    >>> file = open(config.rc)
    >>> lines = [l for l in file.readlines()]
    >>> file.close()
    >>> lines
    ['[sources]\n',
    'foo.bar = svn https://example.com/svn/foo.bar/branches/rc\n',
    '\n']

    >>> os.remove(config.rc)

Check ``LiveVersionsCFG`` object::

    >>> from bda.recipe.deployment.common import LiveVersionsCFG
    >>> versions = LiveVersionsCFG(config.live)
    >>> versions.set('foo.bar', '1.1')
    >>> versions()
    >>> file = open(config.live)
    >>> lines = [l for l in file.readlines()]
    >>> file.close()
    >>> lines
    ['[versions]\n',
    'foo.bar = 1.1\n',
    '\n']

    >>> os.remove(config.live)

Check ``ReleaseCFG`` object::

    >>> from bda.recipe.deployment.common import ReleaseCFG
    >>> path = os.path.join(tempdir, '.releasecfg')
    >>> releaserc = ReleaseCFG(path)
    >>> releaserc.set('pypi', 'mustermann', 'secret')
    >>> releaserc.get('pypi')
    ('mustermann', 'secret')

    >>> releaserc()
    >>> file = open(path)
    >>> lines = [l for l in file.readlines()]
    >>> file.close()
    >>> lines
    ['[pypi]\n',
    'username = mustermann\n',
    'password = secret\n',
    '\n']

Test ``DeploymentPackage`` object::

    >>> from bda.recipe.deployment.common import DeploymentPackage
    >>> package = DeploymentPackage(config, 'foo.bar')

Environment checks::

    >>> config.env
    'dev'

    >>> config.config.set('settings', 'env', 'dev')

Check some base stuff of DeploymentPackage::

    >>> package.package_path
    '/.../sources/foo.bar'

    >>> package.version
    '1.1'

    >>> package.connector_name
    'svn'

    >>> package.dist_server
    'http://bda.org'

    >>> package.package_uri
    'https://svn.plone.org/svn/collective/foo.bar/trunk'

    >>> connector = package.connector
    >>> connector
    <bda.recipe.deployment.svn.SVNConnector object at ...>
    
Cleanup::

    >>> import shutil
    >>> shutil.rmtree(os.path.join(tempdir, 'sources'))
    