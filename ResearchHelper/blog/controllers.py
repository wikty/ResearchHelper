from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from . import db
from . import login_required
from . import response_json
from . import status_code
from .models import Post
# from .models import PostCategory
# from .models import PostTag
# from .models import PostSeries
from .forms import PostForm
# from .forms import PostCategoryForm
# from .forms import PostTagForm
# from .forms import PostSeriesForm
from .config import mod_name, per_page


# don't specify url_prefix, so every rules are defined in this blueprint
# that will be hooked into the root path `/`, i.e., there isn't prefix
# for the url rule. In the most time, that means the blueprint is the main
# module in your application. 
# Note: Both url_for('index') and url_for('blog.index') are pointed to the `/`
bp = Blueprint(mod_name, __name__)


def paginate(query, page_key='page'):
    page = request.args.get(page_key, default=1, type=int)
    return query.paginate(page,
        per_page=per_page, error_out=False)


def get_post(id, check_author=True):
    # not found, 404
    post = Post.query.get_or_404(id)
    # has on permission, 403
    if check_author and post.user != g.user:
        abort(403)
    return post

def populate_post(post, form, user):
    post.user = user
    post.title = form.title.data
    post.body = form.body.data
    post.add_series(form.series.data, user.id)
    post.add_categories(form.categories.data, user.id)
    post.add_tags(form.tags.data, user.id)

# CRUD of blog

@bp.route('/')
def index():
    filter_name = request.args.get('filter', default=None)
    if filter_name == 'only_my' and g.user:
        pagination = paginate(Post.query.filter_by(user_id=g.user.id))
    else:
        pagination = paginate(Post.query)
    return render_template('blog/list.html', 
        pagination=pagination, endpoint='.index')


@bp.route('/<int:id>')
def detail(id):
    post = get_post(id, False)
    return render_template('blog/single.html', 
        post=post, series=post.get_series(), categories=post.get_categories(),
        tags=post.get_tags(), endpoint='.index')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        populate_post(post, form, g.user)
        db.session.add(post)
        db.session.commit()
        flash('{} is created.'.format(post))
        return redirect(url_for('.index'))
    return render_template('blog/form.html', 
        form=form, action=url_for('.create'))


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        populate_post(post, form, g.user)
        db.session.commit()
        flash('{} is updated.'.format(post))
        return redirect(url_for('.index'))
    return render_template('blog/form.html', 
        form=form, action=request.path)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('.index'))


# CRUD of category

# @bp.route('/category/')
# def category_index():
#     categories = PostCategory.query.all()
#     return render_template('blog/category/list.html', category_list=categories)


# @bp.route('/category/<int:id>')
# def category_detail(id):
#     category = PostCategory.query.get_or_404(id)
#     return render_template('blog/category/single.html', category=category)


# @bp.route('/category/create', methods=('GET', 'POST'))
# @login_required
# def category_create():
#     form = PostCategoryForm()
#     if form.validate_on_submit():
#         category = PostCategory()
#         form.populate_obj(category)
#         if form.parent.data is None:
#             category.parent_id = -1
#         else:
#             category.parent_id = form.parent.id
#         db.session.add(category)
#         db.session.commit()
#         flash('{} is created.'.format(category))
#         return redirect(url_for('.category_index'))
#     return render_template('blog/category/form.html', 
#         form=form, action=url_for('.category_create'))


# # for now user can update/delete others' category
# # should be fix this in later.
# @bp.route('/category/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def category_update(id):
#     category = PostCategory.query.get_or_404(id)
#     form = PostCategoryForm(obj=category)
#     if form.validate_on_submit():
#         form.populate_obj(category)
#         if form.parent.data is None:
#             category.parent_id = -1
#         else:
#             category.parent_id = form.parent.id
#         db.session.commit()
#         flash('{} is updated.'.format(category))
#         return redirect(url_for('.category_index'))
#     return render_template('blog/category/form.html',
#         form=form, action=url_for('.category_update'))


# @bp.route('/category/<int:id>/delete', methods=('GET', 'POST'))
# @login_required
# def category_delete(id):
#     category = PostCategory.query.get_or_404(id)
#     db.session.delete(category)
#     db.session.commit()
#     flash('{} is deleted.'.format(category))
#     return redirect(url_for('.category_index'))


# CRUD of tag

# @bp.route('/category/')
# def category_index():
#     categories = PostCategory.query.all()
#     return render_template('blog/category/list.html', category_list=categories)

# @bp.route('/category/<int:id>')
# def category_detail(id):
#     category = PostCategory.query.get_or_404(id)
#     return render_template('blog/category/single.html', category=category)

# @bp.route('/category/create', methods=('GET', 'POST'))
# @login_required
# def category_create():
#     pass

# @bp.route('/category/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def category_update(id):
#     pass

# @bp.route('/category/<int:id>/delete', methods=('GET', 'POST'))
# @login_required
# def category_delete(id):
#     pass


# CRUD of series

# @bp.route('/category/')
# def category_index():
#     categories = PostCategory.query.all()
#     return render_template('blog/category/list.html', category_list=categories)

# @bp.route('/category/<int:id>')
# def category_detail(id):
#     category = PostCategory.query.get_or_404(id)
#     return render_template('blog/category/single.html', category=category)

# @bp.route('/category/create', methods=('GET', 'POST'))
# @login_required
# def category_create():
#     pass

# @bp.route('/category/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def category_update(id):
#     pass

# @bp.route('/category/<int:id>/delete', methods=('GET', 'POST'))
# @login_required
# def category_delete(id):
#     pass


# JSON API of blog

@bp.route('/api/<int:id>', methods=('GET',))
@bp.route('/api/', methods=('GET',), defaults={'id': None})
def api_index(id):
    if id is None:
        return response_json(
            message='ok',
            status=status_code['ok'],
            post_list=[post.serialize for post in Post.query.all()]
        )
    else:
        post = get_post(id)
        return response_json(
            message='ok',
            status=status_code['ok'],
            post=post.serialize
        )


@bp.route('/api/create', methods=('POST',))
@login_required
def api_create():
    title = request.form['title']
    body = request.form['body']
    if not title:
        error = 'Title is required.'

    if error is not None:
        return response_json(
            message=error, 
            status=status_code['post_field_required_error'], 
            post={'title': title, 'body': body}
        )
    post = Post(title=title,
                body=body,
                user_id=g.user_id)
    db.session.add(post)
    db.session.commit()
    return response_json(
        message='{} is created.'.format(post),
        status=status_code['ok']
    )


@bp.route('/api/<int:id>/update', methods=('GET', 'POST',))
@login_required
def api_update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if not title:
            error = 'Title is required.'

        if error is not None:
            return response_json(
                message=error, 
                status=status_code['post_field_required_error'], 
                post={'title': title, 'body': body}
            )
        post.title = title
        post.body = body
        db.session.commit()
        return response_json(
            message='{} is updated.'.format(post),
            status=status_code['ok']
        )
    return response_json(
        message='ok',
        status=status_code['ok'],
        post=post.serialize
    )


@bp.route('/api/<int:id>/delete', methods=('POST',))
@login_required
def api_delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return response_json(
        message='{} is deleted'.format(post),
        status=status_code['ok']
    )