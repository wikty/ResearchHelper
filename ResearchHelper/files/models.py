import sqlalchemy as sa
from flask import g

from . import db
from . import TimestampModelMixin
from . import CommaSeparatedStr
from . import User
from . import file_fingerprint
from . import file_uniquename
from . import uuid_generator
from .config import mod_name
from .config import get_upload_folder



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


def save_file(file):
    """Save file and record it in to database.
    :param file: a file object
    :return (message, status), uuid
    """
    fingerprint = file_fingerprint(file) # calulate file content fingerprint
    file.seek(0) # reset file pointer
    if fingerprint is None:
        return (('Something wrong with server, please contact admin.', 'warning'), None)

    # create and store file
    file_model = File.query.filter_by(fingerprint=fingerprint).first()
    if file_model is None:
        ext = ''
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1]
        filename = file_uniquename(
            dirname=get_upload_folder(current_app), 
            ext=ext
        )
        try:
            full_filename = files_collection.save(file, 
                folder=filename[:2], name=filename)
        except UploadNotAllowed as e:
            return (('Upload Failed!', 'warning'), None)
        
        url = files_collection.url(full_filename)
        uuid = None
        while True:
            uuid = uuid_generator()
            if File.query.filter_by(uuid=uuid).first() is None:
                break
        file_model = File(
            uuid=uuid,
            url=url,
            fingerprint=fingerprint,
            dirname=filename[:2],
            filename=filename
        )
        db.session.add(file_model)

    # create file ownership
    ownership = FileOwnership.query.filter(sa.and_(
        FileOwnership.user_id == g.user.id,
        FileOwnership.file_id == file_model.id
    )).first()
    if ownership is None:
        ownership = FileOwnership(file=file_model, user=g.user)
        db.session.add(ownership)
    else:
        ownership.count = ownership.count + 1
    
    db.session.commit()
    return (('Upload Success!', 'success'), file_model.uuid)