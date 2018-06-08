from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Base(db.Model):

    __abstract__  = True

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, 
        default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, 
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())


class User(Base):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    status = db.Column(db.SmallInteger, nullable=False, default=0)

    def __init__(self, **kwargs):
        """Create user and encrypt password."""
        super(User, self).__init__(**kwargs)
        self.password = self._encrypt_password(self.password)

    def _encrypt_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        """Check user password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.username


class InvitationCode(Base):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=-1)
    code = db.Column(db.String(6), nullable=False, unique=True)
    refer = db.Column(db.Text, nullable=False, default='')
    assigned = db.Column(db.Boolean, nullable=False, default=False)
