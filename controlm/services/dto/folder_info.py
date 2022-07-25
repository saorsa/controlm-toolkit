from abc import ABC
from logging import Logger
from typing import List, Optional, Tuple, Dict
from controlm.model import CtmDefTableItem, CtmSimpleFolder, CtmSmartFolder
from corelib.logging import create_console_logger
from uuid import uuid4
from .job_info import map_job_info_from_ctm_model, DtoJobInfo


class DtoFolderInfo(ABC):

    def __init__(self):
        self.is_smart: bool = False
        self.order_method: str = 'UNKNOWN'
        self.server: str = f"server-{uuid4()}"
        self.name: str = f"folder-{uuid4()}"
        self.node_id: Optional[str] = None
        self.application: Optional[str] = None
        self.sub_application: Optional[str] = None
        self.job_application_keys: List[str] = []
        self.job_sub_application_keys: List[str] = []
        self.jobs: List[DtoJobInfo] = []
        self.job_node_keys: List[str] = []
        self.job_nodes_map: Dict[str, str] = {}
        self.node_jobs_map: Dict[str, List[str]] = {}
        self.is_running_automatically: bool = False
        self.run_as: Optional[str] = None
        self.variables: List[Tuple[str, str]]

    @property
    def job_names(self) -> List[str]:
        return [j.job_name for j in self.jobs]


def map_folder_info_from_ctm_model(
        item_def: CtmDefTableItem,
        logger: Logger = None) -> DtoFolderInfo:
    logger = logger or create_console_logger(f"{__name__}.mapper")
    if isinstance(item_def, CtmSimpleFolder) or isinstance(item_def, CtmSmartFolder):
        result = DtoFolderInfo()
        result.is_smart = item_def.is_smart
        result.server = item_def.data_center
        result.name = item_def.folder_name
        result.order_method = item_def.folder_order_method
        result.is_running_automatically = item_def.folder_order_method == 'SYSTEM'
        if isinstance(item_def, CtmSmartFolder):
            result.application = item_def.application
            result.sub_application = item_def.sub_application
            result.variables = [(v.name, v.value) for v in item_def.variables]
            result.run_as = item_def.run_as
            result.node_id = item_def.node_id
            if item_def.node_id:
                print(item_def)
        for job_item in item_def.jobs:
            dto_job = map_job_info_from_ctm_model(job_item, logger=logger)
            if dto_job.application and dto_job.application not in result.job_application_keys:
                result.job_application_keys.append(dto_job.application)
            if dto_job.sub_application and dto_job.sub_application not in result.job_sub_application_keys:
                result.job_sub_application_keys.append(dto_job.sub_application)
            if dto_job.node_id and dto_job.node_id not in result.job_node_keys:
                result.job_node_keys.append(dto_job.node_id)
            if dto_job.node_id:
                if dto_job.job_name not in result.job_nodes_map:
                    result.job_nodes_map[dto_job.job_name] = job_item.node_id
                if dto_job.node_id not in result.node_jobs_map:
                    result.node_jobs_map[dto_job.node_id] = [job_item.job_name]
                else:
                    result.node_jobs_map[dto_job.node_id].append(job_item.job_name)
            result.jobs.append(dto_job)
        return result
    raise ValueError(
        f"Unsupported item {item_def.tag_name}"
    )
