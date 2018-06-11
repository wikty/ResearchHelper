import functools

from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask.views import MethodView
from werkzeug.exceptions import abort

from .db import db
from .config import admin_role, default_list_template, default_single_template
from .forms import form_factory


# require authentication decorator
def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # redirect to auth blueprint's login()
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


# require authentication decorator
def admin_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if g.user.role == admin_role:
            return view(**kwargs)

        return redirect(url_for('index'))

    return wrapped_view


class ModelAPIView(MethodView):

    def __init__(self, app, endpoint, model, list_template=None,
                 single_template=None, filters=None, form_kwargs=None,
                 enable_flash=True):
        """
        :param app, application/blueprint
        :param model, the model class will be equiped with CRUD API
        :param endpoint, the final endpoint will be `blueprint.endpoint`
        :param list_template, the list template name
        :param single_template, the single template name
        :param filters, the filters for model query, {filter_name:filter}
        :param form_kwargs, the arguments for model form class
        """
        self.model = model
        self.url = url_for(endpoint)
        self.filters = filters or {}
        self.list_template = (list_template or default_list_template)
        self.single_template = (single_template or default_single_template)
        self.ModelForm = form_factory(model, **(form_kwargs or {}))
        self.enable_flash = enable_flash

    def flash(self, *args):
        if self.enable_flash:
            flash(*args)
        else:
            pass

    # form post action of create, update, delete, get
    def action_url(self, action, obj_id=None):
        if action == 'create':
            return self.url
        elif action == 'update':
            return '{}{}/update'.format(self.url, obj_id)
        elif action == 'delete':
            return '{}{}/delete'.format(self.url, obj_id)
        else:
            # there isn't an action for get method
            return None   

    def render_single(self, form, obj_id, action, **kwargs):
        return render_template(self.single_template,
            url=self.url,
            obj_id=obj_id,
            form=form,
            action=action,
            **kwargs
        )

    def render_list(self, obj_list, current_filter, **kwargs):
        return render_template(self.list_template,
            url=self.url,
            filters=self.filters, 
            obj_list=obj_list, 
            current_filter=current_filter,
             **kwargs
        )

    def get(self, obj_id):
        """URL pattern:
        /model/?page=create, get the create page
        /model/<obj_id>?page=update, get the update page
        /model/, get all models
        /model/?filter=filter_name, get all filter models
        /model/<obj_id>, get a model
        """
        page = request.args.get('page', None)
        filter_name = request.args.get('filter', None)
        if obj_id is None:
            # get a model create page
            if page == 'create':
                form = self.ModelForm()
                return self.render_single(form,
                    obj_id=obj_id, action=self.action_url('create'))
            # get models
            else:
                if self.filters.get(filter_name, None):
                    obj_list = self.filters[filter_name](self.model)
                else:
                    obj_list = self.model.query.all()
                return self.render_list(obj_list, 
                    current_filter=filter_name)
        else:
            obj = self.model.query.get_or_404(obj_id)
            # get a model update page
            if page == 'update':
                form = self.ModelForm(obj=obj)
                return self.render_single(form, 
                    obj_id=obj_id, action=self.action_url('update'))
            # get a model detail page
            else:
                form = self.ModelForm(obj=obj)
                return self.render_single(form, 
                    obj_id=obj_id, action=None)

    def post(self, obj_id):
        """URL pattern:
        /model/, create a model
        /model/<obj_id>/update, update a model
        /model/<oj_id>/delete, delete a model
        """
        # create a model
        if obj_id is None:
            form = self.ModelForm()
            if form.validate():
                obj = self.model()
                form.populate_obj(obj)
                db.session.add(obj)
                db.session.commit()
                self.flash('{} is create.'.format(obj))
                return redirect(self.url)
            self.flash('There are some errors, when create {}.'.format(obj))
            return self.render_single(form, 
                obj_id=obj_id, action=self.action_url('create'))
        # update a model
        elif request.path.endswith('update'):
            obj = self.model.query.get_or_404(obj_id)
            form = self.ModelForm(obj=obj)
            if form.validate():
                form.populate_obj(obj)
                db.session.commit()
                self.flash('{} is updated.'.format(obj))
                return self.render_single(form, 
                    obj_id=obj.id, action=None)
            self.flash('There are some errors, when update {}.'.format(obj))
            return self.render_single(form, 
                obj_id=obj_id, action=self.action_url('update'))
        # delete a model
        elif request.path.endswith('delete'):
            obj = self.model.query.get_or_404(obj_id)
            db.session.delete(obj)
            db.session.commit()
            self.flash('{} is deleted.'.format(obj))
            return redirect(self.url)


def register_api(app,
    view, endpoint, url, model, pk='obj_id', pk_type='int',
    view_decorators=[], view_kwargs={}):
    """Register CRUD API into app or blueprint."""
    # get view function
    if isinstance(app, Blueprint):
        # app is a instance of Blueprint
        full_endpoint = '%s.%s' % (app.name, endpoint)
    else:
        # app is a instance of Flask
        full_endpoint = endpoint
    kwargs = {
        'app': app,
        'model': model,
        'endpoint': full_endpoint
    }
    kwargs.update(view_kwargs)
    view_func = view.as_view(endpoint, **kwargs)

    # add decorators for the view function
    for decorator in view_decorators:
        view_func = decorator(view_func)
    # get a model detail page, GET: /model/<model_id>
    # get a model update page, GET: /model/<model_id>?page=update
    url = url.strip('/')
    app.add_url_rule('/%s/<%s:%s>' % (url, pk_type, pk),
        view_func=view_func,
        methods=['GET',]
    )
    # get models, GET: /model/
    # get a model create page, GET: /model/?page=create
    app.add_url_rule('/%s/' % url, 
        view_func=view_func,
        defaults={pk: None}, 
        methods=['GET',]
    )
    # create a model, POST: /model/
    # app.add_url_rule('/%s/create' % url, 
    #     view_func=view_func, 
    #     defaults={pk: None}, 
    #     methods=['GET',]
    # )
    app.add_url_rule('/%s/' % url, 
        view_func=view_func, 
        defaults={pk: None}, 
        methods=['POST',]
    )
    # update a model, POST: /model/<model_id>/update
    # app.add_url_rule('/%s/<%s:%s>/update' % (url, pk_type, pk), 
    #     view_func=view_func, 
    #     methods=['GET',]
    # )
    app.add_url_rule('/%s/<%s:%s>/update' % (url, pk_type, pk), 
        view_func=view_func, 
        methods=['POST',]
    )
    # delete a model, POST url: /model/<model_id>/delete
    app.add_url_rule('/%s/<%s:%s>/delete' % (url, pk_type, pk), 
        view_func=view_func, 
        methods=['POST',]
    )
    return full_endpoint


model_filters = {
    'sorted_by_id': lambda model: model.query.order_by(model.id).all(),
    'sorted_by_created': lambda model: model.query.order_by(model.created).all(),
    'sorted_by_modified': lambda model: model.query.order_by(model.modified).all()
}