from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, \
    SubmitField, FieldList, SelectField, RadioField, SelectMultipleField, \
    DateField, DateTimeField, FloatField, DecimalField
from wtforms.validators import (
    DataRequired, InputRequired, Email, EqualTo, NumberRange, ValidationError
)

from . import CommaListField
from .models import FileMetadata


class FileMetadataForm(FlaskForm):
    title = StringField('Title', [
        DataRequired(message='Title is required.')
    ])
    abstract = TextAreaField('Abstract', [
        DataRequired(message='Abstract is required.')
    ])
    authors = CommaListField('Authors')
    keywords = CommaListField('Keywords')
    thema = StringField('Thema')
    date = DateField('Published Date')
    toc = StringField('TOC')

    submit = SubmitField('Save')