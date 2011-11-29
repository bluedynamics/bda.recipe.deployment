from setuptools import setup, find_packages
import os

version = "1.0"
shortdesc =""
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name="bda.recipe.deployment",
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          "",
      ],
      keywords="",
      author="",
      author_email="",
      url="",
      license="",
      packages=find_packages("src"),
      package_dir={"": "src"},
      namespace_packages=["bda", "bda.recipe"],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          ##code-section dependencies
          'zope.component',
          'mr.developer',
          ##/code-section dependencies
      ],
      extras_require = dict(
          ##code-section extras_require
          test=[
            'interlude',
            'zope.testing',
          ]
          ##/code-section extras_require
      ),
      entry_points="""
      ##code-section entry_points

      [zc.buildout]
      default = bda.recipe.deployment.recipe:Recipe

      [distutils.commands]
      deploymentregister = bda.recipe.deployment.command:register
      deploymentupload = bda.recipe.deployment.command:upload

      [console_scripts]
      repopasswd = bda.recipe.deployment.main:repopasswd
      version = bda.recipe.deployment.main:version
      merge = bda.recipe.deployment.main:merge
      commit = bda.recipe.deployment.main:commit
      creatercbranch = bda.recipe.deployment.main:creatercbranch
      tag = bda.recipe.deployment.main:tag
      release = bda.recipe.deployment.main:release
      exportliveversion = bda.recipe.deployment.main:exportliveversion
      exportrcsource = bda.recipe.deployment.main:exportrcsource
      deploycandidate = bda.recipe.deployment.main:deploycandidate
      deployrelease = bda.recipe.deployment.main:deployrelease
      showversion = bda.recipe.deployment.main:showversion
      showall = bda.recipe.deployment.main:showall

      ##/code-section entry_points
      """,
      ##code-section additionals
      ##/code-section additionals
      )
