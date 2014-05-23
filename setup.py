from setuptools import setup, find_packages
import os
version = '2.0b7'

shortdesc = "python deployment process based on buildout and mr.developer"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(
    name="bda.recipe.deployment",
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    keywords="",
    author="BlueDynamics Alliance",
    author_email="dev@bluedynamics.com",
    url="http://pypi.python.org/pypi/bda.recipe.deployment",
    license="GPLv2",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["bda", "bda.recipe"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.configuration',
        'mr.developer>1.19',
    ],
    extras_require=dict(
        test=[
            'interlude',
            'zope.testing',
        ]
    ),
    entry_points="""
        [zc.buildout]
        default = bda.recipe.deployment.recipe:Recipe

        [distutils.commands]
        deploymentregister = bda.recipe.deployment.command:register
        deploymentupload = bda.recipe.deployment.command:upload

        [console_scripts]
        deploy = bda.recipe.deployment.main:deploy
        bda_deployment_helper = bda.recipe.deployment.main:deploy_single
    """,
    )
