import os
import sqlalchemy as sa

from flask import Blueprint, request, render_template, flash, g, \
    session, redirect, url_for, current_app, abort
from flask_uploads import UploadSet, configure_uploads, IMAGES, \
    TEXT, DOCUMENTS, AUDIO, DATA, ARCHIVES, UploadNotAllowed, patch_request_class

from . import db
from . import login_required
from . import file_fingerprint
from . import file_uniquename
from . import rlid_generator
from . import uuid_generator
from .config import mod_name
from .config import per_page
from .models import File as FileModel
from .models import FileOwnership
from .forms import FileMetadataForm


def get_upload_folder(app):
    return os.path.join(app.instance_path, 'upload')


def get_extension(filename):
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1]


VEDIO = tuple('webm mkv flv mp4 avi'.split())
OTHERS = tuple('pdf tex ps'.split())


files_collection = UploadSet('FILES', 
    extensions=TEXT+DOCUMENTS+IMAGES+AUDIO+DATA+ARCHIVES+VEDIO+OTHERS,
    default_dest=get_upload_folder)


bp = Blueprint(mod_name, __name__, url_prefix='/files')


def save_file(file):
    """Save file and record it in to database.
    :param file: a file object
    :return (message, status), uuid
    """
    fingerprint = file_fingerprint(file) # calulate file content fingerprint
    file.seek(0) # reset file pointer
    if fingerprint is None:
        return (('Something wrong with server, please contact admin.', 'warning'), None)

    # create and store file
    file_model = FileModel.query.filter_by(fingerprint=fingerprint).first()
    if file_model is None:
        ext = get_extension(file.filename)
        filename = file_uniquename(
            dirname=get_upload_folder(current_app), 
            ext=ext
        )
        try:
            full_filename = files_collection.save(file, 
                folder=filename[:2], name=filename)
        except UploadNotAllowed as e:
            return (('Upload Failed!', 'warning'), None)
        
        url = files_collection.url(full_filename)
        uuid = None
        while True:
            uuid = uuid_generator()
            if FileModel.query.filter_by(uuid=uuid).first() is None:
                break
        file_model = FileModel(
            uuid=uuid,
            url=url,
            fingerprint=fingerprint,
            dirname=filename[:2],
            filename=filename
        )
        db.session.add(file_model)

    # create file ownership
    ownership = FileOwnership.query.filter(sa.and_(
        FileOwnership.user_id == g.user.id,
        FileOwnership.file_id == file_model.id
    )).first()
    if ownership is None:
        ownership = FileOwnership(file=file_model, user=g.user)
        db.session.add(ownership)
    else:
        ownership.count = ownership.count + 1
    
    db.session.commit()
    return (('Upload Success!', 'success'), uuid)


@bp.route('/')
@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part.', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file.', 'error')
            return redirect(request.url)
        error, uuid = save_file(file)
        flash(error[0], error[1])
        if error[1] == 'success':
            return redirect(url_for('.manager', uuid=uuid))
        else:
            return redirect(request.url)
    return render_template('files/index.html')


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


