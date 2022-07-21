from flask import Blueprint, jsonify
from controlm.ctm_rest_cache import sharedCache

cache_blueprint = Blueprint('cache', __name__, template_folder='templates')


@cache_blueprint.route('/cache', methods=['GET'])
def cache_info():
    cache_error = sharedCache.cache_error
    return jsonify({
        'state': sharedCache.get_cache_item('CACHE_STATE'),
        'error': str(cache_error) if cache_error else 'None',
        'keys': sharedCache.cache_keys,
    })


@cache_blueprint.route('/cache/<cache_key>', methods=['GET'])
def cache_item(cache_key):
    if cache_key == '':
        return cache_info()
    item = sharedCache.get_cache_item(cache_key)
    return jsonify(item) if item else jsonify({
        'status': 404,
        'message': f"No cache found for key '{cache_key}'"
    }), 404
