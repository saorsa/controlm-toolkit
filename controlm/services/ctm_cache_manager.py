from abc import ABC
from concurrent.futures import Future
from datetime import datetime
from enum import Enum
from logging import Logger
from threading import Lock
from typing import Final, Dict, Optional
from uuid import uuid4
from controlm.model import CtmDefTable
from controlm.services import CtmXmlParser
from controlm.services.dto import map_server_infos_from_ctm_model, DtoServerInfo
from corelib.caching import CacheStore
from corelib.logging import create_console_logger
from corelib.threading import TaskRunner, TaskMetaData


class CtmCacheManagerKeys:

    CACHE_STATE: Final = f"{__name__}.cache.state"
    CACHE_ERROR: Final = f"{__name__}.cache.error"
    CACHE_POPULATE_START: Final = f"{__name__}.cache.populate.start"
    CACHE_POPULATE_END: Final = f"{__name__}.cache.populate.end"
    CACHE_POPULATE_DURATION: Final = f"{__name__}.cache.populate.duration"
    CACHE_TIMESTAMP: Final = f"{__name__}.cache.timestamp"

    CONTROL_M_ALL_FOLDERS = f"{__name__}.cache.controlm.folders.all"
    CONTROL_M_ALL_FOLDERS_DTO = f"{__name__}.cache.controlm.folders.all.dto"
    CONTROL_M_SERVERS = f"{__name__}.cache.controlm.servers"
    CONTROL_M_SERVER_INFOS = f"{__name__}.cache.controlm.server.infos"


class CtmCacheManagerState (Enum):
    UNKNOWN: str = 'UNKNOWN',
    PROGRESS: str = 'PROGRESS',
    FAULT: str = 'FAULT',
    COMPLETE: str = 'COMPLETE'


class CtmCacheManager (ABC):

    def __init__(self,
                 identifier: str = f"{__name__}_{uuid4()}",
                 cache: CacheStore = None,
                 task_runner: TaskRunner = None,
                 logger: Logger = None):
        self._identifier: str = identifier
        self._logger = logger or create_console_logger(__name__)
        if cache is None:
            self._logger.warning('Cache argument is None. Creating new cache instance.')
        self._cache: CacheStore = cache or CacheStore()
        self._task_runner: TaskRunner = task_runner or TaskRunner()
        self._cache_lock: Lock = Lock()
        self._cache_process_lock: Lock = Lock()
        self._cache_task: Optional[Future] = None
        self._logger.info(f"Cache manager '{self.identifier}' initialized.")

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
    def cache_state(self) -> CtmCacheManagerState:
        return self._cache.get_item(CtmCacheManagerKeys.CACHE_STATE) or CtmCacheManagerState.UNKNOWN

    @property
    def cache_error(self) -> any:
        return self._cache.get_item(CtmCacheManagerKeys.CACHE_ERROR)

    @property
    def cache_timestamp(self) -> Optional[datetime]:
        if self.is_cache_ready:
            return self._cache.get_item(CtmCacheManagerKeys.CACHE_TIMESTAMP)
        return None

    @property
    def cache_populate_duration(self) -> Optional[float]:
        if self.is_cache_ready:
            return self._cache.get_item(CtmCacheManagerKeys.CACHE_POPULATE_DURATION)
        return None

    @property
    def is_cache_corrupt(self) -> bool:
        return self.cache_error is not None

    @property
    def is_cache_ready(self) -> bool:
        return not self.is_cache_corrupt and self.cache_state == CtmCacheManagerState.COMPLETE

    @property
    def is_populating_cache(self) -> bool:
        return self.cache_state == CtmCacheManagerState.PROGRESS

    def set_caching_in_progress(self, error: any = None):
        self.cache.set_items_from_dict({
            CtmCacheManagerKeys.CACHE_ERROR: error,
            CtmCacheManagerKeys.CACHE_STATE: CtmCacheManagerState.PROGRESS
        })
        self.logger.info(f"[{self.identifier}] Caching has started.")

    def set_caching_complete(self,
                             def_table: CtmDefTable,
                             data_center_keys: [str],
                             data_center_aggregates: dict) -> None:
        mapped = map_server_infos_from_ctm_model(def_table, self.logger)
        self.cache.set_items_from_dict({
            CtmCacheManagerKeys.CONTROL_M_ALL_FOLDERS: def_table,
            CtmCacheManagerKeys.CONTROL_M_ALL_FOLDERS_DTO: mapped,
            CtmCacheManagerKeys.CONTROL_M_SERVERS: data_center_keys,
            CtmCacheManagerKeys.CONTROL_M_SERVER_INFOS: data_center_aggregates,
            CtmCacheManagerKeys.CACHE_STATE: CtmCacheManagerState.COMPLETE,
        })
        self.logger.info(f"[{self.identifier}] Caching complete.")

    def set_caching_failed(self, error: any):
        self.cache.set_items_from_dict({
            CtmCacheManagerKeys.CACHE_ERROR: error,
            CtmCacheManagerKeys.CACHE_STATE: CtmCacheManagerState.FAULT
        })
        self.logger.error(f"[{self.identifier}] Caching has failed: {error}.")

    def set_caching_stats(self, start: datetime, end: datetime) -> None:
        second_diff = (end - start).total_seconds()
        self.cache.set_items_from_dict({
            CtmCacheManagerKeys.CACHE_POPULATE_START: start,
            CtmCacheManagerKeys.CACHE_POPULATE_END: end,
            CtmCacheManagerKeys.CACHE_TIMESTAMP: end,
            CtmCacheManagerKeys.CACHE_POPULATE_DURATION: second_diff
        })
        self.logger.info(f"Caching started at [{start}], finished at [{end}]. "
                         f"Duration = {second_diff} seconds")

    def populate_cache(self, *args, **kwargs):
        self.logger.debug(f"[{self.identifier}] Populate cache invoked with *args={args} and **kwargs={kwargs}")
        task_meta: TaskMetaData = kwargs['task_meta']
        task_meta.invalidate_thread()
        with self._cache_process_lock:
            if self.is_populating_cache:
                self.logger.warning(f"[{self.identifier}] Already running cache initialization. "
                                    f"Subsequent calls will be ignored.")
                return
            self.set_caching_in_progress()
            date_start = datetime.now()
            parser = CtmXmlParser()
            try:
                def_table = parser.parse_xml('./resources/PROD_CTM.all.xml')
                data_center_keys = []
                data_center_aggregates = {}
                self.set_caching_complete(def_table, data_center_keys, data_center_aggregates)
            except BaseException as ex:
                self.set_caching_failed(ex)
            finally:
                date_end = datetime.now()
                self.set_caching_stats(
                    start=date_start,
                    end=date_end
                )
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

    def get_cached_server_names(self) -> [str]:
        return self.cache.get_item(CtmCacheManagerKeys.CONTROL_M_SERVERS) if self.is_cache_ready else []

    def get_cached_server_infos_dto(self) -> Dict[str, DtoServerInfo]:
        return self.cache.get_item(CtmCacheManagerKeys.CONTROL_M_ALL_FOLDERS_DTO) if self.is_cache_ready else {}
