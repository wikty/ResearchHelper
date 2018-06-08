import click
from flask import current_app, g
from flask.cli import with_appcontext

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_app(app):
    """Register functions/commands into application instance."""
    db.init_app(app)