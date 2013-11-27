from setuptools.command.upload import upload as st_upload
from setuptools.command.register import register as st_register
from bda.recipe.deployment import env


class upload(st_upload):

    def finalize_options(self):
        """Set repository, username and password for uploading by
        bda.recipe.deployment.env.waitress
        """
        self.repository = env.waitress['repository']
        self.username = env.waitress['username']
        self.password = env.waitress['password']
        st_upload.finalize_options(self)


class register(st_register):

    def finalize_options(self):
        """Set repository, username and password for register by
        bda.recipe.deployment.env.waitress
        """
        self.repository = env.waitress['repository']
        self.username = env.waitress['username']
        self.password = env.waitress['password']
        st_register.finalize_options(self)
