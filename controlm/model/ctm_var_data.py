from typing import Optional
from .ctm_base_object import CtmBaseObject


class CtmVarData (CtmBaseObject):

    def __init__(self):
        super().__init__('VARIABLE')
        self.name: Optional[str] = None
        self.value: Optional[str] = None

    def __str__(self) -> str:
        return f"VARIABLE = {self.name}, VALUE = {self.value}"
