from abc import ABC
from logging import Logger
from typing import List, Optional, Tuple
from controlm.model import CtmJobData
from corelib.logging import create_console_logger


class DtoJobInfo(ABC):

    def __init__(self):
        self.job_name: Optional[str] = None
        self.mem_name: Optional[str] = None
        self.node_id: Optional[str] = None
        self.application: Optional[str] = None
        self.sub_application: Optional[str] = None
        self.group: Optional[str] = None
        self.description: Optional[str] = None
        self.is_current_version: Optional[str] = None
        self.days: Optional[str] = None
        self.is_running_automatically: bool = False
        self.group: Optional[str] = None
        self.jobs_in_group: Optional[str] = None
        self.parent_table: Optional[str] = None
        self.parent_folder: Optional[str] = None
        self.task_type: Optional[str] = None
        self.is_run_as_dummy: bool = False
        self.variables: List[Tuple[str, str]]


def map_job_info_from_ctm_model(
        item_def: CtmJobData,
        logger: Logger = None) -> DtoJobInfo:
    logger = logger or create_console_logger(f"{__name__}.mapper")
    result = DtoJobInfo()
    result.application = item_def.application
    result.sub_application = item_def.sub_application
    result.node_id = item_def.node_id
    result.job_name = item_def.job_name
    result.mem_name = item_def.mem_name
    result.group = item_def.group
    result.description = item_def.description
    result.is_current_version = item_def.is_current_version
    result.days = item_def.days
    result.is_running_automatically = item_def.days is not None
    result.variables = [(v.name, v.value) for v in item_def.variables]
    result.group = item_def.group
    result.jobs_in_group = item_def.jobs_in_group
    result.parent_table = item_def.parent_table
    result.parent_folder = item_def.parent_folder
    result.task_type = item_def.task_type
    result.is_run_as_dummy = item_def.task_type == 'Dummy'
    logger.debug(f"Mapped job {item_def.job_name}.")
    return result
