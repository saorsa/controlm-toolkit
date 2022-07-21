from abc import ABC
from logging import Logger
from typing import Dict, Optional
from common.logging.helpers import create_console_logger
from controlm.model import CtmDefTable


class CtmRestCache (ABC):

    def __init__(self, logger: Logger = None):
        self._dict: Dict[str, any] = {}
        self._logger = logger or create_console_logger()

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def cache_keys(self) -> [str]:
        return list(self._dict.keys())

    def get_cache_item(self, key: str) -> Optional[any]:
        if key in self._dict:
            self.logger.debug(f"Fetching cache item for key [{key}]...")
            return self._dict[key]
        self.logger.warning(f"Cache item for key [{key}] not found.")
        return None

    def set_cache_item(self, key: str, value: any) -> None:
        if value is None:
            existing = self.get_cache_item(key)
            if existing:
                self.logger.warning(f"Deleting cache item for key [{key}]...")
                del self._dict[key]
        else:
            self.logger.warning(f"Setting cache item for key [{key}]...")
            self._dict[key] = value

    @property
    def cache_state(self) -> str:
        return self.get_cache_item('CACHE_STATE') or 'unknown'

    @property
    def cache_error(self) -> Optional[any]:
        return self.get_cache_item('CACHE_ERROR')

    def set_cache_state_error(self, error: any) -> None:
        if error:
            self.set_cache_item('CACHE_STATE', 'fault')
            self.set_cache_item('CACHE_ERROR', error)
        else:
            self.set_cache_item('CACHE_STATE', 'unknown')
            self.set_cache_item('CACHE_ERROR', None)

    def set_cache_state_progress(self) -> None:
        self.set_cache_item('CACHE_STATE', 'progress')

    def set_cache_state_complete(self,
                                 def_table: CtmDefTable,
                                 data_center_names: [str],
                                 data_center_stats: {}) -> None:
        self.set_cache_item('ALL_FOLDERS', def_table)
        self.set_cache_item('DATA_CENTER_NAMES', data_center_names)
        self.set_cache_item('DATA_CENTER_STATS', data_center_stats)
        self.set_cache_item('CACHE_STATE', 'complete')


sharedCache: CtmRestCache = CtmRestCache()
