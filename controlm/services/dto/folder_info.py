from abc import ABC
from logging import Logger
from typing import List, Optional
from controlm.model import CtmDefTableItem, CtmSimpleFolder, CtmSmartFolder
from corelib.logging import create_console_logger
from uuid import uuid4


class DtoFolderInfo(ABC):

    def __init__(self):
        self.is_smart: bool = False
        self.server: str = f"server-{uuid4()}"
        self.name: str = f"folder-{uuid4()}"
        self.application: Optional[str] = None
        self.sub_application: Optional[str] = None
        self.job_keys: List[str] = []


def map_folder_info_from_ctm_model(
        item_def: CtmDefTableItem,
        logger: Logger = None) -> DtoFolderInfo:
    logger = logger or create_console_logger(f"{__name__}.mapper")
    if isinstance(item_def, CtmSimpleFolder) or isinstance(item_def, CtmSmartFolder):
        result = DtoFolderInfo()
        result.server = item_def.data_center
        result.name = item_def.folder_name
        if isinstance(item_def, CtmSmartFolder):
            result.application = item_def.application
            result.sub_application = item_def.sub_application
        return result
    raise ValueError(
        f"Unsupported item {item_def.tag_name}"
    )
