import os

from ResearchHelper.db import db
from ResearchHelper.db import TimestampModelMixin
from ResearchHelper.helper import login_required
# inherit forms via Flask-WTF FlaskForm base class
from ResearchHelper.forms import BaseForm
# create forms via WTForms.ext.sqlalchemy.model_form factory
from ResearchHelper.forms import baseclass_form_factory
# inherit forms via WTForms-Alchemy ModelForm(a subclass of FlaskForm)
from ResearchHelper.forms import ModelForm
# create forms via WTForms-Alchemy factory
from ResearchHelper.forms import metaclass_form_factory
from ResearchHelper.api import response_json

from .controllers import bp
from .config import get_spider_cache_folder

__all__ = ['config', 'controllers', 'models']


def init_app(app):
    dirname = get_spider_cache_folder(app)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)