from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from controlm.services import CtmRepository
from controlm.di.di_rest_server import DIRestServer
from controlm.services.dto.node_info import DtoNodeInfo

hosts_blueprint = Blueprint('hosts', __name__, template_folder='templates')


@hosts_blueprint.route('/servers/<server>/nodes', methods=['GET'])
@inject
def get_node_names(server: str, repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        nodes = repository.fetch_node_names(server)
        return jsonify(nodes)
    except NameError:
        jsonify({
            'status': 404,
            'message': f"Server '{server}' not found."
        }), 404


@hosts_blueprint.route('/servers/<server>/nodes/stats', methods=['GET'])
@inject
def get_node_stats(server: str, repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        stats = repository.fetch_node_stats(server)
        return jsonify(stats)
    except NameError:
        jsonify({
            'status': 404,
            'message': f"Server '{server}' not found."
        }), 404


@hosts_blueprint.route('/servers/<server>/node/<host>', methods=['GET'])
@inject
def get_node(server: str, host: str, repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        host_ref = repository.fetch_host_or_default(server, host)
        node_ref = repository.fetch_node_or_default(server, host)
        if node_ref:
            node_ref.hosts = repository.fetch_hosts(server, host)
            if host_ref:
                node_ref.group = host_ref.group
            return jsonify(node_ref)
        elif host_ref:
            result = DtoNodeInfo()
            return jsonify(result)
        else:
            raise NameError(f"Host group '{host}' not found.")
    except NameError as err:
        jsonify({
            'status': 404,
            'message': err
        }), 404
