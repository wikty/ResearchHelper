from wtforms import StringField, TextAreaField, PasswordField, \
    SubmitField, FieldList, SelectField, RadioField, SelectMultipleField, \
    DateField, DateTimeField, FloatField, DecimalField

from wtforms.validators import (
    DataRequired, InputRequired, Email, EqualTo, NumberRange, ValidationError
)

from . import form_factory
from .models import Post, PostCategory, PostTag, PostSeries


PostForm = form_factory(Post, 
    include=None, not_null_validator=None, validators={
    'title': [
        DataRequired(message='title is required.'),
    ],
    'body': [
        InputRequired(message='body is required.'),
    ]})
PostCategoryForm = form_factory(PostCategory,
    not_null_validator=None, validators={
    'name': [
        DataRequired(message='name is required.')
    ]})
PostTagForm = form_factory(PostTag,
    not_null_validator=None, validators={
    'name': [
        DataRequired(message='name is required.')
    ]})
PostSeriesForm = form_factory(PostSeries,
    not_null_validator=None, validators={
    'name': [
        DataRequired(message='name is required.')
    ]})