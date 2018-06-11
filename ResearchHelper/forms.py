# WTForms-Alchemy work with Flask-WTF
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory

from .db import db
# from .models import User


BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

# example of user form
# class UserForm(ModelForm):
#     class Meta:
#         model = User

def form_factory(model, **meta_kwargs):
    """"
    Some kwargs configuration for the form:
    only=[]
    exclude=[]
    include_primary_keys=False
    include_foreign_keys=False
    
    More about wtforms-alchemy configuration:
    https://wtforms-alchemy.readthedocs.io/en/latest/configuration.html
    """
    classname = '{}Form'.format(model.__name__)
    meta_kwargs['model'] = model
    metaclass = type('Meta', (object, ), meta_kwargs)
    return type(classname, (ModelForm, ), {'Meta': metaclass})