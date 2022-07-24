from flask import Blueprint, jsonify, current_app
from ..ctm_rest_server_meta import CTM_REST_SERVER_META


meta_endpoint = Blueprint('meta', __name__)


@meta_endpoint.route('/', methods=['GET'])
def index():
    return jsonify({
        'maintainer': 'atanas.dragolov@saorsa.bg',
        'description': 'Control-M Toolkit API Server',
        'version': CTM_REST_SERVER_META['version'],
        'discovery_endpoint': '/discover'
    })


@meta_endpoint.route('/discover', methods=['GET'])
def discover():
    result_routes = [{'methods': p.methods, 'rule': p.rule,
                      'args': p.arguments, 'defaults': p.defaults} for p in current_app.url_map.iter_rules()]
    return jsonify({
        'routes': result_routes
    })
