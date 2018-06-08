import os

from flask import Flask


def create_app(test_config=None):
    '''Application Factory: configure, register, setup and create
    flask application instance.
    :param test_config application configuration for test mode
    '''
    # Create app instance
    # arg: `__name__`
    # The app needs to know where it’s located to set up some
    # paths, and __name__ is a convenient way to tell it that.
    # arg: `instance_relative_config=True`
    # Configuration files are relative to the instance folder.
    # Instance folder is located outside the current package and can hold 
    # local data that shouldn’t be committed to version control, such as 
    # configuration secrets and the database file. You can get the folder
    # path via `app.instance_path`.
    app = Flask(__name__, instance_relative_config=True)
    # Sets some default configuration for app, i.e., development mode
    # arg: `SECRET_KEY='dev'`
    # SECRET_KEY is used by Flask and extensions to keep data safe. It’s set
    # to 'dev' to provide a convenient value during development, but it should
    # be overridden with a random value when deploying.
    # arg: `SQLALCHEMY_DATABASE_URI`
    # http://flask-sqlalchemy.pocoo.org/2.3/config/#connection-uri-format
    # arg: `SQLALCHEMY_ECHO`
    # echo the sql statements into stderr
    # arg: `SQLALCHEMY_BINDS`
    # configure multiple database engines/binds. The `SQLALCHEMY_DATABASE_URI`
    # is default database. Other database bings are specified in here.
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///{}'.format(
            os.path.join(app.instance_path, 'db.sqlite3')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
        SQLALCHEMY_BINDS={
            'users': 'sqlite:///{}'.format(
                os.path.join(app.instance_path, 'users.sqlite3')),
            'appmeta': 'sqlite:///{}'.format(
                os.path.join(app.instance_path, 'appmeta.sqlite3')),
        }
    )
    # Overrides the default configuration, i.e., production mode
    if test_config is None:
        # Load the config file in the instance folder if it exists. For 
        # example, when deploying, this can be used to set a real `SECRET_KEY`.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # register db
    from . import db
    db.init_app(app)
    # register cli
    from . import cli
    cli.init_app(app)
    # register auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)
    # register blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    # register taxonomy
    from . import taxonomy
    app.register_blueprint(taxonomy.bp)

    return app