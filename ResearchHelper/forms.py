###
# Form usage methods:
# 1. Custom form class
# 1.1 WTForms Form base + WTForms validators
# 1.2 Flask-WTF FlaskForm base + Flask-WTF validators + WTForms validators
# 2. Auto-generate form class from the ORM model of SQLAlchemy
# 2.1 use WTForms extension factory function `wtforms.ext.sqlalchemy.model_form`
# 2.2 use WTForms-Alchemy framework meta class `ModelForm`
# 2.3 auto-generated process needs a base form as base class. We'll use FlaskForm.
###

###
# WTForms form: declarative Form base class.
# More: https://wtforms.readthedocs.io/en/stable/forms.html
###
from wtforms.form import Form as WTFForm

###
# Flask-WTF: simple integration of Flask and WTForms, including CSRF, 
# file upload, and reCAPTCHA.
# A improved version of WTForms.form.Form, please use it as Form base
# instead of WTForms.form.Form.
###
# The form base class used in the my application
from flask_wtf import FlaskForm as BaseForm
from flask_wtf.file import FileField
from flask_wtf.file import FileRequired
from flask_wtf.file import FileAllowed

###
# WTForms fields: fields are responsible for rendering and data 
# conversion. they delegate to validators for data validation.
###
from wtforms.fields import Field as BaseField
from wtforms.fields import BooleanField
from wtforms.fields import DateField
from wtforms.fields import DateTimeField
from wtforms.fields import DecimalField
from wtforms.fields import FileField as WTFFileField
from wtforms.fields import MultipleFileField as WTFMultipleFileField
from wtforms.fields import FloatField
from wtforms.fields import HiddenField
from wtforms.fields import IntegerField
from wtforms.fields import PasswordField
from wtforms.fields import RadioField
from wtforms.fields import SelectField
from wtforms.fields import SelectMultipleField
from wtforms.fields import SubmitField
from wtforms.fields import TextAreaField
# This field is the base for most of the more complicated fields, 
# and represents an <input type="text">.
from wtforms.fields import TextField
# Encapsulate a form as a field in another form.
from wtforms.fields import FormField
# Encapsulate an ordered list of multiple instances of the same 
# field type, keeping data as a list.
from wtforms.fields import FieldList

###
# WTForms widgets: widgets are classes whose purpose are to render
# a field to its usable representation.
###
from wtforms.widgets import Select
from wtforms.widgets import TextArea
from wtforms.widgets import SubmitInput
from wtforms.widgets import FileInput
from wtforms.widgets import CheckboxInput
from wtforms.widgets import HiddenInput
from wtforms.widgets import PasswordInput
from wtforms.widgets import TextInput
from wtforms.widgets import ListWidget
from wtforms.widgets import TableWidget

###
# WTForms validators: A validator simply takes an input, verifies it
# fulfills some criterion, such as a maximum length for a string and
# returns. Or, if the validation fails, raises a ValidationError.
###
# Raised when a validator fails to validate its input.
from wtforms.validators import ValidationError
# If StopValidation is raised, no more validators in the validation 
# chain are called. If raised with a message, the message will be added 
# to the errors list.
from wtforms.validators import StopValidation
# This validator checks that the data attribute on the field is a True value
# (effectively, it does `if field.data`.)
# Note: Unless a very specific reason exists, we recommend using the 
# InputRequired instead.
from wtforms.validators import DataRequired
# Validates that input was provided for this field. 
# Note: InputRequired looks that form-input data was provided, and 
# DataRequired looks at the post-coercion data.
from wtforms.validators import InputRequired
# Allows empty input and stops the validation chain from continuing.
from wtforms.validators import Optional
# Compares the values of two fields.
from wtforms.validators import EqualTo
# 
from wtforms.validators import Email
# IPAddress(ipv4=True, ipv6=False, message=None)
from wtforms.validators import IPAddress
# Length(min=-1, max=-1, message=None)
from wtforms.validators import Length
# 
from wtforms.validators import MacAddress
# NumberRange(min=None, max=None, message=None)
from wtforms.validators import NumberRange
# Validates the field against a user provided regexp.
# Regexp(regex, flags=0, message=None)
from wtforms.validators import Regexp
# 
from wtforms.validators import URL
# 
from wtforms.validators import UUID
# Compares the incoming data to a sequence of valid inputs.
# AnyOf(values, message=None, values_formatter=None)
from wtforms.validators import AnyOf
# Compares the incoming data to a sequence of invalid inputs.
# NoneOf(values, message=None, values_formatter=None)
from wtforms.validators import NoneOf

###
# WTforms extensions:
# WTForms ships with a number of extensions that make it easier to 
# work with other frameworks and libraries, such as Django/SQLAlchemy.
# Most of WTForms extentsions provide a generator for automatically 
# creating forms based on other frameworks' ORM models, such as SQLAlchemy.
###
# access/query SQLAlchemy models data from forms
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
# generate forms from SQLAlchemy models
from wtforms.ext.sqlalchemy.orm import model_form as sa_model_form

###
# WTForms-Alchemy: a toolkit for easier creation of model based forms.
# This is a improved tool of the `wtforms.ext.sqlalchemy.orm.model_form`,
# while you can use QuerySelectField and QuerySelectMultipleField along
# with it.
###
from wtforms_alchemy import model_form_factory

from .db import db
from .utils import split_delimiter_quoted_str


BaseModelForm = model_form_factory(BaseForm)

# You can super this class to create form class or use the following
# metaclass_form_factory.
class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


# from .models import User
# example of user form
# class UserForm(ModelForm):
#     class Meta:
#         model = User


def metaclass_form_factory(model, 
    fields=[], enable_default_validators=True, **meta_kwargs):
    """"
    Some kwargs configuration for the form:
    only=[]
    exclude=[]
    include_primary_keys=False
    include_foreign_keys=False

    More about wtforms-alchemy configuration:
    https://wtforms-alchemy.readthedocs.io/en/latest/configuration.html

    Form Validators
    By default WTForms-Alchemy ModelForm assigns the following validators:
    InputRequired validator if column is not nullable and has no default value
    DataRequired validator if column is not nullable, has no default value and is of type sqlalchemy.types.String
    NumberRange validator if column if of type Integer, Float or Decimal and column info parameter has min or max arguments defined
    DateRange validator if column is of type Date or DateTime and column info parameter has min or max arguments defined
    TimeRange validator if column is of type Time and info parameter has min or max arguments defined
    Unique validator if column has a unique index
    Length validator for String/Unicode columns with max length
    Optional validator for all nullable columns
    """
    classname = '{}Form'.format(model.__name__)
    kwargs = {'model': model}
    # disable WTForms-Alchemy default validators
    if not enable_default_validators:
        kwargs['email_validator'] = None
        kwargs['length_validator'] = None
        kwargs['unique_validator'] = None
        kwargs['number_range_validator'] = None
        kwargs['date_range_validator'] = None
        kwargs['time_range_validator'] = None
        kwargs['optional_validator'] = None
    # get meta args from model class method
    if hasattr(model, 'form_meta_kwargs'):
        kwargs.update(model.form_meta_kwargs())
    # get meta args from meta_kwargs
    kwargs.update(meta_kwargs)
    metaclass = type('Meta', (object, ), kwargs)
    cls = type(classname, (ModelForm, ), {'Meta': metaclass})
    # add/override fields
    for fieldname, fieldtype in fields:
        cls.fieldname = fieldtype
    return cls


def baseclass_form_factory(model, 
    only=None, exclude=None, exclude_pk=True, exclude_fk=True, **kwargs):
    """https://wtforms.readthedocs.io/en/2.2.1/ext.html#wtforms.ext.sqlalchemy.orm.model_form"""
    classname = '{}Form'.format(model.__name__)
    return sa_model_form(
        model=model, 
        db_session=db.session, 
        base_class=BaseForm, 
        only=only, 
        exclude=exclude, 
        type_name=classname,
        exclude_pk=exclude_pk,
        exclude_fk=exclude_fk,
        **kwargs
    )


# Custom Fields
class CommaListField(BaseField):
    """A comma-separated list of tags."""
    widget = TextInput()

    def _value(self):
        # invoked by the TextInput widget to display the value of field
        if self.data:
            return ','.join(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        # invoked when form data income
        if valuelist:
            self.data = split_delimiter_quoted_str(valuelist[0])
        else:
            self.data = []

def select_field_factory(field_name,
    form_class, 
    form_instance=None,
    query_factory=None,
    get_label=None,
    blank_allowed=True,
    blank_label="",
    multiple_selected=False,
    **field_kwargs):
    """Create select field using model query.
    :param field_name: the name of field in the form.
    :param form_class: the form class.
    :param form_instance: the form instance.
    :param query_factory: a function will return query result.
    :param get_label: the label of the field. If a str is provided, then label
        is defined by getattr(model, label). If a function is provided, then
        the function will be called with a model instance as argument, its
        return result will be the label. Otherwise, str(model) will be used.
    :param multiple_selected: the field is allowed multiple selected.
    :param field_kwargs: field arguments, e.g., label, validators, description
        and so on, just like others field arguments.
    """
    # set a dynamic query result in the view
    if form_instance:
        field = getattr(form_instance, field_name)
        field.query = query_factory()
        return
    # set a field in the form class
    kwargs = {
        'get_label': get_label,
        'query_factory': query_factory,
        'allow_blank': blank_allowed,
        'blank_text': blank_label
    }
    kwargs.update(**field_kwargs)

    if multiple_selected:
        select_field = QuerySelectMultipleField(**kwargs)
    else:
        select_field = QuerySelectField(**kwargs)

    setattr(form_class, field_name, select_field)