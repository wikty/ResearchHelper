from . import db
from . import TimestampModelMixin
from . import CommaSeparatedStr
from . import User
from .config import mod_name



class File(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), nullable=True, unique=True)
    fingerprint = db.Column(db.String, nullable=True, unique=True)
    url = db.Column(db.String, nullable=True)
    dirname = db.Column(db.String, nullable=True)
    filename = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<File uuid=%r>' % self.uuid

    @property
    def serialize(self):
        return {
            'uuid': self.uuid,
            'created': self.created,
            'modified': self.modified
        }


class FileMetadata(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey(File.id),
        nullable=False, primary_key=True)
    title = db.Column(db.String, nullable=True)
    abstract = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date)
    toc = db.Column(db.Text)
    thema = db.Column(db.String)
    authors = db.Column(CommaSeparatedStr)
    keywords = db.Column(CommaSeparatedStr)

    file = db.relationship(File,
        lazy='joined',
        backref=db.backref('metadatas', lazy=True))


class FileOwnership(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    file_id = db.Column(db.Integer, db.ForeignKey(File.id),
        nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id),
        nullable=False, primary_key=True)
    count = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship(User, 
        lazy='joined',
        backref=db.backref('files', lazy=True))
    file = db.relationship(File,
        lazy='joined',
        backref=db.backref('users', lazy=True))

    def __repr__(self):
        return '<FileOwnership User=%r;File=%r>' % (self.user, self.file)

    @property
    def serialize(self):
        return {
            'file_id': self.file_id,
            'user_id': self.user_id,
            'count': self.count,
            'created': self.created,
            'modified': self.modified
        }