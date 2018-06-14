# Import from outsite of current package
from ResearchHelper.db import db
from ResearchHelper.db import TimestampModelMixin
from ResearchHelper.db import CommaSeparatedStr
from ResearchHelper.helper import login_required
from ResearchHelper.utils import file_uniquename
from ResearchHelper.utils import file_fingerprint
from ResearchHelper.utils import uuid_generator
from ResearchHelper.models import User
from ResearchHelper.forms import CommaListField

# Expose the inside of current package
from .controllers import bp
from .config import configure_uploads
from .config import patch_request_class
from .config import files_collection

# `from auth import *` will import those modules
__all__ = ['config', 'controllers', 'models', "forms"]


def init_app(app):
    # add upload sets
    configure_uploads(app, (files_collection,))
    # upload limit config via MAX_CONTENT_LENGTH
    patch_request_class(app, size=None)