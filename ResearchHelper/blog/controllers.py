from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from . import db
from . import login_required
from .models import Post
from .models import PostCategory as Category
from .config import mod_name


# don't specify url prefix, this mod will be hooked into index url
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
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post = Post(title=title, 
                        body=body, 
                        user_id=g.user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.index'))