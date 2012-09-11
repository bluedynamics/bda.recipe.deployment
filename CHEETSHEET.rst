================================
bda.recipe.deployment cheatsheet
================================

OUTDATED (this was valid for version 1.x)

Deploy candidate
================

1 Update your repository and then commit all changes.
 
2 Choose a new version. Show version with ./bin/version packagename
 
3 DEPLOY: ./bin/deploycandidate PACKAGENAME NEWVERSION
 
4 Tell the manager of the the RC when youre done
 
5 Lean back and write the invoice
 
Manage the Release Candidate
============================
 
All this need to be done in your RC instance!
 
1 Get informed by the developer about changes done.

2 NEW? If there wasn't any candidate before for the package, do an svn up

3 MERGE the package as a whole into the RC: ./bin/merge PACKAGENAME

OR

MERGE PARTIAL, only some files into the RC. Always include setup.py to have the 
version increase::

    ./bin/merge PACKAGENAME setup.py 
    ./bin/merge PACKAGENAME src/PART/SUBPART/FILENAME

4 TEST!!! Let buildout run with ./bin/buildout -c rc.cfg, start zope, copy live 
  database into rc. Do upgrade steps or whatever is needed.

5 CHECK if there isnt any empty directory in your package. Empty directories are 
  not added by default to the release tarball!

6 RELEASE - if everything is ok: ./bin/deployrelease PACKAGENAME

Manage the Live Instance
========================

All this need to be done in your LIVE instance!
You may need to do this for every instance if your running a cluster!

1 UPDATE svn up your live instance

2 BUILDOUT run buildout: ./bin/buildout -c live.cfg

3 RESTART restart your cluster, upgrade - you may have here a special process 
  too.
