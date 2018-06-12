from flask import (
    Blueprint, request, render_template, flash, g, session, redirect, url_for
)


from . import db
from . import login_required
from .forms import LoginForm, RegisterForm
from .models import User
from .config import mod_name


bp = Blueprint(mod_name, __name__, url_prefix='/auth')


# registers a function to load user before view running
@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into `g.user`."""
    user_id = session.get('user_id', None)
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()


# login view
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # store the user id in a new session and return to the index
        session.clear()
        session['user_id'] = form._user.id
        flash('Welcome %s!' % form._user.username)
        return redirect(url_for('index'))
    return render_template("auth/login.html", form=form)


# logout view
@bp.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('index'))


# register view
@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        invitation = form._invitation
        invitation.user_id = user.id
        invitation.refer = form.refer.data
        invitation.assigned = True
        db.session.commit()
        flash('You have registered successfully!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)