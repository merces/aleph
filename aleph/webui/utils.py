import os
from aleph.webui import app
from hashlib import sha256, sha512
from pygeoip import GeoIP

def hash_password(username, password):

    salt = sha512(app.secret_key+username).hexdigest()
    return sha256(password+salt).hexdigest()
    
def geoip():

    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../', 'webui/resources/GeoLiteCity.dat')
    return GeoIP(db_path)
