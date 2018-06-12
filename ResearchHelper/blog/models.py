from . import db, TimestampModelMixin, User
from .config import mod_name


class PostCategory(db.Model, TimestampModelMixin):
    # __tablename__ = "post_category"
    __tableprefix__ = mod_name
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=False,
        default=-1)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<PostCategory %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'name': self.name
        }


class PostTag(db.Model, TimestampModelMixin):
    # __tablename__ = "post_tag"
    __tableprefix__ = mod_name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<PostTag %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class PostSeries(db.Model, TimestampModelMixin):
    # __tablename__ = "post_series"
    __tableprefix__ = mod_name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    brief = db.Column(db.Text, nullable=False, default='')

    def __repr__(self):
        return '<PostSeries %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'brief': self.brief
        }
    

class Post(db.Model, TimestampModelMixin):
    # __tablename__ = 'post'
    __tableprefix__ = mod_name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    series_id = db.Column(db.Integer, nullable=False,
        default=-1)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id),
        nullable=False)
    user = db.relationship(User, 
        lazy='joined',
        backref=db.backref('posts', lazy=True))

    categories = db.relationship(PostCategory, 
        lazy='subquery',
        secondary='{}_post_category_link'.format(mod_name), 
        backref=db.backref('posts', lazy=True))

    tags = db.relationship(PostTag, 
        lazy='subquery',
        secondary='{}_post_tag_link'.format(mod_name), 
        backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return '<Post %r>' % self.title

    @property
    def serialize(self):
        """Model return as a serialize dict"""
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'series_id': self.series_id,
            'user': self.user.serialize,
            'categories': [category.serialize for category in self.categories],
            'tags': [tag.serialize for tag in self.tags]
        }

    @classmethod
    def form_meta_kwargs(cls):
        return {
            'include': ('user_id', )
        }


post_tag_link = db.Table('{}_post_tag_link'.format(mod_name),
    db.Column('tag_id', db.Integer, 
        db.ForeignKey(PostTag.id), primary_key=True),
    db.Column('post_id', db.Integer, 
        db.ForeignKey(Post.id), primary_key=True)
)

post_category_link = db.Table('{}_post_category_link'.format(mod_name),
    db.Column('category_id', db.Integer, 
        db.ForeignKey(PostCategory.id), primary_key=True),
    db.Column('post_id', db.Integer, 
        db.ForeignKey(Post.id), primary_key=True)    
)