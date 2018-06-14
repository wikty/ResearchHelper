from flask import Flask, Blueprint, request, render_template, \
    flash, g, session, redirect, url_for, abort
from . import db
from . import TimestampModelMixin
from . import login_required
from .config import mod_name


bp = Blueprint(mod_name, __name__, url_prefix="/paper")


@bp.route('/')
def index():
    return "paper index"