Test SVNConnector
=================

Imports and config.
::

    >>> import os
    >>> path = os.path.join(tempdir, '.bda.recipe.deployment.cfg')
    
    >>> from bda.recipe.deployment.common import Config
    >>> config = Config(path)
    
    >>> from bda.recipe.deployment.common import DeploymentPackage
    
Try on invalid package repository.
::

    >>> resource = 'svn https://svn.plone.org/foo.bar/tags/1.1'
    >>> config.config.set('sources', 'foo.bar', resource)  
    
    >>> package = DeploymentPackage(config, 'foo.bar')
    >>> connector = package.connector
    Traceback (most recent call last):
      ...
    DeploymentError: Invalid repository structure. Could only handle packages contained either in 'svn_url/trunk' or in 'svn_url/branches/NAME'

    
Try on trunk package repository.
::

    >>> resource = 'svn https://svn.plone.org/foo.bar/trunk'
    >>> config.config.set('sources', 'foo.bar', resource)
    
    >>> package = DeploymentPackage(config, 'foo.bar')
    >>> connector = package.connector
    >>> connector
    <bda.recipe.deployment.svn.SVNConnector object at ...>
    
    >>> connector._svn_base_path
    'https://svn.plone.org/foo.bar'
        
    >>> connector.rc_source
    'svn https://svn.plone.org/foo.bar/branches/rc'

Try on branches/NAME package repository.
::

    >>> resource = 'svn https://svn.plone.org/foo.bar/branches/1'
    >>> config.config.set('sources', 'foo.bar', resource)
    
    >>> package = DeploymentPackage(config, 'foo.bar')
    >>> connector = package.connector
    >>> connector
    <bda.recipe.deployment.svn.SVNConnector object at ...>
    
    >>> connector._svn_base_path
    'https://svn.plone.org/foo.bar'
        
    >>> connector.rc_source
    'svn https://svn.plone.org/foo.bar/branches/rc-1'

Check refering URI's.
::
    
    >>> connector._rc_uri
    'https://svn.plone.org/foo.bar/branches/rc-1'
    
    >>> connector._tag_uri
    'https://svn.plone.org/foo.bar/tags/1.1'