Test SVNConnector
=================

Prepare
-------

::
    >>> import os
    >>> FILEPATH = os.path.join(tempdir, '.bda.recipe.deployment.cfg')
    >>> SOURCESDIR = os.path.join(tempdir, 'git_sources')

    >>> from bda.recipe.deployment.common import Config
    >>> config = Config(FILEPATH, sources_dir=SOURCESDIR)

    >>> from bda.recipe.deployment.common import DeploymentPackage
    
    
Test
----

::    
    
    >>> resource = 'git https://github.com/collective/foo.bar.baz'
    >>> config.config.set('sources', 'foo.bar.baz', resource)

    >>> package = DeploymentPackage(config, 'foo.bar.baz')
    >>> connector = package.connector
    

Cleanup
-------

::    
    >>> import shutil
    >>> shutil.rmtree(SOURCESDIR, ignore_errors=True)    
