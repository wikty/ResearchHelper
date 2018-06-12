from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property

from . import db, TimestampModelMixin
from .config import mod_name, admin_role


class User(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    # change password behavior
    _password = db.Column("password", db.Text, nullable=False,
        info={'label': 'password'})
    role = db.Column(db.SmallInteger, nullable=False, default=0)
    status = db.Column(db.SmallInteger, nullable=False, default=0)

    def __init__(self, **kwargs):
        """Create user and encrypt password."""
        super(User, self).__init__(**kwargs)

    @classmethod
    def form_meta_kwargs(cls):
        return {
            'include': ('password', ),
            'exclude': ('_password', )
        }

    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, password):
        self._password = self._encrypt_password(password)

    def _encrypt_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        """Check user password."""
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.role == admin_role

    def __repr__(self):
        return '<User %r>' % self.username


class InvitationCode(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=-1)
    code = db.Column(db.String(32), nullable=False, unique=True)
    refer = db.Column(db.Text, nullable=False, default='')
    assigned = db.Column(db.Boolean, nullable=False, default=False)
