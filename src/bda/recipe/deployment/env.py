import os

BASE_DIR = os.path.abspath('')
if BASE_DIR.endswith('/bin'):
    BASE_DIR = BASE_DIR[:-4]

RC_PATH = os.path.join(os.environ['HOME'], '.bda.recipe.deployment.rc')

CONFIG_PATH = os.path.join(BASE_DIR, '.bda.recipe.deployment.cfg')

waitress = dict()