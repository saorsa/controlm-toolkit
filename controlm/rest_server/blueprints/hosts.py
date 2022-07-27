from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from controlm.services import CtmRepository
from controlm.di.di_rest_server import DIRestServer

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
        node = repository.fetch_node_or_die(server, host)
        return jsonify(node)
    except NameError as err:
        jsonify({
            'status': 404,
            'message': err
        }), 404
