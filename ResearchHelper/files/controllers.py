from flask import Blueprint, request, render_template, flash, g, \
    session, redirect, url_for, current_app, abort

from . import db
from . import login_required
from .config import mod_name
from .config import per_page
from .models import File as FileModel
from .models import FileOwnership
from .models import save_file
from .forms import FileMetadataForm
from .forms import FileUploadForm


bp = Blueprint(mod_name, __name__, url_prefix='/files')


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        
        # if 'file' not in request.files:
        #     flash('No file part.', 'error')
        #     return redirect(request.url)
        # file = request.files['file']
        file = form.file.data

        if file.filename == '':
            flash('No selected file.', 'error')
            return redirect(request.url)
        error, uuid = save_file(file)
        flash(error[0], error[1])
        if error[1] == 'success':
            return redirect(url_for('.manager', uuid=uuid))
        else:
            return redirect(request.url)
    return render_template('files/index.html', form=form)


@bp.route('/list/', defaults={'page': 1})
@bp.route('/list/<int:page>')
@login_required
def list(page):
    pagination = FileModel.query.order_by(
        FileModel.created.desc()
    ).paginate(page, per_page, error_out=False)
    return render_template('files/list.html', 
        pagination=pagination, endpoint='.list')


@bp.route('/manager/', methods=('GET',), defaults={'uuid': None})
@bp.route('/manager/<uuid:uuid>', methods=('GET', 'POST'))
@login_required
def manager(uuid):
    if uuid is None:
        return 'hello manager!'
    # file = FileModel.query.filter_by(uuid=uuid).first()
    # if file is None:
    #     abort(404)
    form = FileMetadataForm()
    if form.validate_on_submit():
        pass

    return render_template('files/form.html', form=form)


