import hashlib

from . import db, TimestampModelMixin, User
from .config import mod_name


def md5_hash(data):
    return hashlib.md5(str(data).encode('utf-8')).hexdigest()


class Source(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False, unique=True)
    urlhash = db.Column(db.String, nullable=False, index=True)
    title = db.Column(db.String, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    published = db.Column(db.DateTime)
    toc = db.Column(db.Text)
    highlights = db.Column(db.Text)
    authors = db.Column(db.CommaSeparatedString)
    categories = db.Column(db.CommaSeparatedString)
    keywords = db.Column(db.CommaSeparatedString)
    doi_link = db.Column(db.String)
    download_link = db.Column(db.String)
    download_hash = db.Column(db.String)
    download_count = db.Column(db.Integer, nullable=False, default=0)
    pull_count = db.Column(db.Integer, nullable=False, default=0)

    @property
    def serialize(self):
        return {
            "id": self.id
        }

    @classmethod
    def form_meta_kwargs(cls):
        return {}

    @classmethod
    def update_or_create(cls, url, **kwargs):
        urlhash = md5_hash(url)
        source = cls.query.filter_by(urlhash=urlhash).first()
        created = False
        if source is None:
            source = cls(url=url, pull_count=0)
            created = True
        for key, value in kwargs.items():
            if value:
                setattr(source, key, value)
        source.urlhash = urlhash
        source.pull_count = source.pull_count + 1
        if created:
            db.session.add(source)
        db.session.commit()
        return source

    def __repr__(self):
        return "<Source title=%r>" % self.title

    def is_downloaded(self):
        return self.download_pull > 0


class Metadata(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    source_id = db.Column(db.Integer,
        db.ForeignKey(Source.id), primary_key=True)
    user_id = db.Column(db.Integer, 
        db.ForeignKey(User.id), primary_key=True)
    title = db.Column(db.String, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    published = db.Column(db.DateTime)
    toc = db.Column(db.Text)
    highlights = db.Column(db.Text)
    authors = db.Column(db.CommaSeparatedString)
    categories = db.Column(db.CommaSeparatedString)
    keywords = db.Column(db.CommaSeparatedString)
    
    source = db.relationship(Source,
        lazy='joined',
        backref=db.backref('users', lazy=True))
    user = db.relationship(User, 
        lazy='joined',
        backref=db.backref('sources', lazy=True))

    @classmethod
    def get_or_create(cls, source, user):
        metadata = cls.query.filter_by(
            user_id=user.id,
            source_id=source.id
        ).first()
        if metadata is None:
            metadata = cls(
                user_id=user.id,
                source_id=source.id,
                title=source.title,
                abstract=source.abstract,
                published=source.published,
                toc=source.toc,
                authors=source.authors,
                categories=source.categories,
                keywords=source.keywords,
                highlights=source.highlights
            )
            db.session.add(metadata)
            db.session.commit()
        return metadata