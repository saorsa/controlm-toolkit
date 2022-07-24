from abc import ABC
from concurrent.futures import Future
from datetime import datetime
from enum import Enum
from uuid import uuid4
from logging import Logger
from typing import Final, Optional
from threading import Lock
from common.caching import CacheStore
from common.logging import create_console_logger
from common.threading import TaskRunner, TaskMetaData
from controlm.services import CtmXmlParser


class CtmRepositoryCacheKeys:

    CACHE_STATE: Final = f"{__name__}.cache.state"
    CACHE_ERROR: Final = f"{__name__}.cache.error"
    CACHE_POPULATE_START: Final = f"{__name__}.cache.populate.start"
    CACHE_POPULATE_END: Final = f"{__name__}.cache.populate.end"
    CACHE_POPULATE_DURATION: Final = f"{__name__}.cache.populate.duration"
    CACHE_TIMESTAMP: Final = f"{__name__}.cache.timestamp"

    CONTROL_M_ALL_FOLDERS = f"{__name__}.cache.controlm.folders.all"
    CONTROL_M_SERVERS = f"{__name__}.cache.controlm.servers"
    CONTROL_M_SERVER_INFOS = f"{__name__}.cache.controlm.server.infos"


class CtmRepositoryCacheState (Enum):
    UNKNOWN: str = 'UNKNOWN',
    PROGRESS: str = 'PROGRESS',
    FAULT: str = 'FAULT',
    COMPLETE: str = 'COMPLETE'


class CtmRepository (ABC):

    def __init__(self,
                 cache: CacheStore = None,
                 task_runner: TaskRunner = None,
                 logger: Logger = None):
        self._identifier: str = f"{__name__}_{uuid4()}"
        self._logger = logger or create_console_logger(__name__)
        if cache is None:
            self._logger.warning('Cache argument is None. Creating new cache instance.')
        self._cache: CacheStore = cache or CacheStore()
        if task_runner is None:
            self._logger.warning('Task runner argument is None. Creating new task runner instance.')
        self._task_runner: TaskRunner = task_runner or TaskRunner()
        self._logger.info(f"Repository '{self.identifier}' initialized.")
        self._cache_lock: Lock = Lock()
        self._cache_process_lock: Lock = Lock()
        self._cache_task: Optional[Future] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Repository shutting down...")
        self.task_runner.shutdown(wait=True)
        self.logger.info("Repository shut down.")

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def task_runner(self) -> TaskRunner:
        return self._task_runner

    @property
    def cache(self) -> CacheStore:
        return self._cache

    @property
    def cache_state(self) -> CtmRepositoryCacheState:
        return self._cache.get_item(CtmRepositoryCacheKeys.CACHE_STATE) or CtmRepositoryCacheState.UNKNOWN

    @property
    def cache_error(self) -> any:
        return self._cache.get_item(CtmRepositoryCacheKeys.CACHE_ERROR)

    @property
    def cache_timestamp(self) -> Optional[datetime]:
        if self.is_cache_ready:
            return self._cache.get_item(CtmRepositoryCacheKeys.CACHE_TIMESTAMP)
        return None

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
                self.cache.set_items_from_dict({
                    CtmRepositoryCacheKeys.CONTROL_M_ALL_FOLDERS: def_table,
                    CtmRepositoryCacheKeys.CONTROL_M_SERVERS: data_center_keys,
                    CtmRepositoryCacheKeys.CONTROL_M_SERVER_INFOS: data_center_aggregates,
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
                parser.logger.warning(f"Parsing started at [{date_start}], finished at [{date_end}]. "
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
            )
            return self._cache_task
