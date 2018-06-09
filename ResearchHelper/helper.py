import functools

from flask import (
    flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


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