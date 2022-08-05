from abc import ABC
from uuid import uuid4
from logging import Logger
from typing import Dict, Optional, List
from controlm.services.dto.node_info import DtoNodeInfo
from controlm.services.dto.host_info import DtoHostInfo
from corelib.logging import create_console_logger
from controlm.services import CtmCacheManager
from controlm.services.dto import DtoServerInfo, DtoFolderInfo


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

    def fetch_server_names(self) -> List[str]:
        return self.cache_manager.get_cached_server_names()

    def fetch_server_aggregate_stats(self) -> Dict[str, DtoServerInfo]:
        return self.cache_manager.get_cached_server_infos_dto()

    def fetch_server_info_or_default(self, server_name: str) -> Optional[DtoServerInfo]:
        stats = self.fetch_server_aggregate_stats()
        if server_name in stats:
            return stats[server_name]
        return None

    def fetch_server_info_or_die(self, server_name: str) -> DtoServerInfo:
        stats = self.fetch_server_aggregate_stats()
        if server_name in stats:
            return stats[server_name]
        raise NameError(f"Server '{server_name}' not found.")

    def fetch_folders(self,
                      server_name: str,
                      folder_order_methods: List[Optional[str]] = None,
                      folder_node_ids: List[str] = None) -> List[DtoFolderInfo]:
        server_info = self.fetch_server_info_or_die(server_name)
        results = server_info.folders

        if folder_order_methods and len(folder_order_methods):
            c_before = len(results)
            results = list(filter(lambda folder: folder.order_method in folder_order_methods, results))
            c_after = len(results)
            self.logger.warning(f"[{self.identifier}] fetching folders. Original count = {c_before}. "
                                f"Filtering by order methods ({folder_order_methods}) count = {c_after}")

        if folder_node_ids and len(folder_node_ids):
            c_before = len(results)
            results = list(filter(
                lambda folder: folder.node_id in folder_node_ids or bool(
                    set(folder_node_ids) & set(folder.job_node_keys)
                ), results))
            c_after = len(results)
            self.logger.warning(f"[{self.identifier}] fetching folders. Original count = {c_before}. "
                                f"Filtering by nodes ({folder_node_ids}) count = {c_after}")
        return results

    def fetch_folder_or_default(self, server_name: str, folder_name: str) -> Optional[DtoFolderInfo]:
        server_info = self.fetch_server_info_or_default(server_name)
        if server_info:
            results = list(filter(lambda folder: folder.folder_name == folder_name, server_info.folders))
            if len(results) > 1:
                self.logger.warning(f"Server '{server_name}' hosts {len(results)} folders with name '{folder_name}'. "
                                    f"This is not expected")
            return results[0] if len(results) else None
        return None

    def fetch_folder_or_die(self, server_name: str, folder_name: str) -> Optional[DtoFolderInfo]:
        server_info = self.fetch_server_info_or_default(server_name)
        if server_info:
            results = list(filter(lambda folder: folder.folder_name == folder_name, server_info.folders))
            if len(results):
                if len(results) > 1:
                    raise NameError(f"Server '{server_name}' hosts {len(results)} folders with name '{folder_name}'. "
                                    f"This is not expected")
                return results[0]
            raise NameError(f"Folder '{folder_name}' not found.")
        raise NameError(f"Server '{server_name}' not found.")

    def fetch_node_names(self, server_name: str) -> List[str]:
        server_info = self.fetch_server_info_or_die(server_name)
        node_keys = list(server_info.node_infos.keys())
        return node_keys

    def fetch_node_or_default(self, server_name: str, host: str) -> Optional[DtoNodeInfo]:
        server_info = self.fetch_server_info_or_die(server_name)
        if server_info:
            return server_info.node_infos[host] if host in server_info.node_infos else None
        return None

    def fetch_node_or_die(self, server_name: str, host: str) -> Optional[DtoNodeInfo]:
        server_info = self.fetch_server_info_or_die(server_name)
        if server_info:
            if host in server_info.node_infos:
                return server_info.node_infos[host]
            raise NameError(f"Host '{host}' not found.")
        raise NameError(f"Server '{server_name}' not found.")

    def fetch_node_stats(self, server_name: str) -> dict:
        server_info = self.fetch_server_info_or_die(server_name)
        node_keys = server_info.node_infos.keys()
        result: dict = {}
        for node_id in node_keys:
            active = self.fetch_folders(server_name, folder_order_methods=['SYSTEM'], folder_node_ids=[node_id])
            disabled = self.fetch_folders(server_name, folder_order_methods=[None], folder_node_ids=[node_id])
            result[node_id] = {
                'activeCount': len(active),
                'active': [f.name for f in active],
                'disabledCount': len(disabled),
                'disabled': [f.name for f in disabled],
            }
        return result

    def fetch_host_or_default(self, server_name: str, host_name: str) -> Optional[DtoHostInfo]:
        hosts = self.cache_manager.get_cached_host_infos_dto()
        for h in hosts:
            if h.server == server_name and h.host == host_name:
                return h
        return None

    def fetch_hosts(self, server_name: str, node_group: str = None) -> List[DtoHostInfo]:
        hosts = self.cache_manager.get_cached_host_infos_dto()
        results: List[DtoHostInfo] = []
        for h in hosts:
            if h.server == server_name and (node_group is None or h.group == node_group):
                results.append(h)
        return results
