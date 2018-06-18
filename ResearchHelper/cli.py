import os
import shutil

import click
from flask import current_app, g
from flask.cli import with_appcontext, AppGroup

from .db import db
from .models import InvitationCode
from .utils import rlid_generator


current_dir = os.path.dirname(os.path.abspath(__file__))


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


mod_cli = AppGroup('mod')


def new_mod(dirname, mod_name):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    files = [{
        'name': '__init__.py',
        'lines': [
            'from ResearchHelper.db import db',
            'from ResearchHelper.db import TimestampModelMixin',
            'from ResearchHelper.helper import login_required',
            '# inherit forms via Flask-WTF FlaskForm base class',
            'from ResearchHelper.forms import BaseForm',
            '# create forms via WTForms.ext.sqlalchemy.model_form factory',
            'from ResearchHelper.forms import baseclass_form_factory',
            '# inherit forms via WTForms-Alchemy ModelForm(a subclass of FlaskForm)',
            'from ResearchHelper.forms import ModelForm',
            '# create forms via WTForms-Alchemy factory',
            'from ResearchHelper.forms import metaclass_form_factory',
            '',
            'from .controllers import bp',
            '',
            "__all__ = ['config', 'controllers', 'models']"
        ]
    }, {
        'name': 'config.py',
        'lines': [
            "mod_name='{}'".format(mod_name)
        ]
    }, {
        'name': 'controllers.py',
        'lines': [
            'from flask import Flask, Blueprint, request, render_template, \\',
            '    flash, g, session, redirect, url_for, abort',
            'from . import db',
            'from . import login_required',
            'from .config import mod_name',
            '',
            '',
            'bp = Blueprint(mod_name, __name__, url_prefix="/{}")'.format(mod_name),
            '',
            '',
            "@bp.route('/')",
            'def index():',
            '    return "{} index"'.format(mod_name)
        ]
    }, {
        'name': 'models.py',
        'lines': [
            'from . import db, TimestampModelMixin',
            'from .config import mod_name',
            '',
            '',
            '# class FooBar(db.Model, TimestampModelMixin):',
            '#     __tableprefix__ = mod_name',
            '#     id = db.Column(db.Integer, primary_key=True)',
            '#     name = db.Column(db.String, nullable=False, unique=True)',
            '',
            '#     @property',
            '#     def serialize(self):',
            '#         return {',
            '#             "id": self.id',
            '#             "name": self.name',
            '#         }',
            '',
            '#     @classmethod',
            '#     def form_meta_kwargs(cls):',
            '#         return {}',
            '',
            '#     def __repr__(self):',
            '#         return "<FooBar name=%r> % self.name"'
        ]
    }, {
        'name': 'forms.py',
        'lines': [
            'from wtforms.fields import StringField, TextAreaField, PasswordField, \\',
            '    SubmitField, FieldList, SelectField, RadioField, \\',
            '    SelectMultipleField, DateField, DateTimeField, FloatField, \\',
            '    DecimalField, BooleanField',
            '',
            'from wtforms.validators import DataRequired, InputRequired, Email,\\',
            '    EqualTo, NumberRange, Optional, Length, NumberRange, Regexp, \\',
            '    AnyOf, NoneOf, UUID, URL, ValidationError, StopValidation',
            '',
            'from . import BaseForm',
            '',
            '',
            '',
            '# class FooBarForm(BaseForm):',
            '#     name = StringField("Name Label", validators=[',
            '#         DataRequired(message="name is required.")',
            '#     ])'
        ]
    }]
    for file in files:
        with open(os.path.join(dirname, file['name']), 'w', encoding='utf8') as f:
            f.write('\n'.join(file['lines']))


@mod_cli.command('new')
@click.argument('mod_name')
@click.option('--dir', 
    default=current_dir, 
    help="mod's parent directory path")
def new_mod_command(mod_name, dir):
    dirname = os.path.join(dir, mod_name)
    msg = 'The mod [{}] exists, Do you want to override it?'.format(mod_name)
    if (os.path.isdir(dirname) 
        and (not click.confirm(msg))):
        click.echo('Bye!')
    else:
        new_mod(dirname, mod_name)
        click.echo('[{}] mod is created.'.format(mod_name))
        click.echo('Please register its blueprint in the app factory.')


def init_app(app):
    app.cli.add_command(db_cli)
    app.cli.add_command(generate_cli)
    app.cli.add_command(mod_cli)