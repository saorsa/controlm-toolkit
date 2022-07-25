from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from corelib.caching import CacheStore
from controlm.di.di_rest_server import DIRestServer
from controlm.services import CtmCacheManager

cache_blueprint = Blueprint('cache', __name__, template_folder='templates')


@cache_blueprint.route('/cache/keys', methods=['GET'])
@inject
def get_shared_cache_keys(cache: CacheStore = Provide[DIRestServer.shared_cache]):
    keys = cache.cache_keys
    return jsonify(keys)


@cache_blueprint.route('/cache/state', methods=['GET'])
@inject
def get_shared_cache_state(cache_manager: CtmCacheManager = Provide[DIRestServer.shared_cache_manager]):
    return jsonify({
        'state': cache_manager.cache_state,
        'error': cache_manager.cache_error,
        'ready': cache_manager.is_cache_ready,
        'timestamp': cache_manager.cache_timestamp,
        'parsingInterval': cache_manager.cache_populate_duration,
    })


@cache_blueprint.route('/cache/populate', methods=['GET', 'POST', 'PUT'])
@inject
def schedule_populate_cache(cache_manager: CtmCacheManager = Provide[DIRestServer.shared_cache_manager]):
    future = cache_manager.schedule_populate_cache()
    return jsonify({
        'task_started': True if future else False
    })
