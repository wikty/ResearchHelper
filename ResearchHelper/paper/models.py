from . import db, TimestampModelMixin
from .config import mod_name


# class FooBar(db.Model, TimestampModelMixin):
#     __tableprefix__ = mod_name
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False, unique=True)

#     @property
#     def serialize(self):
#         return {
#             "id": self.id
#             "name": self.name
#         }

#     @classmethod
#     def form_meta_kwargs(cls):
#         return {}

#     def __repr__(self):
#         return "<FooBar name=%r> % self.name"