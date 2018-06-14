from wtforms.fields import StringField, TextAreaField, PasswordField, \
    SubmitField, FieldList, SelectField, RadioField, \
    SelectMultipleField, DateField, DateTimeField, FloatField, \
    DecimalField, BooleanField

from wtforms.validators import DataRequired, InputRequired, Email,\
    EqualTo, NumberRange, Optional, Length, NumberRange, Regexp, \
    AnyOf, NoneOf, UUID, URL, ValidationError, StopValidation

from . import BaseForm


# class FooBarForm(BaseForm):
#     name = StringField("Name Label", validators=[
#         DataRequired(message="name is required.")
#     ])