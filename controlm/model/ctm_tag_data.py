from typing import Optional
from .ctm_base_object import CtmBaseObject


class CtmTagData (CtmBaseObject):

    def __init__(self, tag_name: str):
        super().__init__(tag_name)
        self.name: Optional[str] = None
        self.max_wait: Optional[str] = None
        self.days_and_or: Optional[str] = None
        self.jan: Optional[str] = None
        self.feb: Optional[str] = None
        self.mar: Optional[str] = None
        self.apr: Optional[str] = None
        self.may: Optional[str] = None
        self.jun: Optional[str] = None
        self.jul: Optional[str] = None
        self.aug: Optional[str] = None
        self.sep: Optional[str] = None
        self.oct: Optional[str] = None
        self.nov: Optional[str] = None
        self.dec: Optional[str] = None
        self.days_cal: Optional[str] = None
        self.weeks_cal: Optional[str] = None
        self.conf_cal: Optional[str] = None
        self.shift: Optional[str] = None
        self.shift_num: Optional[str] = None
        self.retro: Optional[str] = None
        self.date: Optional[str] = None
        self.days: Optional[str] = None
        self.weekdays: Optional[str] = None
        self.active_from: Optional[str] = None
        self.tags_active_from: Optional[str] = None
        self.active_till: Optional[str] = None
        self.tags_active_till: Optional[str] = None
        self.level: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.tag_name} NAME = {self.name}, MAX WAIT = {self.max_wait}"
