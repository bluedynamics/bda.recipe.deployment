import sys
import logging

log = logging.getLogger()

log.setLevel(logging.DEBUG)

hdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)-5s %(message)s')

hdlr.setLevel(logging.INFO)
hdlr.setFormatter(formatter)
log.addHandler(hdlr)

import svn
import git

# pep 8
svn, git
