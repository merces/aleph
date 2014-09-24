#!/usr/bin/env python
import sys, os

# Fix path for importing modules
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.append(PACKAGE_DIR)

from aleph.webui.database import db
from aleph.webui.models import *
from aleph.webui.utils import hash_password
from aleph.constants import ACCOUNT_SUPERUSER

db.create_all()

# Let's create an admin user
u = User(login='admin', email='example@example.org', password=hash_password('admin', 'changeme12!'))
u.account_type = ACCOUNT_SUPERUSER
u.first_name = 'System'
u.last_name = 'Administrator'
db.session.add(u)
db.session.commit()
