import json

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


from .utils import (
    camel_to_snake_case, comma_separated_string_join, 
    comma_separated_string_split
)


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


class JSONTypeException(Exception):
    pass


class JSONType(sa.types.TypeDecorator):
    impl = sa.types.String

    ensure_ascii = False

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, ensure_ascii=self.ensure_ascii)

    def process_result_value(self, value, dialect):
        if isinstance(value, str):
            return json.loads(value)


class CommaSeparatedStringException(Exception):
    pass


class CommaSeparatedString(sa.types.TypeDecorator):
    impl = sa.types.String

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, (list, tuple, set)):
            raise CommaSeparatedStringException('Only list/tuple/set is allowed.')
        return comma_separated_string_join(value)

    def process_result_value(self, value, dialect):
        if isinstance(value, str):
            return comma_separated_string_split(value)


def init_app(app):
    """Register functions/commands into application instance."""
    db.init_app(app)
    # add custome column types
    db.JSONType = JSONType
    db.CommaSeparatedString = CommaSeparatedString