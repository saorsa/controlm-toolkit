from abc import ABC
from typing import Optional
from uuid import uuid4
from logging import Logger

from controlm.services.dto import DtoServerInfo
from corelib.logging import create_console_logger
from controlm.services import CtmCacheManager


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

    def get_server_info_or_default(self, server_name: str) -> Optional[DtoServerInfo]:
        stats = self.get_server_aggregate_stats()
        if server_name in stats:
            return DtoServerInfo(
                name=server_name,
                application_keys=stats[server_name]['applications']
            )
        return None
