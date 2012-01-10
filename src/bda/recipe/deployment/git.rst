Test SVNConnector
=================

Preparations
------------

Create a local bare git repo with one file
::::::::::::::::::::::::::::::::::::::::::

::
    >>> import os
    >>> GITPATH = os.path.join(tempdir, 'foo.bare-git')
    >>> GITINITPATH = os.path.join(tempdir, 'foo.init-git')
    >>> os.mkdir(GITPATH)
    >>> from mr.developer.git import  gitWorkingCopyFactory
    >>> gwc = gitWorkingCopyFactory({})
    
    >>> cmd = gwc.run_git(['--bare', 'init', '-q', GITPATH])
    >>> stdout, stderr = cmd.communicate()
    >>> cmd.returncode
    0
    
    >>> os.mkdir(GITINITPATH)
    >>> cmd = gwc.run_git(['init'], cwd=GITINITPATH)
    >>> stdout, stderr = cmd.communicate()
    >>> cmd.returncode
    0
    
    >>> with open(os.path.join(GITINITPATH, 'dummy.txt'), 'w') as dummy:
    ...     dummy.write('some dummy data\n')    

    >>> cmd = gwc.run_git(['add', 'dummy.txt'], cwd=GITINITPATH)
    >>> stdout, stderr = cmd.communicate()
    >>> cmd.returncode
    0
    
    >>> cmd = gwc.run_git(['commit', '-q', '-a', '-m', 'init' ], 
    ...                   cwd=GITINITPATH)
    >>> stdout, stderr = cmd.communicate()
    >>> cmd.returncode
    0

    >>> cmd = gwc.run_git(['remote', 'add', 'origin', 'file://%s' % GITPATH], 
    ...                   cwd=GITINITPATH)
    >>> stdout, stderr = cmd.communicate()
    >>> cmd.returncode
    0
    
    >>> cmd = gwc.run_git(['push', 'origin', 'master'], cwd=GITINITPATH)
    >>> stdout, stderr = cmd.communicate()
    >>> cmd.returncode
    0
    
    >>> import shutil
    >>> shutil.rmtree(GITINITPATH)    
    
Prepare connector
:::::::::::::::::

::
    >>> CFGPATH = os.path.join(tempdir, '.bda.recipe.deployment.cfg')
    >>> SOURCESDIR = os.path.join(tempdir, 'git_sources')

    >>> from bda.recipe.deployment.common import Config
    >>> config = Config(CFGPATH, sources_dir=SOURCESDIR)

    >>> from bda.recipe.deployment.common import DeploymentPackage   
    >>> config.config.set('sources', 'foo', 'git file://%s' % GITPATH)
    >>> package = DeploymentPackage(config, 'foo')
    >>> connector = package.connector

Clone Repo
::::::::::

So lets see if we can clone this, ak a checkout in the mr.developer world::

    >>> connector.git_wc.git_checkout()
    >>> DUMMYFILEPATH = os.path.join(SOURCESDIR, 'foo', 'dummy.txt')
    >>> os.path.exists(DUMMYFILEPATH)
    True
        
    
Commit Tests
------------

::

    >>> with open(DUMMYFILEPATH, 'a') as dummyfile:
    ...     dummyfile.write('another line\n')
    >>> connector.commit()    



Create RC Branch Tests
----------------------

::

    TODO
    
Merge Tests
-----------

::    

    TODO
    

Tag Tests
---------

::    

    TODO
    

Cleanup
-------

::    
    >>> import shutil
    >>> shutil.rmtree(SOURCESDIR, ignore_errors=True)    
    >>> shutil.rmtree(GITPATH, ignore_errors=True)    
    