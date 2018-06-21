from flask import Flask, Blueprint, request, render_template, \
    flash, g, session, redirect, url_for, abort, current_app
from . import db
from . import TimestampModelMixin
from . import login_required
from . import response_json
from .config import mod_name, spider_cache_expire, get_spider_cache_folder
from .forms import SearchForm
from .spiders import SpiderFactory


bp = Blueprint(mod_name, __name__, url_prefix="/paper")


@bp.route('/', methods=('GET', 'POST'))
def index():
    form = SearchForm()
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
        else:
            return response_json(**spider.get_item())

    return render_template('paper/index.html', form=form)