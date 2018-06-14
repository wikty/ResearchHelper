def init_app(app):
    @app.route('/hello')
    def hello():
        return 'Hello, World!'