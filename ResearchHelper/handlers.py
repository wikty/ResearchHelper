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

    # CSRF validation fails(default is 400 code)
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return render_template('400.html', reason=error.description), 400

    # 403 Forbidden
    # If you have some kind of access control on your website, you will have 
    # to send a 403 code for disallowed resources. 
    @app.errorhandler(403)
    def handle_forbidden(error):
        return render_template('403.html'), 403
    
    # 404 Not Found
    # It’s a very good idea to make sure there is actually something useful on
    # a 404 page, at least a link back to the index.
    @app.errorhandler(404)
    def handle_not_found(error):
        return render_template('404.html'), 404

    # 410 Gone
    # Resources that previously existed and got deleted answer with 410 instead
    # of 404. If you are not deleting documents permanently from the database but
    # just mark them as deleted, do the user a favour and use the 410 code instead
    # and display a message that what they were looking for was deleted for all 
    # eternity.
    # @app.errorhandler(410)
    # def handle_gone(error):
    #     pass
    
    # 500 Internal Server Error
    # Usually happens on programming errors or if the server is overloaded. 
    # A terribly good idea is to have a nice page there, because your application
    # will fail sooner or later.
    # Note: If you set a 500 error handler, Flask will not trigger it if it's 
    # running in Debug mode.
    @app.errorhandler(500)
    def handle_internal_error(error):
        return render_template('500.html'), 500