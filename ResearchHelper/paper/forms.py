from urllib.parse import urlparse

from wtforms.fields import StringField, TextAreaField, PasswordField, \
    SubmitField, FieldList, SelectField, RadioField, \
    SelectMultipleField, DateField, DateTimeField, FloatField, \
    DecimalField, BooleanField

from wtforms.validators import DataRequired, InputRequired, Email,\
    EqualTo, NumberRange, Optional, Length, NumberRange, Regexp, \
    AnyOf, NoneOf, UUID, URL, ValidationError, StopValidation

from . import BaseForm
from . import CommaListField
from .spiders import SpiderFactory


# class FooBarForm(BaseForm):
#     name = StringField("Name Label", validators=[
#         DataRequired(message="name is required.")
#     ])

class SearchForm(BaseForm):
    link = StringField("Link", validators=[
        DataRequired(message="link is required."),
        URL(message="Link is invalid.")
    ])

    def link_validator(self, field):
        url = field.data
        if ((not url.startswith('http://'))
            and (not url.startswith('https://'))
            and (not url.startswith('//'))):
            url = '//' + url
        netloc = urlparse(url).netloc
        flag = False
        for spider in SpiderFactory.spiders:
            if netloc.endswith(spider.host):
                flag = True
        if not flag:
            raise ValidationError('Site [%s] is not supported yet' % netloc)

class MetadataForm(BaseForm):
    title = StringField('Title', validators=[
        DataRequired(message='title is required.')
    ])
    abstrace = TextAreaField('Abstract')
    date = DateField('Date')
    toc = TextAreaField('TOC')
    highlights = TextAreaField('Highlights')
    authors = CommaListField('Authors')
    categories = CommaListField('Categories')
    keywords = CommaListField('Keywords')