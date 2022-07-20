from typing import Optional
from .ctm_def_table_item import CtmDefTableItem
from .ctm_var_data import CtmVarData
from .ctm_tag_data import CtmTagData

class CtmSmartFolder (CtmDefTableItem):

    def __init__(self, tag_name: str):
        super().__init__(tag_name)
        self.description: Optional[str] = None
        self.application: Optional[str] = None
        self.sub_application: Optional[str] = None
        self.mem_name: Optional[str] = None
        self.job_name: Optional[str] = None
        self.created_by: Optional[str] = None
        self.owner: Optional[str] = None
        self.author: Optional[str] = None
        self.run_as: Optional[str] = None
        self.task_type: Optional[str] = None
        self.cyclic: Optional[str] = None
        self.priority: Optional[str] = None
        self.node_id: Optional[str] = None
        self.variables: [CtmVarData] = []
        self.rule_based_calendars: [CtmTagData] = []

    @property
    def is_smart(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"{super().__str__()}, APPLICATION = {self.application}, SUB-APPLICATION = {self.sub_application}, " \
               f"MEM NAME = {self.mem_name}, JOB NAME = {self.job_name}, CREATED BY = {self.created_by}, " \
               f"OWNER = {self.owner}, AUTHOR = {self.author}, RUN AS = {self.run_as}, HOST = {self.node_id}, " \
               f"IS CYCLIC = {self.cyclic}, PRIORITY = {self.priority}"
