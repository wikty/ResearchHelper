from flask import Flask, Blueprint, request, render_template, \
    flash, g, session, redirect, url_for, abort
from . import db
from . import login_required
from .config import mod_name, per_page
from .models import (
    Category, Tag, Series, CategoryUser, TagUser, SeriesUser
)
from .forms import (
    CategoryForm, TagForm, SeriesForm
)

def paginate(query, page_key='page'):
    page = request.args.get(page_key, 
                    default=1, type=int)
    return query.paginate(page, 
        per_page=per_page, error_out=False)


def category_user_get_or_404(category_id):
    item = CategoryUser.query.filter(
        CategoryUser.user_id == g.user.id,
        CategoryUser.category_id == category_id
    ).first()
    if item is None:
        abort(404)
    return item

def tag_user_get_or_404(tag_id):
    item = TagUser.query.filter(
        TagUser.user_id == g.user.id,
        TagUser.tag_id == tag_id
    ).first()
    if item is None:
        abort(404)
    return item


def series_user_get_or_404(series_id):
    item = SeriesUser.query.filter(
        SeriesUser.user_id == g.user.id,
        SeriesUser.series_id == series_id
    ).first()
    if item is None:
        abort(404)
    return item


bp = Blueprint(mod_name, __name__, url_prefix="/taxonomy")


@bp.route('/', endpoint='index')
def index():
    taxonomy_list = [{
        'name': 'Category',
        'endpoint': '.category'
    }, {
        'name': 'Tag',
        'endpoint': '.tag'
    }, {
        'name': 'Series',
        'endpoint': '.series'
    }]
    return render_template('taxonomy/index.html', taxonomy_list=taxonomy_list)


@bp.route('/category/', endpoint='category')
@login_required
def category(): 
    pagination = paginate(Category.query.join(CategoryUser).filter(
        CategoryUser.user_id==g.user.id))
    return render_template('taxonomy/category/list.html', 
        pagination=pagination, endpoint='.category')


@bp.route('/category/<int:id>')
@login_required
def category_detail(id):
    category_user = category_user_get_or_404(id)
    category = category_user.category
    category.count = category_user.count
    parent_category = None
    if category_user.parent_id != -1:
        parent_category_user = category_user_get_or_404(category_user.parent_id)
        parent_category = parent_category_user.category
        parent_category.count = parent_category_user.count
    return render_template('taxonomy/category/single.html', 
        item=category, parent_item=parent_category, endpoint='.category')


@bp.route('/category/create', methods=('GET', 'POST'))
@login_required
def category_create():
    form = CategoryForm()
    if form.validate_on_submit():
        category = CategoryUser.insert_or_update(
            name=form.name.data,
            brief=form.brief.data,
            parent=form.parent.data,
            user=g.user
        )
        flash('{} is created.'.format(category))
        return redirect(url_for('.category'))
    return render_template('taxonomy/category/form.html', 
        form=form, action=url_for('.category_create'), operation='create')


@bp.route('/category/<int:id>/update', methods=('GET', 'POST'))
@login_required
def category_update(id):
    category_user = category_user_get_or_404(id)
    category = category_user.category
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category = CategoryUser.insert_or_update(
            name=form.name.data,
            brief=form.brief.data,
            parent=form.parent.data,
            user=g.user
        )
        flash('{} is updated.'.format(category))
        return redirect(url_for('.category'))
    return render_template('taxonomy/category/form.html',
        form=form, action=url_for('.category_update', id=category.id), operation='update')


@bp.route('/category/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def category_delete(id):
    category_user = category_user_get_or_404(id)
    category = category_user.category
    form = CategoryForm(obj=category)
    if request.method == 'POST':
        db.session.delete(category_user)
        db.session.commit()
        flash('{} is deleted.'.format(category))
        return redirect(url_for('.category'))
    return render_template('taxonomy/category/form.html',
        form=form, action=url_for('.category_delete', id=category.id), operation='delete')


@bp.route('/tag/', endpoint='tag')
@login_required
def tag(): 
    pagination = paginate(Tag.query.join(TagUser).filter(
        TagUser.user_id==g.user.id))
    return render_template('taxonomy/tag/list.html', 
        pagination=pagination, endpoint='.tag')


@bp.route('/tag/<int:id>')
@login_required
def tag_detail(id):
    tag_user = tag_user_get_or_404(id)
    tag = tag_user.tag
    tag.count = tag_user.count
    return render_template('taxonomy/tag/single.html', 
        item=tag, endpoint='.tag')


@bp.route('/tag/create', methods=('GET', 'POST'))
@login_required
def tag_create():
    form = TagForm()
    if form.validate_on_submit():
        tag = TagUser.insert_or_update(
            name=form.name.data,
            brief=form.brief.data,
            user=g.user
        )
        flash('{} is created.'.format(tag))
        return redirect(url_for('.tag'))
    return render_template('taxonomy/tag/form.html', 
        form=form, action=url_for('.tag_create'), operation='create')


@bp.route('/tag/<int:id>/update', methods=('GET', 'POST'))
@login_required
def tag_update(id):
    tag_user = tag_user_get_or_404(id)
    tag = tag_user.tag
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag = TagUser.insert_or_update(
            name=form.name.data,
            brief=form.brief.data,
            user=g.user
        )
        flash('{} is updated.'.format(tag))
        return redirect(url_for('.tag'))
    return render_template('taxonomy/tag/form.html',
        form=form, action=url_for('.tag_update', id=id), operation='update')


@bp.route('/tag/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def tag_delete(id):
    tag_user = tag_user_get_or_404(id)
    tag = tag_user.tag
    form = CategoryForm(obj=tag)
    if request.method == 'POST':
        db.session.delete(tag_user)
        db.session.commit()
        flash('{} is deleted.'.format(tag))
        return redirect(url_for('.tag'))
    return render_template('taxonomy/tag/form.html',
        form=form, action=url_for('.tag_delete', id=id), operation='delete')


@bp.route('/series/', endpoint='series')
@login_required
def series(): 
    pagination = paginate(Series.query.join(SeriesUser).filter(
        SeriesUser.user_id==g.user.id))
    return render_template('taxonomy/series/list.html', 
        pagination=pagination, endpoint='.series')


@bp.route('/series/<int:id>')
@login_required
def series_detail(id):
    series_user = series_user_get_or_404(id)
    series = series_user.series
    series.count = series_user.count
    return render_template('taxonomy/series/single.html', 
        item=series, endpoint='.series')


@bp.route('/series/create', methods=('GET', 'POST'))
@login_required
def series_create():
    form = SeriesForm()
    if form.validate_on_submit():
        series = SeriesUser.insert_or_update(
            name=form.name.data,
            brief=form.brief.data,
            user=g.user
        )
        flash('{} is created.'.format(series))
        return redirect(url_for('.series'))
    return render_template('taxonomy/series/form.html', 
        form=form, action=url_for('.series_create'), operation='create')


@bp.route('/series/<int:id>/update', methods=('GET', 'POST'))
@login_required
def series_update(id):
    series_user = series_user_get_or_404(id)
    series = series_user.series
    form = SeriesForm(obj=series)
    if form.validate_on_submit():
        series = SeriesUser.insert_or_update(
            name=form.name.data,
            brief=form.brief.data,
            user=g.user
        )
        flash('{} is updated.'.format(series))
        return redirect(url_for('.series'))
    return render_template('taxonomy/series/form.html',
        form=form, action=url_for('.series_update', id=id), operation='update')


@bp.route('/series/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def series_delete(id):
    series_user = series_user_get_or_404(id)
    series = series_user.series
    form = SeriesForm(obj=series)
    if request.method == 'POST':
        db.session.delete(series_user)
        db.session.commit()
        flash('{} is deleted.'.format(series))
        return redirect(url_for('.series'))
    return render_template('taxonomy/series/form.html',
        form=form, action=url_for('.series_delete', id=id), operation='delete')
