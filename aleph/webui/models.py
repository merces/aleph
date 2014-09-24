import hashlib, base64, hmac, random, urllib, datetime
from aleph.webui import app
from aleph.webui.database import db
from aleph.constants import ACCOUNT_REGULAR, ACCOUNT_PREMIUM, ACCOUNT_SUPERUSER, ACCOUNT_ENABLED

class Submission(db.Model):
    
    id = db.Column('id', db.Integer, primary_key=True)
    sample_uuid = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(), nullable=False)
    file_hash = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self):

        self.timestamp = datetime.datetime.utcnow()

class User(db.Model):

    id = db.Column('id', db.Integer, primary_key=True)

    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(255))

    login = db.Column('login', db.String(16), nullable=False, unique = True)
    email = db.Column(db.String(255), nullable=False, unique = True)
    password = db.Column(db.String(200), nullable=False)

    locale = db.Column(db.String(4), default = app.config.get('BABEL_DEFAULT_LOCALE'))
    timezone = db.Column(db.String(32), default = app.config.get('BABEL_DEFAULT_TIMEZONE'))

    account_type = db.Column(db.Integer, default = ACCOUNT_REGULAR)
    active = db.Column(db.Integer, default = ACCOUNT_ENABLED)

    token = db.Column(db.String(255), unique = True)
    api_key = db.Column(db.String(255), unique = True)

    submissions = db.relationship('Submission', backref='user', lazy='dynamic')

    def generate_token(self, hashalg=hashlib.sha256, bits=32):

        salt = str(random.getrandbits(bits))
        signature = hmac.new(app.config.get('SECRET_KEY'), msg=salt, digestmod=hashalg).digest()
        
        encodedSignature = base64.encodestring(signature).replace('\n', '').replace('=', '')
        
        return encodedSignature

    def __init__(self, login, email, password, active = ACCOUNT_ENABLED):
        self.login = login
        self.email = email
        self.password = password
        self.active = active

        if not self.active:
            self.token = self.generate_token()

        self.api_key = self.generate_token(hashalg=hashlib.sha512)

    def is_active(self):
        return (self.active == ACCOUNT_ENABLED)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def to_json(self):
        return dict(name=self.name, is_admin=self.is_admin)

    @property
    def is_premium(self):
        return (self.account_type == ACCOUNT_PREMIUM)

    @property
    def is_admin(self):
        return (self.account_type == ACCOUNT_SUPERUSER)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

class AnonymousUser(object):
    '''
    This is the default object for representing an anonymous user.
    '''
    def is_authenticated(self):
        return False

    def is_active(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return

