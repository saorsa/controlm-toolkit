from flask import Flask, jsonify
from rest.cache_blueprint import cache_blueprint
from rest.data_centers_blueprint import data_centers_blueprint
from __version__ import controlm_toolkit_version
from threading import Thread
from controlm import sharedCache, CtmXmlParser
from common.logging.helpers import create_console_logger
import json


def invalidate_cache() -> None:
    parser = CtmXmlParser(
        logger=create_console_logger()
    )
    try:
        sharedCache.set_cache_state_error(None)
        sharedCache.set_cache_state_progress()
        def_table = parser.parse_xml('./resources/PROD_CTM.all.xml')
        data_center_keys = []
        data_center_aggregates = {}
        for item in def_table.items:
            if hasattr(item, 'data_center'):
                if item.data_center not in data_center_keys:
                    data_center_keys.append(item.data_center)
                if item.data_center not in data_center_aggregates:
                    data_center_aggregates[item.data_center] = {
                        'applications': {}
                    }
                data_center_apps = data_center_aggregates[item.data_center]['applications']
                if hasattr(item, 'application') and item.application:
                    if item.application not in data_center_apps:
                        data_center_apps[item.application] = []
                    active_app_subs = data_center_apps[item.application]
                    if hasattr(item, 'sub_application') and item.sub_application not in active_app_subs:
                        active_app_subs.append(item.sub_application)
        sharedCache.set_cache_state_complete(def_table, data_center_keys, data_center_aggregates)
    except BaseException as ex:
        parser.logger.fatal(ex)
        sharedCache.set_cache_state_error(ex)


class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, set):
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


cache_thread = Thread(target=invalidate_cache)
cache_thread.start()

app.run()
