from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from common.caching import CacheStore
from controlm.di.di_rest_server import DIRestServer
from controlm.services import CtmRepository

cache_blueprint = Blueprint('cache', __name__, template_folder='templates')


@cache_blueprint.route('/cache/keys', methods=['GET'])
@inject
def get_shared_cache_keys(cache: CacheStore = Provide[DIRestServer.shared_cache]):
    keys = cache.cache_keys
    return jsonify(keys)


@cache_blueprint.route('/cache/state', methods=['GET'])
@inject
def get_shared_cache_state(ctm_repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    return jsonify({
        'state': ctm_repository.cache_state,
        'error': ctm_repository.cache_error,
        'ready': ctm_repository.is_cache_ready,
        'timestamp': ctm_repository.cache_timestamp,
        'parsingInterval': ctm_repository.cache_populate_duration,
    })


@cache_blueprint.route('/cache/populate', methods=['GET', 'POST', 'PUT'])
@inject
def schedule_populate_cache(ctm_repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    future = ctm_repository.schedule_populate_cache()
    return jsonify({
        'task_started': True if future else False
    })
