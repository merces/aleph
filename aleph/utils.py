import os, sys, logging
from functools import partial

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
# Get path as a function - for PluginBase
get_path = partial(os.path.join, CURRENT_DIR)

def error(msg):
    # print help information and exit:
    logging.error(msg)
    sys.stderr.write(str(msg+"\n"))
    sys.exit(2)
