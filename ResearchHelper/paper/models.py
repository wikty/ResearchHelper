import hashlib

from . import db, TimestampModelMixin, User
from .config import mod_name


class Paper(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False, unique=True)
    urlhash = db.Column(db.String, nullable=False, index=True)
    title = db.Column(db.String, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    date = db.Column(db.String)
    toc = db.Column(db.Text)
    authors = db.Column(db.CommaSeparatedString)
    categories = db.Column(db.CommaSeparatedString)
    keywords = db.Column(db.CommaSeparatedString)
    highlights = db.Column(db.Text)
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
        urlhash = hashlib.md5(str(url).encode('utf-8')).hexdigest()
        paper = cls.query.filter_by(urlhash=urlhash).first()
        created = False
        if paper is None:
            paper = cls(url=url, pull_count=0)
            created = True
        for key, value in kwargs.items():
            if value:
                setattr(paper, key, value)
        paper.urlhash = urlhash
        paper.pull_count = paper.pull_count + 1
        if created:
            db.session.add(paper)
        db.session.commit()
        return paper

    def __repr__(self):
        return "<Paper title=%r>" % self.title

    def is_downloaded(self):
        return self.download_pull > 0


class PaperMetadata(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    paper_id = db.Column(db.Integer,
        db.ForeignKey(Paper.id), primary_key=True)
    user_id = db.Column(db.Integer, 
        db.ForeignKey(User.id), primary_key=True)
    title = db.Column(db.String, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    date = db.Column(db.String)
    toc = db.Column(db.Text)
    highlights = db.Column(db.Text)
    authors = db.Column(db.CommaSeparatedString)
    categories = db.Column(db.CommaSeparatedString)
    keywords = db.Column(db.CommaSeparatedString)
    
    paper = db.relationship(Paper,
        lazy='joined',
        backref=db.backref('users', lazy=True))
    user = db.relationship(User, 
        lazy='joined',
        backref=db.backref('papers', lazy=True))

    @classmethod
    def get_or_create(cls, paper, user):
        metadata = cls.query.filter_by(
            user_id=user.id,
            paper_id=paper.id
        ).first()
        if metadata is None:
            metadata = cls(
                user_id=user.id,
                paper_id=paper.id,
                title=paper.title,
                abstract=paper.abstract,
                date=paper.date,
                toc=paper.toc,
                authors=paper.authors,
                categories=paper.categories,
                keywords=paper.keywords,
                highlights=paper.highlights
            )
            db.session.add(metadata)
            db.session.commit()
        return metadata