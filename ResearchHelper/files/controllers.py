import os
import sqlalchemy as sa

from flask import Blueprint, request, render_template, flash, g, \
    session, redirect, url_for, current_app, abort
from flask_uploads import UploadNotAllowed

from . import db
from . import login_required
from . import file_fingerprint
from . import file_uniquename
from . import uuid_generator
from .config import mod_name
from .config import per_page
from .config import get_upload_folder
from .models import File as FileModel
from .models import FileOwnership
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
        error, uuid = save_file(file, 
            dirname=get_upload_folder(current_app),
            app=current_app,
            user=g.user,
            db_session=db.session
        )
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
    pagination = FileOwnership.query.filter_by(
        user_id=g.user.id
    ).order_by(
        FileOwnership.modified.desc()
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


def save_file(file, dirname, app, user, db_session):
    """Save file and record it in to database.
    :param file: a FileStorage object
    :param dirname: the target directory to store the file
    :param app: the application instance
    :param user: the owner user who stores the file
    :param db_session: db session
    :return (message, status), uuid
    """
    file.seek(0) # reset file pointer
    fingerprint = file_fingerprint(file) # calulate file content fingerprint
    file.seek(0) # reset file pointer
    if fingerprint is None:
        return (('Something wrong with server, please contact admin.', 'warning'), None)

    # create and store file
    file_model = FileModel.query.filter_by(fingerprint=fingerprint).first()
    if file_model is None:
        # get file extension
        ext = ''
        if '.' in file.filename:
            ext = file.filename.rsplit('.', 1)[1]

        # get unique filename in the `dirname/folder` directory
        filename = None
        folder = None
        while True:
            filename = file_uniquename(ext=ext)
            folder =  filename[:2]
            if not os.path.isfile(os.path.join(dirname, folder, filename)):
                break

        # save into the file system
        try:
            full_filename = files_collection.save(file, 
                folder=folder, name=filename)
        except UploadNotAllowed as e:
            return (('Upload Not Allowed!', 'warning'), None)
        
        # get file url and uuid
        url = files_collection.url(full_filename)
        uuid = None
        while True:
            uuid = uuid_generator()
            if File.query.filter_by(uuid=uuid).first() is None:
                break
        
        # create file model
        file_model = FileModel(
            uuid=uuid,
            url=url,
            fingerprint=fingerprint,
            dirname=folder,
            filename=filename
        )
        db_session.add(file_model)

    # create file ownership model
    ownership = FileOwnership.query.filter(sa.and_(
        FileOwnership.user_id == user.id,
        FileOwnership.file_id == file_model.id
    )).first()
    if ownership is None:
        ownership = FileOwnership(file=file_model, user=user)
        db_session.add(ownership)
    else:
        ownership.count = ownership.count + 1
    
    db_session.commit()
    return (('Upload Success!', 'success'), file_model.uuid)