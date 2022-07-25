import logging
from abc import ABC
from logging import Logger
from typing import List, Dict
from controlm.model import CtmDefTable, CtmSimpleFolder, CtmSmartFolder
from corelib.logging import create_console_logger
from uuid import uuid4
from .folder_info import map_folder_info_from_ctm_model, DtoFolderInfo
from .node_info import DtoNodeInfo


class DtoServerInfo(ABC):

    def __init__(self):
        self.name = f"server-{uuid4()}"
        self.application_keys: List[str] = []
        self.sub_application_keys: List[str] = []
        self.node_infos: Dict[str, DtoNodeInfo] = {}
        self.folders: List[DtoFolderInfo] = []

    @property
    def folder_names(self) -> List[str]:
        return [folder.name for folder in self.folders]


def map_server_infos_from_ctm_model(
        ctm_def: CtmDefTable,
        logger: Logger = None) -> Dict[str, DtoServerInfo]:

    logger = logger or create_console_logger(
        f"{__name__}.mapper", min_log_level=logging.WARNING, console_log_level=logging.WARNING)
    results: Dict[str, DtoServerInfo] = {}
    for item in ctm_def.items:
        if isinstance(item, CtmSimpleFolder) or isinstance(item, CtmSmartFolder):
            dto_folder = map_folder_info_from_ctm_model(item, logger=logger)
            if dto_folder.server not in results:
                logger.debug(f"Mapping server DTO '{dto_folder.server}'...")
                info = DtoServerInfo()
                info.name = dto_folder.server
                results[dto_folder.server] = info
            else:
                info = results[dto_folder.server]

            info.folders.append(dto_folder)

            if dto_folder.application and dto_folder.application not in info.application_keys:
                info.application_keys.append(dto_folder.application)

            if dto_folder.sub_application and dto_folder.sub_application not in info.sub_application_keys:
                info.sub_application_keys.append(dto_folder.sub_application)

            if dto_folder.node_id:
                if dto_folder.node_id not in info.node_infos:
                    node_info = DtoNodeInfo()
                    info.node_infos[dto_folder.node_id] = node_info
                else:
                    node_info = info.node_infos[dto_folder.node_id]
                node_info.append_folder_key_if_needed(dto_folder.name)

            for k in dto_folder.job_application_keys:
                if k not in info.application_keys:
                    info.application_keys.append(k)

            for k in dto_folder.job_sub_application_keys:
                if k not in info.sub_application_keys:
                    info.sub_application_keys.append(k)

            for folder_node_id in dto_folder.node_jobs_map:
                if folder_node_id not in info.node_infos:
                    node_info = DtoNodeInfo()
                    info.node_infos[folder_node_id] = node_info
                else:
                    node_info = info.node_infos[folder_node_id]
                folder_node_jobs = dto_folder.node_jobs_map[folder_node_id]
                for j in folder_node_jobs:
                    node_info.append_folder_key_if_needed(dto_folder.name)
                    node_info.append_job_key_if_needed(dto_folder.name, j)
        else:
            logger.warning(f"Cannot map item ({item}). Tag '{item.tag_name}' is not supported. Skipping...")
    return results
