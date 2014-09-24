from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, SelectField, PasswordField, FileField
from wtforms.validators import Required, Length, Email, EqualTo, Regexp, NumberRange, Optional
from flask.ext.babel import gettext
from flask import g
from aleph.constants import LANGUAGES, ACCOUNT_REGULAR, ACCOUNT_PREMIUM, ACCOUNT_SUPERUSER
from pytz import common_timezones

class LoginForm(Form):
    username = TextField(gettext('Username'), validators = [Required()])
    password = TextField(gettext('Password'), validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class BasicUserForm(Form):
    first_name = TextField(gettext('First Name'), validators = [Length(min=2, max=30, message=gettext('First name must be between 2 and 30 characters long'))])
    last_name = TextField(gettext('Last Name'), validators = [Length(min=2, max=255, message=gettext('Last name must be between 2 and 255 characters long'))])

    email = TextField(gettext('Email'), validators = [Required(), Email()])

    langs = []
    for langcode, langname in LANGUAGES.iteritems():
        langs.append((langcode, langname))

    timezones = []
    for timezone in common_timezones:
        timezones.append((timezone, timezone))

    locale = SelectField(gettext('Language'), choices=langs, validators = [Optional()])
    timezone = SelectField(gettext('Timezone'), choices=timezones, default='UTC', validators = [Optional()])

    active = BooleanField(gettext('Account enabled'), default=True, validators = []) 

    acc_types = [
        (ACCOUNT_REGULAR, gettext('Regular account')),
        (ACCOUNT_PREMIUM, gettext('Premium account')),
        (ACCOUNT_SUPERUSER, gettext('Superuser account')),
    ]

    account_type = SelectField(gettext('Account Type'), coerce=int, default=ACCOUNT_REGULAR, choices=acc_types, validators = [])

    token = TextField(gettext('Token'), [])
    api_key = TextField(gettext('API Key'), [])


class UserForm(BasicUserForm):
    login = TextField(gettext('Username'), validators = [Required(), Regexp(regex='^\w+$', message=gettext('Only alphanumeric characters valid'))])

class NewUserForm(UserForm):

    password = PasswordField(gettext('Password'), validators = [
        Required(),
        EqualTo('confirm', message=gettext('Passwords must match')) 
    ])
    confirm = PasswordField(gettext('Confirm password'), validators = [Required()])

class ChangePasswordForm(Form):
    current_password = PasswordField(gettext('Current password'), validators = [Required()])
    password = PasswordField(gettext('Password'), validators = [
        Required(),
        EqualTo('confirm', message=gettext('Passwords must match')) 
    ])
    confirm = PasswordField(gettext('Confirm password'), validators = [Required()])

class SubmitSampleForm(Form):

    sample = FileField('Sample', validators=[Required()])
