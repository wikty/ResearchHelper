import os
import sqlalchemy as sa

from flask import Blueprint, request, render_template, flash, g, \
    session, redirect, url_for, current_app
from flask_uploads import UploadSet, configure_uploads, IMAGES, \
    TEXT, DOCUMENTS, AUDIO, DATA, ARCHIVES, UploadNotAllowed, patch_request_class

from . import db
from . import login_required
from . import file_fingerprint
from . import file_uniquename
from . import rlid_generator
from . import uuid_generator
from .config import mod_name
from .models import File as FileModel
from .models import FileOwnership


def get_upload_folder(app):
    return os.path.join(app.instance_path, 'upload')


def get_extension(filename):
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1]


VEDIO = tuple('webm mkv flv mp4 avi'.split())
OTHERS = tuple('pdf tex'.split())


files_collection = UploadSet('FILES', 
    extensions=TEXT+DOCUMENTS+IMAGES+AUDIO+DATA+ARCHIVES+VEDIO+OTHERS,
    default_dest=get_upload_folder)


bp = Blueprint(mod_name, __name__, url_prefix='/files')


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

        fingerprint = file_fingerprint(file) # calulate file content fingerprint
        file.seek(0) # reset file pointer
        if fingerprint is None:
            flash('Something wrong with server, please contact admin.', 'warning')
            return redirect(request.url)

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
                raise
                flash('Upload Failed!', 'warning')
                return redirect(request.url)
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
        flash('upload success!', 'success')
        return redirect(url_for('.manager', uuid=file_model.uuid))
    return render_template('upload/index.html')


@bp.route('/manager/<uuid:uuid>', methods=('GET', 'POST'))
@bp.route('/manager/', methods=('GET', 'POST'), defaults={'uuid': None})
@login_required
def manager(uuid):
    return 'hello manager! {}'.format(uuid)