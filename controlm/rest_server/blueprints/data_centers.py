from dependency_injector.wiring import Provide
from flask import Blueprint, jsonify

from common.caching import CacheStore
from controlm.di import DIRestServer

data_centers_blueprint = Blueprint('servers', __name__, template_folder='templates')


@data_centers_blueprint.route('/servers', methods=['GET'])
def servers_info(cache: CacheStore = Provide[DIRestServer.shared_cache]):
    servers = cache.get_item('DATA_CENTER_NAMES')
    return jsonify(servers or [])


@data_centers_blueprint.route('/servers/<server>/applications', methods=['GET'])
def servers_apps(server: str,
                 cache: CacheStore = Provide[DIRestServer.shared_cache]):
    servers = cache.get_item('DATA_CENTER_STATS')
    return jsonify(list(servers[server]['applications'].keys())) if servers and server in servers else jsonify({
        'status': 404,
        'message': f"Server '{server}' not found."
    }), 404


@data_centers_blueprint.route('/servers/<server>/applications/<application>', methods=['GET'])
def servers_app_single(server: str,
                       application: str,
                       cache: CacheStore = Provide[DIRestServer.shared_cache]):
    servers = cache.get_item('DATA_CENTER_STATS')
    if servers and server in servers:
        all_app_keys = servers[server]['applications'].keys()
        if all_app_keys and application in all_app_keys:
            return jsonify(list(servers[server]['applications'][application]))
        else:
            jsonify({
                'status': 404,
                'message': f"Application '{application}' not found."
            }), 404
    return jsonify({
        'status': 404,
        'message': f"Server '{server}' not found."
    }), 404
