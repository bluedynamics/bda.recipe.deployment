import os

BASE_DIR = os.path.abspath('')
if BASE_DIR.endswith('/bin'):
    BASE_DIR = BASE_DIR[:-4]

CFG_PATH = os.path.join(os.environ['HOME'], '.bda.recipe.deployment.auth')

CONFIG_PATH = os.path.join(BASE_DIR, '.bda.recipe.deployment.cfg')

waitress = dict()
