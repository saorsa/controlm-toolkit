from abc import ABC
from typing import Optional
from uuid import uuid4
from logging import Logger
<<<<<<< HEAD
from typing import Final, Optional
from threading import Lock
from common.caching import CacheStore
from common.logging import create_console_logger
from common.threading import TaskRunner, TaskMetaData
from controlm.model import CtmJobData
from controlm.services import CtmXmlParser


class CtmRepositoryCacheKeys:

    CACHE_STATE: Final = f"{__name__}.cache.state"
    CACHE_ERROR: Final = f"{__name__}.cache.error"
    CACHE_POPULATE_START: Final = f"{__name__}.cache.populate.start"
    CACHE_POPULATE_END: Final = f"{__name__}.cache.populate.end"
    CACHE_POPULATE_DURATION: Final = f"{__name__}.cache.populate.duration"
    CACHE_TIMESTAMP: Final = f"{__name__}.cache.timestamp"

    CONTROL_M_FOLDERS = f"{__name__}.cache.controlm.folders"
    CONTROL_M_SERVERS = f"{__name__}.cache.controlm.servers"
    CONTROL_M_SERVER_INFOS = f"{__name__}.cache.controlm.server.infos"
    CONTROL_M_NODES = f"{__name__}.cache.controlm.nodes"
    CONTROL_M_APPLICATIONS = f"{__name__}.cache.controlm.applications"
    CONTROL_M_SUB_APPLICATIONS = f"{__name__}.cache.controlm.sub_applications"


class CtmRepositoryCacheState (Enum):
    UNKNOWN: str = 'UNKNOWN',
    PROGRESS: str = 'PROGRESS',
    FAULT: str = 'FAULT',
    COMPLETE: str = 'COMPLETE'
=======

from controlm.services.dto import DtoServerInfo
from corelib.logging import create_console_logger
from controlm.services import CtmCacheManager
>>>>>>> 629961e01142edb6567dcf185449bea1eb4c2cef


class CtmRepository (ABC):

    def __init__(self,
                 cache_manager: CtmCacheManager = None,
                 logger: Logger = None):
        self._identifier: str = f"{__name__}_{uuid4()}"
        self._logger = logger or create_console_logger(__name__)
        if cache_manager is None:
            self._logger.warning(f'[{self.identifier}] Cache manager argument is None. Creating new manager instance.')
        self._cache_manager: CtmCacheManager = cache_manager or CtmCacheManager()
        self._logger.info(f"Repository '{self.identifier}' initialized.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info(f"[{self.identifier}] Repository shutting down...")

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def cache_manager(self) -> CtmCacheManager:
        return self._cache_manager

    def get_server_names(self) -> [str]:
        return self.cache_manager.get_cached_server_names()

    def get_server_aggregate_stats(self) -> dict:
        return self.cache_manager.get_cached_server_aggregate_stats()

<<<<<<< HEAD
    @property
    def cache_populate_duration(self) -> Optional[float]:
        if self.is_cache_ready:
            return self._cache.get_item(CtmRepositoryCacheKeys.CACHE_POPULATE_DURATION)
        return None

    @property
    def is_cache_corrupt(self) -> bool:
        return self.cache_error is not None

    @property
    def is_cache_ready(self) -> bool:
        return not self.is_cache_corrupt and self.cache_state == CtmRepositoryCacheState.COMPLETE

    @property
    def is_populating_cache(self) -> bool:
        return self.cache_state == CtmRepositoryCacheState.PROGRESS

    def populate_cache(self, *args, **kwargs):
        self.logger.debug(f"Populate cache invoked with *args={args} and **kwargs={kwargs}")
        task_meta: TaskMetaData = kwargs['task_meta']
        task_meta.invalidate_thread()
        with self._cache_process_lock:
            if self.is_populating_cache:
                self.logger.warning("Already running cache initialization. Subsequent calls will be ignored.")
                return
            self.cache.set_items_from_dict({
                CtmRepositoryCacheKeys.CACHE_ERROR: None,
                CtmRepositoryCacheKeys.CACHE_STATE: CtmRepositoryCacheState.PROGRESS
            })
            self.logger.debug("Starting cache initialization...")
            date_start = datetime.now()
            parser = CtmXmlParser()
            try:
                def_table = parser.parse_xml('./resources/PROD_CTM.all.xml')
                data_center_keys = []
                application_keys = []
                sub_application_keys = []
                node_id_keys = []
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
                        if hasattr(item, 'node_id') and item.node_id and item.node_id not in node_id_keys:
                            node_id_keys.append(item.node_id)
                        if hasattr(item, 'application') and item.application:
                            if item.application not in data_center_apps:
                                data_center_apps[item.application] = []
                                application_keys.append(item.application)
                            active_app_subs = data_center_apps[item.application]
                            if hasattr(item, 'sub_application') and item.sub_application not in active_app_subs:
                                active_app_subs.append(item.sub_application)
                                sub_application_keys.append(item.sub_application)
                            if hasattr(item, 'jobs') and item.jobs:
                                for job in item.jobs:
                                    if isinstance(job, CtmJobData):
                                        if job.node_id and job.node_id not in node_id_keys:
                                            node_id_keys.append(job.node_id)
                                        if job.application and job.application not in data_center_apps:
                                            data_center_apps[job.application] = []
                                            application_keys.append(job.application)
                                            subs = data_center_apps[job.application]
                                            if job.sub_application and job.sub_application not in subs:
                                                subs.append(job.sub_application)
                                                sub_application_keys.append(job.sub_application)

                self.cache.set_items_from_dict({
                    CtmRepositoryCacheKeys.CONTROL_M_FOLDERS: def_table,
                    CtmRepositoryCacheKeys.CONTROL_M_SERVERS: data_center_keys,
                    CtmRepositoryCacheKeys.CONTROL_M_SERVER_INFOS: data_center_aggregates,
                    CtmRepositoryCacheKeys.CONTROL_M_NODES: node_id_keys,
                    CtmRepositoryCacheKeys.CONTROL_M_APPLICATIONS: application_keys,
                    CtmRepositoryCacheKeys.CONTROL_M_SUB_APPLICATIONS: sub_application_keys,
                    CtmRepositoryCacheKeys.CACHE_STATE: CtmRepositoryCacheState.COMPLETE,
                })
            except BaseException as ex:
                parser.logger.fatal(ex)
                self.cache.set_item(CtmRepositoryCacheKeys.CACHE_STATE, CtmRepositoryCacheState.FAULT)
                self.cache.set_item(CtmRepositoryCacheKeys.CACHE_ERROR, ex)
            finally:
                date_end = datetime.now()
                diff_seconds = (date_end - date_start).total_seconds()
                self.cache.set_item(CtmRepositoryCacheKeys.CACHE_POPULATE_START, date_start)
                self.cache.set_item(CtmRepositoryCacheKeys.CACHE_POPULATE_END, date_end)
                self.cache.set_item(CtmRepositoryCacheKeys.CACHE_TIMESTAMP, date_end)
                self.cache.set_item(CtmRepositoryCacheKeys.CACHE_POPULATE_DURATION, diff_seconds)
                parser.logger.info(f"Parsing started at [{date_start}], finished at [{date_end}]. "
                                   f"Duration = {diff_seconds} seconds")
                task_meta.set_finished(date_end)
                self._cache_task = None

    def schedule_populate_cache(self) -> Optional[Future]:
        with self._cache_lock:
            if self.is_populating_cache:
                self.logger.warning("Already running cache initialization. Returning existing task...")
                return self._cache_task
            self.logger.info("Scheduling cache initialization task...")
            self._cache_task = self.task_runner.schedule_task(
                self.populate_cache,
=======
    def get_server_info_or_default(self, server_name: str) -> Optional[DtoServerInfo]:
        stats = self.get_server_aggregate_stats()
        if server_name in stats:
            return DtoServerInfo(
                name=server_name,
                application_keys=stats[server_name]['applications']
>>>>>>> 629961e01142edb6567dcf185449bea1eb4c2cef
            )
        return None
