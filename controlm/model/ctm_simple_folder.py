from typing import Optional, List
from .ctm_job_data import CtmJobData
from .ctm_def_table_item import CtmDefTableItem


class CtmSimpleFolder (CtmDefTableItem):

    def __init__(self, tag_name: str):
        super().__init__(tag_name)
        self.folder_name: Optional[str] = None
        self.jobs: List[CtmJobData] = []

    def __str__(self) -> str:
        return f"SERVER = {self.data_center}, FOLDER = {self.folder_name} SMART = {self.is_smart}"
