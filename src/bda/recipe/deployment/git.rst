Test SVNConnector
=================

Preparations
------------

Create a local bare git repo with one file::

    >>> import os
    >>> GITPATH = os.path.join(tempdir, 'foo.bare-git')
    >>> GITINITPATH = os.path.join(tempdir, 'foo.init-git')
    >>> os.mkdir(GITPATH)
    >>> from mr.developer.git import  GitWorkingCopy
    >>> gwc = GitWorkingCopy({})
    
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
    
Prepare connector::

    >>> CFGPATH = os.path.join(tempdir, '.bda.recipe.deployment.cfg')
    >>> SOURCESDIR = os.path.join(tempdir, 'git_sources')

    >>> from bda.recipe.deployment.common import Config
    >>> config = Config(CFGPATH, sources_dir=SOURCESDIR)

    >>> from bda.recipe.deployment.common import DeploymentPackage   
    >>> config.config.set('sources', 'foo', 'git file://%s' % GITPATH)
    >>> package = DeploymentPackage(config, 'foo')
    >>> connector = package.connector

Clone Repo::

So lets see if we can clone this, aka checkout in the mr.developer world::

    >>> connector.git_wc().git_checkout()
    >>> DUMMYFILEPATH = os.path.join(connector.source()['path'], 'dummy.txt')
    >>> os.path.exists(DUMMYFILEPATH)
    True
        
    
Commit Tests
------------

::

    >>> connector.status
    'clean'

    >>> with open(DUMMYFILEPATH, 'a') as dummyfile:
    ...     dummyfile.write('another line\n')
    >>> connector.status
    'dirty'

    >>> connector.commit()    
    >>> connector.status
    'clean'

    >>> with open(DUMMYFILEPATH, 'a') as dummyfile:
    ...     dummyfile.write('another line for sinfle file commit\n')
    >>> connector.status
    'dirty'

    >>> connector.commit(resource='dummy.txt')    
    >>> connector.status
    'clean'


Create RC Branch Tests
----------------------

Check has RC branch::

    >>> [sorted(_.items()) for _ in connector._get_branches()]
    [[('alias', None), ('branch', 'master'), ('current', True), ('remote', None)], 
    [('alias', 'origin/HEAD'), ('branch', 'master'), ('current', False), ('remote', 'origin')]]

    >>> connector._has_rc_branch()
    False
    
    >>> connector._current_branch()
    'master'

    >>> connector._has_rc_branch(remote=True)
    False

Create both, remote and local::
    
    >>> connector.creatercbranch()
    True
    
    >>> connector._current_branch()
    'master'

    >>> connector._has_rc_branch()
    True

    >>> connector.status
    'clean'    

    >>> [sorted(_.items()) for _ in connector._get_branches()]
    [[('alias', None), ('branch', 'master'), ('current', True), ('remote', None)], 
    [('alias', None), ('branch', 'rc'), ('current', False), ('remote', None)], 
    [('alias', 'origin/HEAD'), ('branch', 'master'), ('current', False), ('remote', 'origin')], 
    [('alias', None), ('branch', 'rc'), ('current', False), ('remote', 'origin')]]

Subsquent call on existent branch::

    >>> connector.creatercbranch()
    False
    
Remove local branch and try fetching of remote::

    >>> stdout, stderr, cmd = connector._rungit(['checkout', 'master']) 
    >>> stdout, stderr, cmd = connector._rungit(['branch', '-d', 'rc']) 
    
    >>> connector._current_branch()
    'master'
    
    >>> connector._has_rc_branch()
    False

    >>> connector._has_rc_branch(remote=True)
    True

    >>> connector.creatercbranch()
    True

    >>> connector._current_branch()
    'master'

    >>> connector._has_rc_branch()
    True
        
    
Merge Tests
-----------

::    

    >>> stdout, stderr, cmd = connector._rungit(['checkout', 'master']) 
    >>> connector._current_branch()
    'master'

    >>> with open(DUMMYFILEPATH, 'a') as dummyfile:
    ...     dummyfile.write('again another line\n')
    >>> connector.status
    'dirty'    

    >>> connector.merge()   

    >>> connector._current_branch()
    'rc'

    >>> connector.status
    'clean'    

Tag Tests
---------

::    

    >>> connector._tags()
    []
    
    >>> connector._tag('vTest', 'test version')
    >>> connector._tags()
    ['vTest']
    
    >>> connector.package.version
    'unversioned'    

    >>> connector.tag()
    >>> sorted(connector._tags())
    ['unversioned', 'vTest']

    >>> connector.status
    'clean'    
    

Cleanup
-------

::    
    >>> import shutil
    >>> shutil.rmtree(SOURCESDIR, ignore_errors=True)    
    >>> shutil.rmtree(GITPATH, ignore_errors=True)    
