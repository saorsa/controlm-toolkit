from abc import ABC
from logging import Logger
from typing import List, Dict
from controlm.model import CtmDefTable, CtmSimpleFolder, CtmSmartFolder
from corelib.logging import create_console_logger
from uuid import uuid4
from .folder_info import map_folder_info_from_ctm_model, DtoFolderInfo


class DtoServerInfo(ABC):

    def __init__(self):
        self.name = f"server-{uuid4()}"
        self.application_keys: List[str] = []
        self.sub_application_keys: List[str] = []
        self.folders: List[DtoFolderInfo] = []


def map_server_infos_from_ctm_model(
        ctm_def: CtmDefTable,
        logger: Logger = None) -> Dict[str, DtoServerInfo]:
    logger = logger or create_console_logger(f"{__name__}.mapper")
    results: Dict[str, DtoServerInfo] = {}
    for item in ctm_def.items:
        if isinstance(item, CtmSimpleFolder) or isinstance(item, CtmSmartFolder):
            dto_folder = map_folder_info_from_ctm_model(item, logger=logger)
            if dto_folder.server not in results:
                res = DtoServerInfo()
                res.name = dto_folder.server
                res.folders.append(dto_folder)
                if dto_folder.application and dto_folder.application not in res.application_keys:
                    res.application_keys.append(dto_folder.application)
                if dto_folder.sub_application and dto_folder.sub_application not in res.sub_application_keys:
                    res.sub_application_keys.append(dto_folder.sub_application)
                results[dto_folder.server] = res
        raise ValueError(
            f"Unsupported item {item.tag_name}"
        )
    return results
