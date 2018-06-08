from flask_wtf import FlaskForm
# from flask_wtf import RecaptchaField # recaptcha field
# from flask_wtf import Recaptcha # validator for recaptcha
from wtforms import StringField, TextAreaField, PasswordField, \
    SubmitField, FieldList, SelectField, RadioField, SelectMultipleField, \
    DateField, DateTimeField, FloatField, DecimalField
from wtforms.validators import (
    DataRequired, InputRequired, Email, EqualTo, NumberRange, ValidationError
)

from .models import User, InvitationCode


class LoginForm(FlaskForm):
    username = StringField('Username', [
        InputRequired(message="Username is required."), # form input required
        DataRequired(message="Username is required.") # http post required 
    ])
    password = PasswordField('Password', [
        InputRequired(message="Password is required."),
        DataRequired(message="Password is required.")
    ])
    submit = SubmitField('Login')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = None

    # You CANNOT validate username and password respectively. You should do it together.
    # def validate_username(self, field):
    #     user = User.query.filter_by(username=field.data).first()

    #     if user is None:
    #         raise ValidationError('Incorrect username.')
    #     else:
    #         self._user = user

    # def validate_password(self, field):
    #     user = getattr(self, '_user', None)
    
    #     if (user is None) or (not .user.check_password(field.data)):
    #         raise ValidationError('Incorrect password.')

    def validate(self):
        rv = super().validate()
        if not rv:
            return False

        user = User.query.filter_by(
            username=self.username.data).first()
        if user is None:
            self.username.errors.append('Incorrect username.')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Incorrect password.')
            return False

        # attach user into form, so you can access it in view function
        self._user = user
        return True


class RegisterForm(FlaskForm):
    # Google Recaptcha
    # recaptcha = RecaptchaField('recaptcha', [Recaptcha()])
    invitation = StringField('Invitation Code', [
        InputRequired(message='Invitation Code is required.'),
        DataRequired(message='Invitation Code is required.')
    ])
    refer = StringField('Refer')
    username = StringField('Username', [
        InputRequired(message='Username is required.'),
        DataRequired(message='Username is required.')
    ])
    email = StringField('Email', [
        InputRequired(message='Email is required.'),
        DataRequired(message='Email is required.'),
        Email()
    ])
    password = PasswordField('Password', [
        InputRequired(message='Password is required.'),
        DataRequired(message='Password is required.')
    ])
    confirm  = PasswordField('Re-Password',[
        InputRequired(message='Re-Password is required.'),
        DataRequired(message='Re-Password is required.'),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._invitation = None

    def validate_invitation(self, field):
        invitation = InvitationCode.query.filter_by(code=field.data).first()
        if invitation is None:
            raise ValidationError('Invitation Code is invalid.')
        if invitation.assigned:
            raise ValidationError('Invitation Code has already been used.')
        self._invitation = invitation

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError('User {} is already registered.'.format(field.data))