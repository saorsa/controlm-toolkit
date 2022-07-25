from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from controlm.services import CtmRepository
from corelib.caching import CacheStore
from controlm.di.di_rest_server import DIRestServer

data_centers_blueprint = Blueprint('servers', __name__, template_folder='templates')


@data_centers_blueprint.route('/servers', methods=['GET'])
@inject
def servers_info(repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    servers = repository.get_server_names()
    return jsonify(servers)


@data_centers_blueprint.route('/servers/<server>/applications', methods=['GET'])
@inject
def servers_apps(server: str,
                 repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    server_info = repository.get_server_info_or_default(server)
    return jsonify(list(server_info.application_keys)) if server_info else jsonify({
        'status': 404,
        'message': f"Server '{server}' not found."
    }), 404
