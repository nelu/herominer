from flask import Blueprint

hero_api = Blueprint('heroes', __name__)
from . import routes
