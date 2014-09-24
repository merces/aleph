from flask import Flask, render_template, request
from flask.ext.login import LoginManager, current_user
from flask.ext.babel import Babel, format_datetime, lazy_gettext
from flask.ext.mail import Mail

import os

app = Flask('aleph-webui')

from aleph import settings, constants
# Load configuration from file
app.config.from_object(constants)
app.config.from_object(settings)

# Register i18n
babel = Babel(app)

# Register mail handler
mail = Mail(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = lazy_gettext('Please log in to access this page.')

# Import App Modules
from aleph.webui.views import *
from aleph.webui.database import db

# Register blueprints
app.register_blueprint(general.mod)
app.register_blueprint(users.mod)
app.register_blueprint(samples.mod)


@app.teardown_request
def remove_db(exception):
    db.session.remove()

@app.errorhandler(401)
def not_authorized(error):
    return render_template('401.html', hide_sidebar=True, hide_header=True, class_body='bg-black', class_html ='bg-black')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', hide_sidebar=True, hide_header=True, class_body='bg-black', class_html ='bg-black')
