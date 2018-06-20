from wtforms import StringField, TextAreaField, PasswordField, \
    SubmitField, FieldList, SelectField, RadioField, SelectMultipleField, \
    DateField, DateTimeField, FloatField, DecimalField

from wtforms.validators import (
    DataRequired, InputRequired, Email, EqualTo, NumberRange, ValidationError
)

from . import metaclass_form_factory as form_factory
from . import select_field_factory
from .models import Category, Tag, Series


# PostForm = form_factory(Post, 
#     include=None, not_null_validator=None, validators={
#     'title': [
#         DataRequired(message='title is required.'),
#     ],
#     'body': [
#         InputRequired(message='body is required.'),
#     ]
# })
# select_field_factory('categories', PostForm, 
#     query_factory=lambda : PostCategory.query.all(),
#     get_label="name",
#     blank_allowed=True,
#     blank_label="No Category",
#     multiple_selected=True
# )
# select_field_factory('tags', PostForm, 
#     query_factory=lambda : PostTag.query.all(),
#     get_label="name",
#     blank_allowed=True,
#     blank_label="No Tag",
#     multiple_selected=True
# )
# select_field_factory('series', PostForm, 
#     query_factory=lambda : PostSeries.query.all(),
#     get_label="name",
#     blank_allowed=True,
#     blank_label="No Series",
#     multiple_selected=False
# )

CategoryForm = form_factory(Category,
    not_null_validator=None,
    unique_validator=None, validators={
    'name': [
        DataRequired(message='name is required.')
    ]
})
select_field_factory('parent', CategoryForm, 
    query_factory=lambda : Category.query.all(),
    get_label="name",
    blank_allowed=True,
    blank_label="No Parent",
    multiple_selected=False
)

TagForm = form_factory(Tag,
    not_null_validator=None, 
    unique_validator=None, validators={
    'name': [
        DataRequired(message='name is required.')
    ]
})
SeriesForm = form_factory(Series,
    not_null_validator=None, 
    unique_validator=None, validators={
    'name': [
        DataRequired(message='name is required.')
    ]
})