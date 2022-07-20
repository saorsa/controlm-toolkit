from .ctm_base_object import CtmBaseObject
from .ctm_def_table_item import CtmDefTableItem


class CtmDefTable (CtmBaseObject):

    def __init__(self):
        super().__init__('DEFTABLE')
        self.items: [CtmDefTableItem] = []
