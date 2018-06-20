import enum
from sqlalchemy.ext.declarative import declared_attr

from . import db, TimestampModelMixin, User
from .config import mod_name

class TargetModelType(enum.Enum):
    post = 1
    paper = 2


class TargetMixin(object):
    target_id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.Enum(TargetModelType), primary_key=True)

    @classmethod
    def get_or_create(cls, term_id, target_id, target_type):
        association = cls.query.filter_by(
            term_id=term_id,
            target_id=target_id,
            target_type=target_type
        ).first()
        if association is None:
            association = cls(
                term_id=term_id,
                target_id=target_id,
                target_type=target_type
            )
            association._is_created = True
        else:
            association._is_created = False
        return association


class UserMixin(object):
    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, 
            db.ForeignKey(User.id), primary_key=True)
    
    @declared_attr
    def user(cls):
        return db.relationship(User, lazy=False)


class Category(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    brief = db.Column(db.Text)

    def __repr__(self):
        return '<Category %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'name': self.name,
            'brief': self.brief
        }


class Tag(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    brief = db.Column(db.Text)

    def __repr__(self):
        return '<Tag %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'brief': self.brief
        }


class Series(db.Model, TimestampModelMixin):
    __tableprefix__ = mod_name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    brief = db.Column(db.Text)

    def __repr__(self):
        return '<Series %r>' % self.name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'brief': self.brief
        }


class CategoryUser(db.Model, TimestampModelMixin, UserMixin):
    __tableprefix__ = mod_name
    parent_id = db.Column(db.Integer, nullable=False,
        default=-1, comment='category parent id')
    category_id = db.Column(db.Integer, 
        db.ForeignKey(Category.id), primary_key=True)
    category = db.relationship(Category, lazy=False)
    count = db.Column(db.Integer, nullable=False,
        default=1, comment='referencing count')

    @classmethod
    def insert_or_update(cls, name, brief, parent, user):
        category = Category.query.filter_by(
            name=name).first()
        if category is None:
            category = Category(name=name, brief=brief)
            db.session.add(category)
        else:
            category.name = name
            category.brief = brief
        db.session.commit()

        if parent is None:
            parent_id = -1
        else:
            parent_id = parent.id

        category_user = CategoryUser.query.filter(
            CategoryUser.user_id == user.id,
            CategoryUser.category_id == category.id
        ).first()
        if category_user is None:
            category_user = CategoryUser()
            category_user.parent_id = parent_id
            category_user.category_id = category.id
            category_user.user_id = user.id
            db.session.add(category_user)
        else:
            category_user.parent_id = parent_id
            category_user.count = category_user.count + 1
        db.session.commit()
        return category


class TagUser(db.Model, TimestampModelMixin, UserMixin):
    __tableprefix__ = mod_name

    tag_id = db.Column(db.Integer,
        db.ForeignKey(Tag.id), primary_key=True)
    tag = db.relationship(Tag, lazy=False)
    count = db.Column(db.Integer, nullable=False,
        default=1, comment='referencing count')

    @classmethod
    def insert_or_update(cls, name, brief, user):
        tag = Tag.query.filter_by(
            name=name).first()
        if tag is None:
            tag = Tag(name=name, brief=brief)
            db.session.add(tag)
        else:
            tag.name = name
            tag.brief = brief
        db.session.commit()

        tag_user = TagUser.query.filter(
            TagUser.user_id == user.id,
            TagUser.tag_id == tag.id
        ).first()
        if tag_user is None:
            tag_user = TagUser()
            tag_user.tag_id = tag.id
            tag_user.user_id = user.id
            db.session.add(tag_user)
        else:
            tag_user.count = tag_user.count + 1
        db.session.commit()
        return tag


class SeriesUser(db.Model, TimestampModelMixin, UserMixin):
    __tableprefix__ = mod_name

    series_id = db.Column(db.Integer,
        db.ForeignKey(Series.id), primary_key=True)
    series = db.relationship(Series, lazy=False)
    count = db.Column(db.Integer, nullable=False,
        default=1, comment='referencing count')

    @classmethod
    def insert_or_update(cls, name, brief, user):
        series = Series.query.filter_by(
            name=name).first()
        if series is None:
            series = Series(name=name, brief=brief)
            db.session.add(series)
        else:
            series.name = name
            series.brief = brief
        db.session.commit()

        series_user = SeriesUser.query.filter(
            SeriesUser.user_id == user.id,
            SeriesUser.series_id == series.id
        ).first()
        if series_user is None:
            series_user = SeriesUser()
            series_user.series_id = series.id
            series_user.user_id = user.id
            db.session.add(series_user)
        else:
            series_user.count = series_user.count + 1
        db.session.commit()
        return series


class CategoryAssociation(db.Model, TimestampModelMixin, TargetMixin, UserMixin):
    __tableprefix__ = mod_name
    term_id = db.Column(db.Integer, 
        db.ForeignKey(Category.id), primary_key=True)
    # category = db.relationship(Category, foreign_keys=[term_id], lazy='joined')
    # or
    category = db.relationship(Category, lazy='joined')


class TagAssociation(db.Model, TimestampModelMixin, TargetMixin, UserMixin):
    __tableprefix__ = mod_name

    term_id = db.Column(db.Integer,
        db.ForeignKey(Tag.id), primary_key=True)
    # tag = db.relationship(Tag, foreign_keys=[term_id], lazy='joined')
    # or
    tag = db.relationship(Tag, lazy='joined')


class SeriesAssociation(db.Model, TimestampModelMixin, TargetMixin, UserMixin):
    __tableprefix__ = mod_name

    term_id = db.Column(db.Integer,
        db.ForeignKey(Series.id), primary_key=True)
    # series = db.relationship(Series, foreign_keys=[term_id], lazy='joined')
    # or
    series = db.relationship(Series, lazy='joined')


    
