from flask import Blueprint

task_api = Blueprint('tasks', __name__)

from . import routes
