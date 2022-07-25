from typing import Optional
from .ctm_base_object import CtmBaseObject


class CtmDefTableItem (CtmBaseObject):

    def __init__(self, tag_name: str):
        super().__init__(tag_name)
        self.data_center: Optional[str] = None

    @property
    def is_smart(self) -> bool:
        return False

    def __str__(self) -> str:
        return f"SERVER = {self.data_center}, SMART = {self.is_smart}"
