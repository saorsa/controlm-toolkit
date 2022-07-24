from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from common.threading import TaskRunner
from controlm.di.di_rest_server import DIRestServer


tasks_blueprint = Blueprint('task_runner', __name__, template_folder='templates')


@tasks_blueprint.route('/tasks', methods=['GET'])
@inject
def get_shared_cache_keys(task_runner: TaskRunner = Provide[DIRestServer.shared_task_runner]):
    return jsonify(task_runner.tasks_meta_data)
