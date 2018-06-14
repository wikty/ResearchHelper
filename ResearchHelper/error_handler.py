from flask import render_template, abort
from flask_wtf.csrf import CSRFError


def init_app(app):
    # HTTP response code
    # abort() will raise a special exception that returns an HTTP status code. 
    # It takes an optional message to show with the error, otherwise a default 
    # message is used. 
    # 404 means "Not Found"
    # 403 means "Forbidden"
    # 401 means "Unauthorized", you can redirect to the login page instead of 
    # returning this status.
    
    # Not Found
    @app.errorhandler(404)
    def handle_not_found(error):
        return render_template('404.html'), 404
    
    # Server Internal Error
    @app.errorhandler(500)
    def handle_internal_error(error):
        return render_template('500.html'), 500

    # CSRF validation fails(default is 400 code)
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return render_template('400.html', reason=error.description), 400