#!/usr/bin/env python

import sys, os

# Fix path for importing modules
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.append(PACKAGE_DIR)

from aleph import AlephServer

if __name__ == "__main__":

    app = AlephServer()
    app.run()
