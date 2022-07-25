from abc import ABC
from uuid import uuid4
from logging import Logger
from typing import Dict, Optional
from threading import Lock
from corelib.logging.helpers import create_console_logger


class CacheStore (ABC):

    def __init__(self,
                 identifier: str = f"{__name__}_{uuid4()}",
                 logger: Logger = None):
        self._identifier: str = identifier
        self._lock: Lock = Lock()
        self._dict: Dict[str, any] = {}
        self._logger = logger or create_console_logger(__name__)
        self._logger.info(f"Cache store '{self.identifier}' initialized.")

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def cache_keys(self) -> [str]:
        return list(self._dict.keys())

    def get_item(self, key: str) -> Optional[any]:
        with self._lock:
            if key in self._dict:
                self.logger.debug(f"[{self.identifier}] Fetching cache item for key [{key}]...")
                return self._dict[key]
            self.logger.warning(f"[{self.identifier}] Cache item for key [{key}] not found.")
            return None

    def set_item(self, key: str, value: any) -> None:
        with self._lock:
            self._internal_set_item(key, value)

    def set_items_from_dict(self, items_dict: dict) -> None:
        self.set_items(**items_dict)

    def set_items(self, **kwargs) -> None:
        with self._lock:
            for key in kwargs:
                self._internal_set_item(key, kwargs[key])

    def set_multiples(self, keys: [str], values: [any]) -> None:
        if len(keys) != len(values):
            raise ValueError(f"[{self.identifier}] The number of keys ({len(keys)}) does not match the number of values ({len(values)}).")
        if len(keys) <= 0:
            return
        with self._lock:
            for idx, key in keys:
                value = values[idx]
                self._internal_set_item(key, value)

    def _internal_set_item(self, key: str, value: any) -> None:
        if value is None:
            if key in self._dict:
                self.logger.warning(f"[{self.identifier}] Deleting cache item for key [{key}]...")
                del self._dict[key]
            else:
                self.logger.debug(f"[{self.identifier}] Cache item for key [{key}] not found. Skipping deletion...")
        else:
            self.logger.warning(f"[{self.identifier}] Setting cache item for key [{key}] = {value}")
            self._dict[key] = value
