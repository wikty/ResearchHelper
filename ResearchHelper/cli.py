import click
from flask import current_app, g
from flask.cli import with_appcontext, AppGroup

from .db import db
from .models import InvitationCode
from .utils import rlid_generator

db_cli = AppGroup('db')


def create_db(bind):
    if bind == 'all':
        db.create_all(app=current_app)
    else:
        db.create_all(app=current_app, bind=bind)

def drop_db(bind):
    if bind == 'all':
        db.drop_all(app=current_app)
    else:
        db.drop_all(app=current_app, bind=bind)

def renew_db(bind):
    if bind == 'all':
        db.drop_all(app=current_app)
        db.create_all(app=current_app)
    else:
        db.drop_all(app=current_app, bind=bind)
        db.create_all(app=current_app, bind=bind)


@db_cli.command('create')
@click.option('--bind', default=None, help='The database bind key')
@with_appcontext
def create_db_command(bind):
    """Create tables if not exist.
    if bind is None, specify the default bind
    if bind is all, specify all of binds
    """
    create_db(bind)
    click.echo('Created the database.')


@db_cli.command('drop')
@click.option('--bind', default=None, help='The database bind key')
@with_appcontext
def drop_db_command(bind=None):
    """Drop tables if exist.
    if bind is None, specify the default bind
    if bind is all, specify all of binds
    """
    drop_db(bind)
    click.echo('Droped the database.')


@db_cli.command('renew')
@click.option('--bind', default=None, help='The database bind key')
@with_appcontext
def renew_db_command(bind=None):
    """Clear the existing data and create new tables.
    if bind is None, specify the default bind
    if bind is all, specify all of binds
    """
    renew_db(bind)
    click.echo('Renewed the database.')


generate_cli = AppGroup('invitation')


def generate_invitation(count, length=32):
    for i in range(count):
        uid = rlid_generator(length)
        while True:
            code = InvitationCode.query.filter_by(code=uid).first()
            if code is None:
                break
            uid = rlid_generator(length)
        code = InvitationCode(code=uid)
        db.session.add(code)
        db.session.commit()

def get_invitation(count):
    codes = InvitationCode.query.filter_by(assigned=False).limit(count).all()
    return [code.code for code in codes]


@generate_cli.command('generate')
@click.option('--count', default=100, help='The number of invitation code')
@click.option('--length', default=32, help='The length of invitation code')
@with_appcontext
def generate_invitation_command(count, length):
    generate_invitation(count, length)
    click.echo('{}[{}] invitation codes are generated.'.format(count, length))


@generate_cli.command('get')
@click.option('--count', default=1, help='The number of invitation code')
@with_appcontext
def get_invitation_command(count):
    codes = get_invitation(count)
    for code in codes:
        click.echo(code)    

    if len(codes) < count:
        click.echo('{} cannot be allocated.'.format(count-len(codes)))    


def init_app(app):
    app.cli.add_command(db_cli)
    app.cli.add_command(generate_cli)