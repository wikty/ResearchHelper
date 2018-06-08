import click
from flask import current_app, g
from flask.cli import with_appcontext

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# @click.command('create-db')
# @with_appcontext
# def create_db_command():
#     """Create tables if not exist."""
#     db.create_all(app=current_app)
#     click.echo('Created the database.')

# @click.command('drop-db')
# @with_appcontext
# def drop_db_command():
#     """Drop tables if exist."""
#     db.drop_all(app=current_app)
#     click.echo('Droped the database.')

# @click.command('renew-db')
# @with_appcontext
# def renew_db_command():
#     """Clear the existing data and create new tables."""
#     db.drop_all(app=current_app)
#     db.create_all(app=current_app)
#     click.echo('Renewed the database.')

def init_app(app):
    """Register functions/commands into application instance."""
    db.init_app(app)
    # app.cli.add_command(create_db_command)
    # app.cli.add_command(drop_db_command)
    # app.cli.add_command(renew_db_command)