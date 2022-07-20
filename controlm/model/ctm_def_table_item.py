from .ctm_base_object import CtmBaseObject


class CtmDefTableItem (CtmBaseObject):

    def __init__(self, tag_name: str):
        super().__init__(tag_name)
