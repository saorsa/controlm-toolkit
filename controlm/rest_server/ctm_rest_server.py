import enum
import json
from abc import ABC
from datetime import datetime
from dependency_injector.wiring import Provide, inject
from flask import Flask
from controlm.di import DIRestServer
from controlm.services import CtmCacheManager
from controlm.rest_server.blueprints import meta_endpoint, cache_blueprint, tasks_blueprint, data_centers_blueprint


class CtmRestServerJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, str):
            return obj
        if isinstance(obj, int):
            return obj
        if isinstance(obj, float):
            return obj
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, enum.Enum):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, dict):
            return list(obj)
        if hasattr(obj, '_tag_name'):
            return obj.__dict__
        return obj.__dict__


class CtmRestServer(ABC):

    def __init__(self, app: Flask = None):

        self.di: DIRestServer = DIRestServer()
        self.di.wire(packages=[
            __name__,
            '.'
        ])

        self.app = app or Flask(__name__)
        self.app.json_encoder = CtmRestServerJSONEncoder
        self.app.register_blueprint(meta_endpoint)
        self.app.register_blueprint(cache_blueprint)
        self.app.register_blueprint(data_centers_blueprint)
        self.app.register_blueprint(tasks_blueprint)

    @inject
    def run(self,
            cache_manager: CtmCacheManager = Provide[DIRestServer.shared_cache_manager],
            **kwargs):
        cache_manager.schedule_populate_cache()
        self.app.run(**kwargs)


if __name__ == '__main__':
    server = CtmRestServer()
    server.run(port=5001)
