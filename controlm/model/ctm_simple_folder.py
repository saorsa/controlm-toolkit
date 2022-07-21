from .ctm_def_table_item import CtmDefTableItem


class CtmSimpleFolder (CtmDefTableItem):

    def __init__(self, tag_name: str):
        super().__init__(tag_name)
