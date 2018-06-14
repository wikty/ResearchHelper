from flask import session, g, current_app, request
from flask_wtf import csrf

from .models import User


def init_app(app):
    """Register functions are executed before each request to app."""
    # you can disable csrf default by `WTF_CSRF_CHECK_DEFAULT=False`
    # and then selectively call protect() only when you need. 
    # @app.before_request
    # def check_csrf():
    #     if not is_oauth(request):
    #         csrf.protect()

    # load user into g.user
    @app.before_request
    def load_logged_in_user():
        """If a user id is stored in the session, load the user object from
        the database into `g.user`."""
        user_id = session.get('user_id', None)
        if user_id is None:
            g.user = None
        else:
            g.user = User.query.filter_by(id=user_id).first()