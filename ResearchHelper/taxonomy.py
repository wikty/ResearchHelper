from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import db
from .models import PostCategory as Category

# don't specify url prefix
bp = Blueprint('taxonomy', __name__, url_prefix='/taxonomy')

@bp.route('/category/create', methods=('GET', 'POST'))
@login_required
def category_create():
    if request.method == 'POST':
        name = request.form['category']
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category has been added')
    else:
        flash('Not allowed HTTP method')
    return redirect(url_for('index'))

@bp.route('/category/<int:id>/delete', methods=('CET', 'POST'))
@login_required
def category_delete(id):
    if request.method == 'POST':
        category = Category.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        flash('Category has been deleted')
    else:
        flash('Not allowed HTTP method')
    return redirect(url_for('index'))