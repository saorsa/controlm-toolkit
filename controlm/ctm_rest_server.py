import enum

from flask import Flask, jsonify
from rest.cache_blueprint import cache_blueprint
from rest.data_centers_blueprint import data_centers_blueprint
from controlm import schedule_invalidate_cache
from __version__ import controlm_toolkit_version
import json


class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, int):
            return obj
        if isinstance(obj, enum.Enum):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, dict):
            print(dict)
            return list(obj)
        if hasattr(obj, '_tag_name'):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj.__dict__)


app = Flask(__name__)
app.json_encoder = AdvancedJSONEncoder
app.register_blueprint(cache_blueprint)
app.register_blueprint(data_centers_blueprint)


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'maintainer': 'atanas.dragolov@saorsa.bg',
        'description': 'Control-M Toolkit API Server',
        'version': controlm_toolkit_version,
        'discovery_endpoint': '/discover'
    })


@app.route('/discover', methods=['GET'])
def discover():
    result_routes = [{'methods': p.methods, 'rule': p.rule,
                      'args': p.arguments, 'defaults': p.defaults} for p in app.url_map.iter_rules()]
    return jsonify({
        'routes': result_routes
    })


schedule_invalidate_cache()

app.run()
