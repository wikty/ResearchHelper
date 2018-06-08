from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from .db import db

# CRUD
# Create
# Inserting data into the database is a three step process:
# 1. Create the Python object(model)
# 2. Add it to the session
# 3. Commit the session
# Read/Select
# MyModel.query.all()
# MyModel.query.first()
# MyModel.query.get(the_primary_id)
# MyModel.query.filter_by(username=u).first()
# MyModel.query.filter(MyModel.email.endswith('@gmail.com')).all()
# MyModel.query.order_by(MyModel.email).all()
# MyModel.query.limit(10).all()
# Read in flask view to raise 404
# MyModel.query.get_or_404()
# MyModel.query.first_or_404()
# Update
# 1. get the model
# 2. modify the model attributes
# 3. commit the session
# Delete
# 1. get the model
# 2. remove it from session
# 3. commit the session

# Lazy load relationships
# lazy defines when SQLAlchemy will load the data from the database:
# 'select' / True (which is the default, but explicit is better than implicit)
#  means that SQLAlchemy will load the data as necessary in one go using a 
#  standard select statement.
# 'joined' / False tells SQLAlchemy to load the relationship in the same query
#  as the parent using a JOIN statement.
# 'subquery' works like 'joined' but instead SQLAlchemy will use a subquery.
# 'dynamic' is special and can be useful if you have many items and always want
#  to apply additional SQL filters to them. Instead of loading the items 
#  SQLAlchemy will return another query object which you can further refine 
#  before loading the items. Note that this cannot be turned into a different 
#  loading strategy when querying so it’s often a good idea to avoid using this
#  in favor of lazy=True. A query object equivalent to a dynamic user.addresses
#  relationship can be created using Address.query.with_parent(user) while still
#  being able to use lazy or eager loading on the relationship itself as 
#  necessary.
# For example
# Post.tags(eager loading) will be loaded immediately after loading a post, 
# but using a separate query. This always results in two queries when 
# retrieving a post, but when querying for multiple posts you will not get 
# additional queries.
# On the other hand, the list of pages for a tag is something that’s 
# rarely needed. Set Tag.posts to be lazy-loaded so that accessing
# it for the first time will trigger a query to get the list of posts
# for that tag.
# Summary lazy loading
# 1. lazy loading: load relationships via another query(more than one query) 
# 2. eager loading: load relationships via join or subquery(only one query)
# 3. dynmaic loading: instead of loading relationships, another query object
#    will be returned 

# Multiple dastabase binds
# An application may bind with to multiple database engines.
# The Model class use `__bind_key__` to specify which engine is associated
# with it. If there isn's such attribute, means the Model is binded with the
# default database engine.

# Pagination
# MyModel.query.paginate()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

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


class InvitationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=-1)
    code = db.Column(db.String(6), nullable=False, unique=True)
    refer = db.Column(db.Text, nullable=False, default='')
    assigned = db.Column(db.Boolean, nullable=False, default=False)
    created_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
    assigned_date = db.Column(db.DateTime)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
    mod_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
    series_id = db.Column(db.Integer, nullable=False,
        default=-1)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship('User', lazy='joined',
        backref=db.backref('posts', lazy=True))

    categories = db.relationship('Category', secondary='post_category_link',
        lazy='subquery', backref=db.backref('posts', lazy=True))

    tags = db.relationship('Tag', secondary='post_tag_link', lazy='subquery',
        backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return '<Post %r>' % self.title


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=False,
        default=-1)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Category %r>' % self.name


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Tag %r>' % self.name


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    brief = db.Column(db.Text, nullable=False, default='')

    def __repr__(self):
        return '<Series %r>' % self.name


post_tag_link = db.Table('post_tag_link',
    db.Column('tag_id', db.Integer, 
        db.ForeignKey('tag.id'), primary_key=True),
    db.Column('post_id', db.Integer, 
        db.ForeignKey('post.id'), primary_key=True)
)

post_category_link = db.Table('post_category_link',
    db.Column('category_id', db.Integer, 
        db.ForeignKey('category.id'), primary_key=True),
    db.Column('post_id', db.Integer, 
        db.ForeignKey('post.id'), primary_key=True)    
)


class AppConfig(db.Model):
    """This model is binded with the appmeta database engine which just store 
    some data the application provides internally.
    """
    __bind_key__ = 'appmeta'
    id = db.Column(db.Integer, primary_key=True)