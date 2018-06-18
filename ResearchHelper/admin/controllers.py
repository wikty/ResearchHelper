import functools

from flask import Flask, Blueprint, request, render_template, flash, g, \
    session, redirect, url_for, current_app



from . import db
from . import admin_models
from . import ModelAPIView
from . import admin_required
from . import model_filters
from . import camel_to_snake_case
from . import form_factory
from .config import mod_name, single_template, list_template


bp = Blueprint(mod_name, __name__, url_prefix='/admin')

# register CRUD api url for models
models = []
for model in admin_models:
    if hasattr(model, '__tablename__'):
        endpoint = camel_to_snake_case(model.__tablename__)
    else:
        endpoint = camel_to_snake_case(model.__name__)
    full_endpoint = ModelAPIView.register_api(
        blueprint=bp,
        endpoint=endpoint,
        url='/{}/'.format(endpoint),
        model=model,
        form=form_factory(model),
        view_decorators=[admin_required,],
        view_kwargs={
            'filters': model_filters
        }
    )
    models.append({
        'name': model.__name__,
        'endpoint': full_endpoint,
        'model': model
    })


# register admin index url
@bp.route('/')
@admin_required
def index():
    model_list = []
    for model in models:
        model_list.append({
            'name': model['name'],
            'url': url_for(model['endpoint'], pk=None),
            'count': model['model'].query.count()
        })
    return render_template('admin/index.html', model_list=model_list)

