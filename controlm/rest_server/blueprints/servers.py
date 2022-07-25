from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from controlm.services import CtmRepository
from controlm.di.di_rest_server import DIRestServer

data_centers_blueprint = Blueprint('servers', __name__, template_folder='templates')


@data_centers_blueprint.route('/servers', methods=['GET'])
@inject
def servers_info(repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    servers = repository.fetch_server_aggregate_stats()
    return jsonify(servers)


@data_centers_blueprint.route('/servers-raw', methods=['GET'])
@inject
def servers_info_raw(repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    servers = repository.cache_manager.cache.get_item('controlm.services.ctm_cache_manager.cache.controlm.folders.all')
    return jsonify(servers)


@data_centers_blueprint.route('/servers/<server>/folders/all', methods=['GET'])
@inject
def filter_all_folders(server: str,
                       repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        folder_infos = repository.fetch_folders(
            server,
            folder_order_methods=[],
            folder_node_ids=[]
        )
        return jsonify(folder_infos)
    except NameError:
        jsonify({
            'status': 404,
            'message': f"Server '{server}' not found."
        }), 404


@data_centers_blueprint.route('/servers/<server>/folders/active', methods=['GET'])
@inject
def filter_active_folders(server: str,
                          repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        folder_infos = repository.fetch_folders(
            server,
            folder_order_methods=['SYSTEM'],
            folder_node_ids=[]
        )
        return jsonify(folder_infos)
    except NameError:
        jsonify({
            'status': 404,
            'message': f"Server '{server}' not found."
        }), 404


@data_centers_blueprint.route('/servers/<server>/folders/disabled', methods=['GET'])
@inject
def filter_disabled_folders(server: str,
                            repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        folder_infos = repository.fetch_folders(
            server,
            folder_order_methods=[None],
            folder_node_ids=[]
        )
        return jsonify(folder_infos)
    except NameError:
        jsonify({
            'status': 404,
            'message': f"Server '{server}' not found."
        }), 404


@data_centers_blueprint.route('/servers/<server>/nodes/stats', methods=['GET'])
@inject
def server_node_stats(server: str,
                      repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        stats = repository.fetch_node_stats(server)
        print(stats)
        return jsonify(stats)
    except NameError:
        jsonify({
            'status': 404,
            'message': f"Server '{server}' not found."
        }), 404
