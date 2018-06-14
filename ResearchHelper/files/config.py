import os

from flask_uploads import UploadSet, configure_uploads, IMAGES, \
    TEXT, DOCUMENTS, AUDIO, DATA, ARCHIVES, UploadNotAllowed, patch_request_class


mod_name = 'files'
per_page = 10
upload_folder = 'upload'
collection_name = 'FILES'
VEDIO = tuple('webm mkv flv mp4 avi'.split())
OTHERS = tuple('pdf tex ps'.split())
allowed_extensions = TEXT+DOCUMENTS+IMAGES+AUDIO+DATA+ARCHIVES+VEDIO+OTHERS


def get_upload_folder(app):
    return os.path.join(app.instance_path, upload_folder)


files_collection = UploadSet(collection_name, 
    extensions=allowed_extensions,
    default_dest=get_upload_folder)