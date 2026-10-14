# app/cron/__init__.py
from flask import Blueprint

cron_bp = Blueprint('cron', __name__, url_prefix='/cron')

from . import routes