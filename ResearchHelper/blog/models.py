from sqlalchemy import inspect

from . import db, TimestampModelMixin, User
from .config import mod_name
from . import (
    Category, Tag, Series, CategoryUser, TagUser, SeriesUser,
    CategoryAssociation, TagAssociation, SeriesAssociation, TargetModelType
)



# class PostCategory(db.Model, TimestampModelMixin):
#     # __tablename__ = "post_category"
#     __tableprefix__ = mod_name
#     id = db.Column(db.Integer, primary_key=True)
#     parent_id = db.Column(db.Integer, nullable=False,
#         default=-1)
#     name = db.Column(db.String(50), nullable=False)

#     def __repr__(self):
#         return '<PostCategory %r>' % self.name

#     @property
#     def serialize(self):
#         return {
#             'id': self.id,
#             'parent_id': self.parent_id,
#             'name': self.name
#         }


# class PostTag(db.Model, TimestampModelMixin):
#     # __tablename__ = "post_tag"
#     __tableprefix__ = mod_name
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)

#     def __repr__(self):
#         return '<PostTag %r>' % self.name

#     @property
#     def serialize(self):
#         return {
#             'id': self.id,
#             'name': self.name
#         }


# class PostSeries(db.Model, TimestampModelMixin):
#     # __tablename__ = "post_series"
#     __tableprefix__ = mod_name
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     brief = db.Column(db.Text, nullable=False, default='')

#     def __repr__(self):
#         return '<PostSeries %r>' % self.name

#     @property
#     def serialize(self):
#         return {
#             'id': self.id,
#             'name': self.name,
#             'brief': self.brief
#         }
    

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



    # series = db.relationship(Series,
    #     lazy='subquery',
    #     uselist=False,
    #     secondary=SeriesAssociation.__table__,
    #     primaryjoin='Post.id == SeriesAssociation.target_id',
    #     secondaryjoin='SeriesAssociation.series_id == Series.id',
    #     backref=db.backref('posts', lazy=True))
    series = db.relationship(SeriesAssociation,
        uselist=False,
        primaryjoin='and_(Post.series_id != -1, Post.id == foreign(SeriesAssociation.target_id))')

    categories = db.relationship(CategoryAssociation,
        primaryjoin='Post.id == foreign(CategoryAssociation.target_id)')

    tags = db.relationship(TagAssociation,
        primaryjoin='Post.id == foreign(TagAssociation.target_id)')

    def __repr__(self):
        return '<Post %r>' % self.title

    def get_series(self):
        if self.series_id == -1:
            return None
        else:
            return self.series.series

    def get_categories(self):
        return [association.category for association in self.categories]

    def get_tags(self):
        return [association.tag for association in self.tags]

    def add_series(self, series=None, user_id=-1):
        if series:
            self.series_id = series.id
            association = SeriesAssociation.get_or_create(
                term_id=series.id,
                target_id=self.id,
                target_type=TargetModelType.post
            )
            if association._is_created:
                db.session.add(association)
        else:
            self.series_id = -1

    def add_categories(self, category_list=[], user_id=-1):
        for category in category_list:
            association = CategoryAssociation.get_or_create(
                term_id=category.id,
                target_id=self.id,
                target_type=TargetModelType.post
            )
            association.user_id = user_id
            self.categories.append(association)

    def add_tags(self, tag_list=[], user_id=-1):
        for tag in tag_list:
            association = TagAssociation.get_or_create(
                term_id=tag.id,
                target_id=self.id,
                target_type=TargetModelType.post
            )
            association.user_id = user_id
            self.tags.append(association)

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


# post_tag_link = db.Table('{}_post_tag_link'.format(mod_name),
#     db.Column('tag_id', db.Integer, 
#         db.ForeignKey(PostTag.id), primary_key=True),
#     db.Column('post_id', db.Integer, 
#         db.ForeignKey(Post.id), primary_key=True)
# )

# post_category_link = db.Table('{}_post_category_link'.format(mod_name),
#     db.Column('category_id', db.Integer, 
#         db.ForeignKey(PostCategory.id), primary_key=True),
#     db.Column('post_id', db.Integer, 
#         db.ForeignKey(Post.id), primary_key=True)    
# )