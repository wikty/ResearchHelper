import functools

from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask.views import MethodView
from werkzeug.exceptions import abort

from .db import db
from .config import (
    default_list_template, default_single_template, default_form_template
)


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
        if g.user.is_admin():
            return view(**kwargs)

        return redirect(url_for('index'))

    return wrapped_view


class ModelAPIView(MethodView):
    """CRUD API view class."""

    # GET
    read_list_by_get = '/{url}/'
    read_single_by_get = '/{url}/{id}'
    # POST
    create_action_by_post = '/{url}/'
    update_action_by_post = '/{url}/{id}/update'
    delete_action_by_post = '/{url}/{id}/delete'
    # PUT
    update_action_by_put = '/{url}/{id}'
    # DELETE
    delete_action_by_delete = '/{url}/{id}'

    def __init__(self, endpoint, model, form, pk, pk_type,
        list_template=None, single_template=None, form_template=None, 
        per_page=10, filters=None, enable_flash=True):
        """Model CRUD API view.
        
        :param endpoint: the endpoint of the view function
        :param model: the model class will be equiped with CRUD API
        :param form: the form used to create and update the model
        :param pk: the primary key name of the model
        :param pk_type: the primary key type of the model
        :param list_template: the list template path
        :param single_template: the single template path
        :param form_template: the form template path
        :param per_page: the number of models in each list page
        :param filters: a dict maps filter name to the filter function. the filter
            function accept model class as argument, return a model query object
        :param enable_flash: enable the Flask flash message
        """
        self.endpoint = endpoint
        self.model = model
        self.title = model.__name__
        self.form = form
        self.pk = pk
        self.pk_type = pk_type
        self.list_template = (list_template or default_list_template)
        self.single_template = (single_template or default_single_template)
        self.form_template = (form_template or default_form_template)
        self.filters = filters or {}
        self.per_page = per_page
        self.enable_flash = enable_flash

    @classmethod
    def crud_urls(cls, url, pk='obj_id', pk_type='int'):
        url = url.strip('/')
        urls = {
            'list': [
                (cls.read_list_by_get.format(url=url), 
                    {'methods': ('GET',), 'defaults': {pk: None}})
            ],
            'single': [
                (cls.read_single_by_get.format(url=url, id=('<%s:%s>' % (pk_type, pk))),
                    {'methods': ('GET',)})
            ],
            'create': [
                # process the create POST request
                (cls.create_action_by_post.format(url=url),
                    {'methods': ('POST',), 'defaults': {pk: None}})
            ],
            'update': [
                # process the update POST request
                (cls.update_action_by_post.format(url=url, id=('<%s:%s>' % (pk_type, pk))), 
                    {'methods': ('POST',)}),
                # process the update PUT request
                (cls.update_action_by_put.format(url=url, id=('<%s:%s>' % (pk_type, pk))), 
                    {'methods': ('PUT',)})
            ],
            'delete': [
                # process the delete POST request
                (cls.delete_action_by_post.format(url=url, id=('<%s:%s>' % (pk_type, pk))),
                    {'methods': ('POST',)}),
                # process the delete DELETE request
                (cls.delete_action_by_delete.format(url=url, id=('<%s:%s>' % (pk_type, pk))),
                    {'methods': ('DELETE',)})
            ]
        }
        return urls

    @classmethod
    def register_api(cls,
        blueprint, endpoint, url, model, form,
        pk='obj_id', pk_type='int', per_page=10,
        view_decorators={}, view_kwargs={},
        actions=['create', 'list', 'single', 'update', 'delete']):
        """Register CRUD API into app or blueprint.

        :param blueprint: an app or blueprint instance to bind the api view
        :param endpoint: the endpoint of the view function. Note: the endpoint
            should NOT contain dot
        :param url: the model's index url bind with the view function
        :param model: the model class
        :param form: the form class
        :param pk: the primary key name of the model
        :param pk_type: the primary key type of the model
        :param per_page: the models in the each list page.
        :param view_decorators: a dict to specify decorators for CRUD api. Note: 
            its key is `list`, `single`, `create`, `update`, `create`, and its
            value must be a list of function
        :param view_kwargs: a dict for the view class
        :param actions: the actions will be registered
        """
        # get the full endpoint of the view function
        full_endpoint = endpoint
        if isinstance(blueprint, Blueprint):
            # the app is an instance of Blueprint
            # so add the name of the Blurprint as
            # prefix namespace for the endpoint
            full_endpoint = '%s.%s' % (blueprint.name, endpoint)

        # generate the basic view function
        # Note: must pass the full endpoint into the view class
        kwargs = {
            'model': model,
            'form': form,
            'pk': pk,
            'pk_type': pk_type,
            'endpoint': full_endpoint,
            'per_page': per_page
        }
        kwargs.update(view_kwargs)
        basic_view_func = cls.as_view(endpoint, **kwargs)

        # CRUD URL
        urls = cls.crud_urls(url, pk, pk_type)
        for action in actions:
            if action not in urls:
                continue

            action_view_func = basic_view_func
            if action in view_decorators:
                for decorator in view_decorators[action]:
                    action_view_func = decorator(action_view_func)

            for url_info in urls[action]:
                blueprint.add_url_rule(url_info[0], 
                    view_func=action_view_func,
                    **url_info[1])

        return full_endpoint
    
    def get_post_url(self, action, obj_id):
        url = url_for(self.endpoint).strip('/')
        if action == 'create':
            return self.create_action_by_post.format(url=url)
        elif action == 'update':
            return self.update_action_by_post.format(url=url, id=obj_id)
        elif action == 'delete':
            return self.delete_action_by_post.format(url=url, id=obj_id)
        return None

    def flash(self, message, level='message'):
        if self.enable_flash:
            flash(message, level)
        else:
            pass

    def get_filter_arg(self, name):
        if name in self.filters:
            return name, self.filters.get(name)
        return None

    def get_operation_arg(self, operation):
        if operation in ['create', 'update', 'delete']:
            return operation
        return None

    def render_form(self, form, obj_id, operation, **kwargs):
        action = self.get_post_url(operation, obj_id)
        return render_template(self.form_template,
            form=form,
            action=action,
            endpoint=self.endpoint,
            operation=operation,
            **kwargs
        )

    def render_list(self, pagination, current_filter, **kwargs):
        return render_template(self.list_template,
            filters=self.filters, 
            endpoint=self.endpoint,
            pagination=pagination,
            current_filter=current_filter,
             **kwargs
        )

    def render_single(self, form, obj_id, **kwargs):
        return render_template(self.single_template,
            form=form,
            obj_id=obj_id,
            endpoint=self.endpoint,
            **kwargs
        )

    def get(self, **kwargs):
        """The GET view processor.

        URL pattern:
        /model/, get the first page's models
        /model/?page=n, get the n-th page's models
        /model/?filter=filter_name, get the filter's query models
        /model/<obj_id>, get a model
        /model/?op=create, get the create form page
        /model/<obj_id>?op=update, get the update form page
        /model/<obj_id>?op=delete, get the update form page
        """
        obj_id = kwargs.get(self.pk, None)
        operation = request.args.get('op', 
            default=None, type=self.get_operation_arg)
        if obj_id is None:
            # get a model create page
            if operation == 'create':
                form = self.form()
                return self.render_form(form, None, operation)
            # get models
            else:
                page = request.args.get('page', 
                    default=1, type=int)
                filter = request.args.get('filter', 
                    default=None, type=self.get_filter_arg)
                pagination = None
                if filter is None:
                    pagination = self.model.query.paginate(page, 
                        per_page=self.per_page, error_out=False)
                else:
                    pagination = filter[1](self.model).paginate(page, 
                        per_page=self.per_page, error_out=False)
                return self.render_list(pagination, 
                    current_filter=(filter[0] if filter else None)
                )
        else:
            obj = self.model.query.get_or_404(obj_id)
            form = self.form(obj=obj)
            # get a model update page
            if operation == 'update':
                return self.render_form(form, obj_id, operation)
            elif operation == 'delete':
                return self.render_form(form, obj_id, operation)
            # get a model detail page
            else:
                return self.render_single(form, obj_id)

    def post(self, **kwargs):
        """The POST view processor.

        URL pattern:
        /model/, create a model
        /model/<obj_id>/update, update a model
        /model/<oj_id>/delete, delete a model
        """
        obj_id = kwargs.get(self.pk, None)
        if obj_id is None:
            return self.create()
        elif request.path.endswith('update'):
            return self.put(**kwargs)
        elif request.path.endswith('delete'):
            return self.delete(**kwargs)

    def create(self):
        """Create a model."""
        form = self.form()
        if form.validate():
            obj = self.model()
            form.populate_obj(obj)
            db.session.add(obj)
            db.session.commit()
            self.flash('{} is create.'.format(obj))
            return redirect(url_for(self.endpoint))
        self.flash('There are some errors, when create {}.'.format(obj))
        return self.render_form(form, None, 'create')

    def put(self, **kwargs):
        """Update a model."""
        obj_id = kwargs.get(self.pk, None)
        if obj_id is None:
            abort(400)

        obj = self.model.query.get_or_404(obj_id)
        form = self.form(obj=obj)
        if form.validate():
            form.populate_obj(obj)
            db.session.commit()
            self.flash('{} is updated.'.format(obj))
            return self.render_single(form, obj.id)
        self.flash('There are some errors, when update {}.'.format(obj))
        return self.render_form(form, obj_id, 'update')

    def delete(self, **kwargs):
        """Delete a model."""
        obj_id = kwargs.get(self.pk, None)
        if obj_id is None:
            abort(400)

        obj = self.model.query.get_or_404(obj_id)
        db.session.delete(obj)
        db.session.commit()
        self.flash('{} is deleted.'.format(obj))
        return redirect(url_for(self.endpoint))




# def register_api(blueprint,
#     view, endpoint, url, model, form, 
#     pk='obj_id', pk_type='int', per_page=10,
#     view_decorators={}, view_kwargs={},
#     actions=['create', 'list', 'single', 'update', 'delete']):
#     """Register CRUD API into app or blueprint.
    
#     :param blueprint: an app or blueprint instance to bind the api view
#     :param view: the view class to generate the view function
#     :param endpoint: the endpoint of the view function. Note: the endpoint
#         should NOT contain dot
#     :param url: the model's index url bind with the view function
#     :param model: the model class
#     :param form: the form class
#     :param pk: the primary key name of the model
#     :param pk_type: the primary key type of the model
#     :param per_page: the models in the each list page
#     :param view_decorators: a dict to specify decorators for CRUD api. Note: 
#         its key is `list`, `single`, `create`, `update`, `create`, and its
#         value must be a list of function
#     :param view_kwargs: a dict for the view class
#     :param actions: the actions will be registered
#     """
#     # get the full endpoint of the view function
#     full_endpoint = endpoint
#     if isinstance(blueprint, Blueprint):
#         # the app is an instance of Blueprint
#         # so add the name of the Blurprint as
#         # prefix namespace for the endpoint
#         full_endpoint = '%s.%s' % (blueprint.name, endpoint)

#     # CRUD URL
#     url = url.strip('/')
#     urls = {
#         'list': [
#             ('/%s/' % url, {'methods': ('GET',), 'defaults': {pk: None}})
#         ],
#         'single': [
#             ('/%s/<%s:%s>' % (url, pk_type, pk), {'methods': ('GET',)})
#         ],
#         'create': [
#             # GET the create page/form
#             ('/%s/create' % url, {'methods': ('GET',)}), 
#             # process the create POST request
#             ('/%s/' % url, {'methods': ('POST',)})
#         ],
#         'update': [
#             # GET the update page/form
#             ('/%s/<%s:%s>/update' % (url, pk_type, pk), {'methods': ('GET',)}),
#             # process the update POST request
#             ('/%s/<%s:%s>/update' % (url, pk_type, pk), {'methods': ('POST',)}),
#             # process the update PUT request
#             ('/%s/<%s:%s>' % (url, pk_type, pk), {'methods': ('PUT')}),
#             # process the update PATCH request
#             ('/%s/<%s:%s>' % (url, pk_type, pk), {'methods': ('PATCH',)})
#         ],
#         'delete': [
#             # process the delete DELETE request
#             ('/%s/<%s:%s>' % (url, pk_type, pk), {'methods': ('DELETE',)}),
#             # process the delete POST request
#             ('/%s/<%s:%s>/delete' % (url, pk_type, pk), {'methods': ('POST',)})
#         ]
#     }

#     # generate the basic view function
#     # Note: must pass the full endpoint into the view class
#     kwargs = {
#         'model': model,
#         'form': form,
#         'endpoint': full_endpoint,
#         'urls': urls
#     }
#     kwargs.update(view_kwargs)
#     basic_view_func = view.as_view(endpoint, **kwargs)

#     for action, url_list in urls.items():
#         action_view_func = basic_view_func
#         if action in view_decorators:
#             for decorator in view_decorators[action]:
#                 action_view_func = decorator(action_view_func)

#         for url_info in url_list:
#             app.add_url_rule(url_info[0], 
#                 view_func=action_view_func,
#                 **url_info[1])

#     return full_endpoint

    # # add decorators for the view function
    # for decorator in view_decorators:
    #     view_func = decorator(view_func)
    # # bind url with view
    

    # # get a model detail page, GET: /model/<model_id>
    # # get a model update page, GET: /model/<model_id>?page=update
    # url = url.strip('/')
    # app.add_url_rule('/%s/<%s:%s>' % (url, pk_type, pk),
    #     view_func=view_func,
    #     methods=['GET',]
    # )
    # # get models, GET: /model/
    # # get a model create page, GET: /model/?page=create
    # app.add_url_rule('/%s/' % url, 
    #     view_func=view_func,
    #     defaults={pk: None}, 
    #     methods=['GET',]
    # )
    # # create a model, POST: /model/
    # # app.add_url_rule('/%s/create' % url, 
    # #     view_func=view_func, 
    # #     defaults={pk: None}, 
    # #     methods=['GET',]
    # # )
    # app.add_url_rule('/%s/' % url, 
    #     view_func=view_func, 
    #     defaults={pk: None}, 
    #     methods=['POST',]
    # )
    # # update a model, POST: /model/<model_id>/update
    # # app.add_url_rule('/%s/<%s:%s>/update' % (url, pk_type, pk), 
    # #     view_func=view_func, 
    # #     methods=['GET',]
    # # )
    # app.add_url_rule('/%s/<%s:%s>/update' % (url, pk_type, pk), 
    #     view_func=view_func, 
    #     methods=['POST',]
    # )
    # # delete a model, POST url: /model/<model_id>/delete
    # app.add_url_rule('/%s/<%s:%s>/delete' % (url, pk_type, pk), 
    #     view_func=view_func, 
    #     methods=['POST',]
    # )
    # return full_endpoint