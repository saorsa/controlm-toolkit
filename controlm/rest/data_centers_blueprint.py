from flask import Blueprint, jsonify
from controlm.ctm_rest_cache import sharedCache

data_centers_blueprint = Blueprint('servers', __name__, template_folder='templates')


@data_centers_blueprint.route('/servers', methods=['GET'])
def servers_info():
    servers = sharedCache.get_cache_item('DATA_CENTER_NAMES')
    return jsonify(servers or [])


@data_centers_blueprint.route('/servers/<server>', methods=['GET'])
def servers_app_info(server: str):
    servers = sharedCache.get_cache_item('DATA_CENTER_STATS')
    return jsonify(list(servers[server]['applications'].keys())) if servers and server in servers else jsonify({
        'status': 404,
        'message': f"Server '{server}' not found."
    }), 404

