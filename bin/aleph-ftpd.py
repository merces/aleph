#!/usr/bin/env python

import os, sys
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Fix path for importing modules
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.append(PACKAGE_DIR)

from aleph.webui.models import User
from aleph.webui.utils import hash_password
from aleph.settings import SAMPLE_SUBMIT_FOLDER, FTP_ENABLE, FTP_PORT



# Overriding validate_authentication() to support to Aleph's auth method
class DummyHashAuthorizer(DummyAuthorizer):

    def validate_authentication(self, username, password, handler):
        hash = hash_password(username, password)
        return self.user_table[username]['pwd'] == hash

if __name__ == "__main__":

    if not FTP_ENABLE:
        print 'Integrated FTP Server is disabled by configuration.'
        sys.exit(1)

    authorizer = DummyHashAuthorizer()

    # Add active premium users to the FTP Server
    for user in User.query.filter(User.active, User.account_type < 2):
        authorizer.add_user(user.login, user.password, SAMPLE_SUBMIT_FOLDER, perm='elamw')

    handler = FTPHandler
    #handler.banner = "pyftpdlib based ftpd ready."
    handler.authorizer = authorizer
    address = ('', FTP_PORT)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()