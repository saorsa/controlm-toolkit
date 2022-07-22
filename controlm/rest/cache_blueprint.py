from typing import Optional
from flask import Blueprint, jsonify
from controlm.ctm_rest_cache import shared_rest_cache
from controlm.ctm_cache import schedule_invalidate_cache

cache_blueprint = Blueprint('cache', __name__, template_folder='templates')


class _CacheBlueprintOpts:
    def __init__(self):
        self.active_thread_id: Optional[int] = None


shared_blueprint_opts = _CacheBlueprintOpts()


@cache_blueprint.route('/cache', methods=['GET'])
def cache_info():
    cache_error = shared_rest_cache.cache_error
    return jsonify({
        'state': shared_rest_cache.get_cache_item('CACHE_STATE'),
        'error': str(cache_error) if cache_error else 'None',
        'keys': shared_rest_cache.cache_keys,
    })


@cache_blueprint.route('/cache/<cache_key>', methods=['GET'])
def cache_item(cache_key):
    if cache_key == '':
        return cache_info()
    item = shared_rest_cache.get_cache_item(cache_key)
    return jsonify(item) if item else jsonify({
        'status': 404,
        'message': f"No cache found for key '{cache_key}'"
    }), 404


@cache_blueprint.route('/cache-again', methods=['GET', 'POST', 'PUT'])
def cache_again():
    thread = schedule_invalidate_cache()
    status = 'Processing'
    if shared_blueprint_opts.active_thread_id != thread.native_id:
        shared_blueprint_opts.active_thread_id = thread.native_id
        status = 'New'
    return jsonify({
        'state': status,
        'thread_id': thread.native_id
    })
