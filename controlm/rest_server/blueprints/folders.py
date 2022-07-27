from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify
from controlm.services import CtmRepository
from controlm.di.di_rest_server import DIRestServer

folders_blueprint = Blueprint('folders', __name__, template_folder='templates')


@folders_blueprint.route('/servers/<server>/folder/<folder>', methods=['GET'])
@inject
def filter_all_folders(server: str,
                       folder: str,
                       repository: CtmRepository = Provide[DIRestServer.ctm_repository]):
    try:
        folder_info = repository.fetch_folder_or_die(
            server,
            folder
        )
        return jsonify(folder_info)
    except NameError:
        jsonify({
            'status': 404,
            'message': f"Server '{server}' not found."
        }), 404
