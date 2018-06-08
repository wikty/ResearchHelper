from datetime import datetime
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import db
from .models import User, InvitationCode

# - Blueprint
# A Blueprint is a way to organize a group of related views and other code. 
# Rather than registering views and other code directly with an application, 
# they are registered with a blueprint. Then the blueprint is registered with 
# the application when it is available in the factory function.
# - Endpoint
# The url_for() function generates the URL to a view based on a name and 
# arguments. The name associated with a view is also called the endpoint, and 
# by default it’s the same as the name of the view function. The arguments are 
# those defined by view function. For example, url_for('blog.update', id=p_id)

# with url prefix `/auth`
bp = Blueprint('auth', __name__, url_prefix='/auth')

# require authentication decorator
def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # redirect to auth blueprint's login()
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


# registers a function to load user before run the view function
@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        invitation = request.form['invitation']
        refer = request.form['refer']
        error = None

        if not invitation:
            error = 'Invitation Code is required.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            code = InvitationCode.query.filter_by(code=invitation).first()
            if code is None:
                error = 'Invitation Code is invalid.'
            elif code.assigned:
                error = 'Invitation Code is used.'

            if User.query.filter_by(username=username).first() is not None:
                error = 'User {0} is already registered.'.format(username)

        if error is None:
            # the name is available, store it in the database and go to
            # the login page
            user = User(username=username,
                        password=password)
            db.session.add(user)
            db.session.commit()
            code.user_id = user.id
            code.refer = refer
            code.assigned = True
            code.assigned_date = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('index'))
