from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from controlm.services import CtmRepository
from controlm.di.di_rest_server import DIRestServer

servers_blueprint = Blueprint('servers', __name__, template_folder='templates')


@servers_blueprint.route('/server-names', methods=['GET'])
@inject
def server_names(repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    servers = repository.fetch_server_names()
    return jsonify(servers)


@servers_blueprint.route('/servers', methods=['GET'])
@inject
def servers_info(repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    servers = repository.fetch_server_aggregate_stats()
    return jsonify(servers)


@servers_blueprint.route('/servers-raw', methods=['GET'])
@inject
def servers_info_raw(repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    servers = repository.cache_manager.cache.get_item('controlm.services.ctm_cache_manager.cache.controlm.folders.all')
    return jsonify(servers)


@servers_blueprint.route('/servers/<server>/stats', methods=['GET'])
@inject
def server_info_stats(server: str,
                      repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        server_info = repository.fetch_server_info_or_die(server)
        return jsonify({
            'applicationsCount': len(server_info.application_keys),
            'subApplicationsCount': len(server_info.application_keys),
            'hostsCount': len(server_info.node_infos),
            'foldersCount': len(server_info.folders)
        })
    except NameError:
        jsonify({
            'status': 404,
            'message': f"Server '{server}' not found."
        }), 404


@servers_blueprint.route('/servers/<server>/folders/all', methods=['GET'])
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


@servers_blueprint.route('/servers/<server>/folders/active', methods=['GET'])
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


@servers_blueprint.route('/servers/<server>/folders/disabled', methods=['GET'])
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
