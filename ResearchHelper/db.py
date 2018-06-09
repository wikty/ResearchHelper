import re

import sqlalchemy as sa
from sqlalchemy.ext.declarative import DeclarativeMeta, declared_attr, \
    has_inherited_table, declarative_base
from sqlalchemy.schema import _get_table_key

import click
from flask import current_app, g
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from flask_sqlalchemy.model import Model, DefaultMeta, NameMetaMixin, \
    BindMetaMixin, DeclarativeMeta, should_set_tablename


# Improve the Flask-SQLAlchemy automatcially generate table name mechanism.
camelcase_re = re.compile(r'([A-Z]+)(?=([a-z0-9]|$))')


def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1 and match.end() < len(name):
            return ('_%s_%s' % (word[:-1], word[-1])).lower()

        return '_' + word.lower()

    return camelcase_re.sub(_join, name).lstrip('_')

# Override table automatically generate class
class NameWithPrefixMetaMixin(NameMetaMixin):
    """Add a prefix for automatically generated table name. The prefix is specified by
    `Model.__tableprefix__`.
    """
    def __init__(cls, name, bases, d):
        if should_set_tablename(cls):
            tablename = camel_to_snake_case(cls.__name__)
            if '__tableprefix__' not in cls.__dict__:
                cls.__tablename__ = tablename
            else:
                # add table prefix
                cls.__tablename__ = '_'.join([cls.__tableprefix__, tablename])

        super().__init__(name, bases, d)


class BaseMeta(NameWithPrefixMetaMixin, BindMetaMixin, DeclarativeMeta):
    """Override the DefaultMeta class via NameWithPrefixMetaMixin"""
    pass


# Extend Model `query` property's class.
class Query(BaseQuery):
    # add methods for Model.query in here
    def get_or(self, id, default=None):
        return self.get(id) or default


db = SQLAlchemy(
    model_class=declarative_base(cls=Model, metaclass=BaseMeta, name='Model'),
    query_class=Query
)


class TimestampModelMixin(object):
    """Mixin this class to add created and updated timestamp for models."""

    created = db.Column(db.DateTime, 
        default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, 
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())


def init_app(app):
    """Register functions/commands into application instance."""
    db.init_app(app)