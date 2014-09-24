from flask import Blueprint, render_template, session, redirect, url_for, request, flash, g, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babel import gettext, get_locale, get_timezone

from aleph.webui import app, login_manager
from aleph.webui.utils import hash_password
from aleph.webui.email import send_email
from aleph.webui.database import db
from aleph.webui.models import User, AnonymousUser
from aleph.webui.forms import LoginForm, NewUserForm, UserForm, BasicUserForm, ChangePasswordForm
from aleph.constants import ACCOUNT_DISABLED, ACCOUNT_ENABLED

from sqlalchemy import and_


mod = Blueprint('users', __name__, url_prefix='/users')

@mod.route('/')
@mod.route('/index')
@mod.route('/index/<int:page>')
@login_required
def index(page = 1):

    if not current_user.is_admin:
        abort(401)

    users = User.query.paginate(1, app.config.get('ITEMS_PER_PAGE'))

    return render_template('users/index.html', users=users)

@mod.route('/enable/<int:user_id>')
@login_required
def enable(user_id):

    if not current_user.is_admin:
        abort(401)

    user = User.query.get(user_id)

    if not user:
        abort(404)

    user.active = ACCOUNT_ENABLED

    db.session.add(user)
    db.session.commit()
    flash(gettext('Account enabled'))
    return redirect(url_for('users.index'))

@mod.route('/disable/<int:user_id>')
@login_required
def disable(user_id):

    if not current_user.is_admin:
        abort(401)

    user = User.query.get(user_id)

    if not user:
        abort(404)

    user.active = ACCOUNT_DISABLED
    user.token = None

    db.session.add(user)
    db.session.commit()
    flash(gettext('Account disabled'))
    return redirect(url_for('users.index'))

@mod.route('/add', methods=['POST','GET'])
@login_required
def add():

    if not current_user.is_admin:
        abort(401)

    form = NewUserForm()

    if form.validate_on_submit():

        user = User(
            login=form.login.data,
            email=form.email.data,
            password = hash_password(form.login.data, form.password.data)
        )

        user.active = form.active.data
        user.account_type = form.account_type.data

        user.locale = form.locale.data
        user.timezone = form.timezone.data

        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        db.session.add(user)
        db.session.commit()

        flash(gettext(u'User added successfully'))

        return redirect(url_for('users.index'))
    else:
        form.timezone.data = str(get_timezone())
        form.locale.data = str(get_locale())

    return render_template('users/new.html', form=form)

@mod.route('/edit/<int:user_id>', methods=['POST','GET'])
@login_required
def edit(user_id):

    if not current_user.is_admin:
        abort(401)

    user = User.query.get(user_id)
    if not user:
        abort(404)

    form = UserForm()

    if form.validate_on_submit():
        user.email = form.email.data
        user.login = form.login.data

        user.active = form.active.data
        user.account_type = form.account_type.data

        user.locale = form.locale.data
        user.timezone = form.timezone.data

        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        user.token = form.token.data
        user.api_key = form.api_key.data

        db.session.add(user)
        db.session.commit()

        flash(gettext(u'User updated successfully'))
        return redirect(url_for('users.index'))

    if request.method == 'GET':
        form.login.data = user.login
        form.email.data = user.email
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.locale.data = user.locale
        form.timezone.data = user.timezone
        form.account_type.data = user.account_type
        form.active.data = user.active
        form.api_key.data = user.api_key
        form.token.data = user.token

    return render_template('users/edit.html', form=form, user=user)

@mod.route('/settings', methods=['POST','GET'])
@login_required
def settings():

    form = BasicUserForm()

    if form.validate_on_submit():
        current_user.email = form.email.data

        current_user.locale = form.locale.data
        current_user.timezone = form.timezone.data

        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data

        db.session.add(current_user)
        db.session.commit()

        flash(gettext(u'Settings updated successfully'))
        return redirect(url_for('general.index'))

    if request.method == 'GET':
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.locale.data = current_user.locale
        form.timezone.data = current_user.timezone

    return render_template('users/settings.html', form=form, user=current_user)

@mod.route('/change_password/<int:user_id>', methods=['POST','GET'])
@login_required
def changepw(user_id):
    
    if not current_user.is_admin and user_id != current_user.id:
        abort(401)

    user = User.query.get(user_id)

    if not user:
        abort(404)

    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_pw = hash_password(user.login, form.current_password.data)
        if current_pw != user.password:
            flash(gettext('Current password doesn\'t match'))
        else:
            user.password = hash_password(user.login, form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(gettext('Password changed successfully'))

            if current_user.is_admin:
                return redirect(url_for('users.index'))
            else:
                return redirect(url_for('general.index'))

    return render_template('users/change_password.html', form=form, user=user)

@mod.route('/register', methods=['POST','GET'])
def register():

    if not app.config.get('ALLOW_REGISTRATIONS'):
        abort(404)

    form = NewUserForm()

    if form.validate_on_submit():

        exists = User.query.filter(User.email == form.email.data).first()

        if exists:
            flash(gettext('Email address already registered'))
        else:
            user = User(
                login=form.login.data,
                email=form.email.data,
                password = hash_password(form.login.data, form.password.data),
                active = ACCOUNT_DISABLED
            )

            user.first_name = form.first_name.data
            user.last_name = form.last_name.data

            user.locale = str(get_locale())
            user.timezone = str(get_timezone())

            db.session.add(user)
            db.session.commit()

            # Send email
            send_email(
                gettext('Welcome to %(appname)s', appname = app.config.get('APP_TITLE')),
                app.config.get('MAIL_SENDER'),
                [form.email.data],
                render_template('users/mail_register.txt', user=user),
                render_template('users/mail_register.html', user=user),
                )

            flash(gettext('Account created successfully. Please check your email for instructions on activating your account'))
            return redirect(url_for('users.login'))

    return render_template('users/register.html', form=form, hide_sidebar=True, hide_header=True, class_body='bg-black', class_html ='bg-black')

@mod.route('/activate/<token>')
def activate(token):

    if not app.config.get('ALLOW_REGISTRATIONS'):
        abort(404)

    user = User.query.filter(and_(User.active == ACCOUNT_DISABLED, User.token == token)).first()

    if not user:
        abort(404)

    user.active = ACCOUNT_ENABLED
    user.token = None

    db.session.add(user)
    db.session.commit()

    flash(gettext('Account activated. Please login below'))
    return redirect(url_for('users.login'))

@mod.route('/login', methods=['POST', 'GET'])
def login():

    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('general.index'))

    form = LoginForm()

    if form.validate_on_submit():

        # Validate User
        user = User.query.filter(User.login == form.username.data).first()
        if not user:
            flash(gettext('Invalid credentials'), 'danger')
        else:
            password = hash_password(form.username.data, form.password.data)

            if user.password != password:
                flash(gettext('Invalid credentials'), 'danger')
            else:
                if login_user(user):
                    flash(gettext('You have been successfully signed in'), 'success')
                    session['remember_me'] = form.remember_me.data

                    return redirect(url_for('general.index'))
                else:
                    flash(gettext('Cannot sign in'),'danger')


    return render_template('users/login.html', form=form, hide_sidebar=True, hide_header=True, class_body='bg-black', class_html = 'bg-black')

@login_required
@mod.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('general.index'))

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.before_request
def load_logged_user():
    if not session.get('user_id'):
        g.user = AnonymousUser()
    else:
        g.user = load_user(session['user_id'])

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('users.login'))
