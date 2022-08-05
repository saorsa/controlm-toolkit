from abc import ABC
from typing import List, Optional
from .host_info import DtoHostInfo


class DtoNodeInfo(ABC):

    def __init__(self):
        self.hosts: List[DtoHostInfo] = []
        self.group: Optional[str] = None
        self.folders: List[str] = []
        self.jobs: List[str] = []

    def append_folder_key_if_needed(self, folder_name: str):
        if folder_name not in self.folders:
            self.folders.append(folder_name)

    def append_job_key_if_needed(self, folder_name: str, job_name: str):
        key = f"{folder_name}/{job_name}"
        if key not in self.jobs:
            self.jobs.append(key)
