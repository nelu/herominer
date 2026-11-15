from flask import Blueprint

config_api = Blueprint('configuration', __name__)

from . import routes
