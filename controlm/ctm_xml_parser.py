from logging import Logger
from typing import Final
from xml.etree import ElementTree
from common.logging import create_console_logger
from model.ctm_def_table import CtmDefTable
from model.ctm_def_table_item import CtmDefTableItem
from model.ctm_simple_folder import CtmSimpleFolder
from model.ctm_smart_folder import CtmSmartFolder
from exceptions import CtmXmlParserException

SUPPORTED_DEF_TABLE_SIMPLE_ITEM_TYPES: Final = [
    'FOLDER',
    'SCHED_TABLE',
    'TABLE'
]

SUPPORTED_DEF_TABLE_SMART_ITEM_TYPES: Final = [
    'SMART_FOLDER',
    'SMART_TABLE',
    'SCHED_GROUP'
]

SUPPORTED_DEF_TABLE_ITEM_TYPES: Final = SUPPORTED_DEF_TABLE_SIMPLE_ITEM_TYPES + SUPPORTED_DEF_TABLE_SMART_ITEM_TYPES


class CtmXmlParser:

    def __init__(self, logger: Logger = None):
        self._logger = logger or create_console_logger(self.__class__.__name__)

    @property
    def logger(self) -> Logger:
        return self._logger

    def parse_def_table(self, xml_file_path: str) -> CtmDefTable:
        self.logger.info(f"Parsing file {xml_file_path}")
        result = ElementTree.parse(xml_file_path)
        root = result.getroot()
        self.logger.debug(f"Root element tag is {root.tag}")
        result = CtmDefTable();
        for x in root:
            if x.tag in SUPPORTED_DEF_TABLE_ITEM_TYPES:
                child = self.parse_def_table_item(x)
                result.items.append(child)
            else:
                raise CtmXmlParserException(
                    f"Unsupported DEF_TABLE child element {x.tag}"
                )
        return result

    def parse_def_table_item(self, xml_element: ElementTree) -> CtmDefTableItem:
        self.logger.debug(f"Child element {xml_element.tag}")
        if xml_element.tag in SUPPORTED_DEF_TABLE_SIMPLE_ITEM_TYPES:
            return CtmSimpleFolder(xml_element.tag)
        elif xml_element.tag in SUPPORTED_DEF_TABLE_SMART_ITEM_TYPES:
            return CtmSmartFolder(xml_element.tag)
        return CtmDefTableItem(xml_element.tag)


parser = CtmXmlParser()
etree = parser.parse_def_table('./resources/PROD_CTM.all.xml')
print(etree)
