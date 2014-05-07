# -*- coding: utf-8 -*-
import zc.buildout
import os
from bda.recipe.deployment.common import Config


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.buildout = buildout
        self.buildout_base = buildout['buildout']['directory']
        distserver = options.get('distserver')
        if not distserver:
            raise zc.buildout.UserError(u'distserver section missing.')
        distserver = [d.strip() for d in distserver.strip().split('\n')]
        if not distserver:
            raise zc.buildout.UserError(u'No dist servers defined.')
        self.distserver = dict()
        for server in distserver:
            key, val = server.split(' ')
            self.distserver[key] = val
        packages = options.get('packages')
        if not packages:
            raise zc.buildout.UserError(u'packages section missing.')
        packages = [p.strip() for p in packages.strip().split('\n')]
        if not packages:
            raise zc.buildout.UserError(u'No packages defined.')
        self.packages = dict()
        for package in packages:
            key, val = package.split(None, 1)
            self.packages[key] = val
        base_path = buildout['buildout']['directory']

        self.dev_sources = options.get('dev_sources')
        if not self.dev_sources:
            raise zc.buildout.UserError(u'No DEV sources config defined.')
        if not self.dev_sources.startswith(base_path):
            self.dev = os.path.join(base_path, self.dev_sources)

        self.rc_sources = options.get('rc_sources')
        if not self.rc_sources:
            raise zc.buildout.UserError(u'No RC sources config defined.')
        if not self.rc_sources.startswith(base_path):
            self.rc_sources = os.path.join(base_path, self.rc_sources)

        self.rc_branch_name = options.get('rc_branch_name', 'rc')
        self.rc_versions = options.get('rc_versions')
        if not self.rc_versions:
            raise zc.buildout.UserError(u'No RC versions config defined.')
        if not self.rc_versions.startswith(base_path):
            self.rc_versions = os.path.join(base_path, self.rc_versions)

        self.live_versions = options.get('live_versions')
        if not self.live_versions:
            raise zc.buildout.UserError(u'No Live versions config defined.')
        if not self.live_versions.startswith(base_path):
            self.live_versions = os.path.join(base_path, self.live_versions)

        self.register = options.get('register', '')
        self.env = options.get('env')
        if not self.env in ['dev', 'rc', 'all']:
            raise zc.buildout.UserError(u'No or wrong env flavor defined.')
        sources_default = os.path.join(self.buildout['buildout']['directory'],
                                       'src')
        self.sources_dir = self.buildout['buildout'].get('sources-dir',
                                                         sources_default)

    def install(self):
        path = os.path.join(self.buildout['buildout']['directory'],
                            '.bda.recipe.deployment.cfg')
        if os.path.exists(path):
            os.remove(path)
        dev_sources = Config(self.dev_sources)
        sources = dev_sources.as_dict('sources')
        Config(path, self.buildout_base, self.distserver, self.packages,
               sources, self.rc_sources, self.rc_versions, self.live_versions,
               self.env, self.sources_dir, self.register, self.rc_branch_name)()

    def update(self):
        return self.install()
