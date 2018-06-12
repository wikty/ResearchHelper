from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from . import db
from . import login_required
from . import response_json
from . import status_code
from .models import Post
from .models import PostSeries
from .forms import PostForm
from .config import mod_name


# don't specify url_prefix, so every rules are defined in this blueprint
# that will be hooked into the root path `/`, i.e., there isn't prefix
# for the url rule. In the most time, that means the blueprint is the main
# module in your application. 
# Note: Both url_for('index') and url_for('blog.index') are pointed to the `/`
bp = Blueprint(mod_name, __name__)


def get_post(id, check_author=True):
    # not found, 404
    post = Post.query.get_or_404(id)
    # has on permission, 403
    if check_author and post.user != g.user:
        abort(403)
    return post


@bp.route('/')
def index():
    posts = Post.query.all()
    return render_template('blog/index.html', post_list=posts)


@bp.route('/<int:id>')
def detail(id):
    post = get_post(id)
    post.series = PostSeries.query.get(post.series_id)
    return render_template('blog/single.html', post=post)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        form.populate_obj(post)
        post.user_id = g.user.id
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
        form.populate_obj(post)
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


@bp.route('/api/<int:id>', methods=('GET',))
@bp.route('/api/', methods=('GET',), defaults={'id': None})
@login_required
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