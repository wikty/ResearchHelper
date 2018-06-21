from flask import Flask, Blueprint, request, render_template, \
    flash, g, session, redirect, url_for, abort, current_app
from . import db
from . import TimestampModelMixin
from . import login_required
from . import response_json
from .config import mod_name, spider_cache_expire, get_spider_cache_folder
from .forms import SearchForm, MetadataForm
from .models import Paper, PaperMetadata
from .spiders import SpiderFactory


bp = Blueprint(mod_name, __name__, url_prefix="/paper")


def metadata_get_or_404(paper_id, user_id):
    metadata = PaperMetadata.query.filter_by(
        user_id=user_id,
        paper_id=paper_id
    ).first()
    if metadata is None:
        abort(404)
    return metadata


@bp.route('/', methods=('GET', 'POST'), endpoint='index')
def index():
    form = SearchForm()

    if request.method == 'POST' and g.user is None:
        # redirect to auth blueprint's login()
        flash('Please login first, before pull your papr.', 'info')
        return redirect(url_for('auth.login'))

    if form.validate_on_submit():
        spider = SpiderFactory.create_spider(form.link.data, **{
            'cache_enabled': True,
            'cache_dir': get_spider_cache_folder(current_app),
            'cache_expire': spider_cache_expire,
            'encoding': 'utf-8'
        })
        try:
            spider.pull()
        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('.index'))

        item = spider.get_item()
        paper = Paper.update_or_create(**item)
        PaperMetadata.get_or_create(paper, g.user)
        flash("You just pull a paper, maybe it's time to update the metadata.")
        return redirect(url_for('.metadata_update', paper_id=paper.id))

    return render_template('paper/index.html', form=form)


@bp.route('/metadata/<int:paper_id>')
def metadata_detail(paper_id):
    if g.user is None:
        return 'you will see the share paper metadata.'
    else:
        return 'you will see your own metadata.'


@bp.route('/metadata/<int:paper_id>/update', methods=('GET', 'POST'))
@login_required
def metadata_update(paper_id):
    metadata = metadata_get_or_404(user_id=g.user.id, paper_id=paper_id)
    form = MetadataForm(obj=metadata)
    if form.validate_on_submit():
        form.populate_obj(metadata)
        db.session.commit()
        return redirect(url_for('.metadata_detail', paper_id=paper_id))

    return render_template('paper/metadata/form.html', 
        form=form, action=url_for('.metadata_update'))