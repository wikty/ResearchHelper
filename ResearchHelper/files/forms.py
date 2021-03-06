from flask_wtf import FlaskForm as BaseForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, \
    SubmitField, FieldList, SelectField, RadioField, SelectMultipleField, \
    DateField, DateTimeField, FloatField, DecimalField
from wtforms.validators import (
    DataRequired, InputRequired, Email, EqualTo, NumberRange, ValidationError
)

from . import CommaListField
from .models import FileMetadata
from .config import allowed_extensions


class FileUploadForm(BaseForm):
    file = FileField('Choose File', validators=[
        FileRequired(message='File is required.'),
        FileAllowed(allowed_extensions, message='File format not allowed.')
    ])
    submit = SubmitField('Upload')


class FileMetadataForm(BaseForm):
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