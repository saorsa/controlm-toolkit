import os.path
from logging import Logger
from typing import Final, Optional
from lxml import etree
from common.logging import create_console_logger
from model.ctm_def_table import CtmDefTable
from model.ctm_def_table_item import CtmDefTableItem
from model.ctm_simple_folder import CtmSimpleFolder
from model.ctm_smart_folder import CtmSmartFolder
from model.ctm_var_data import CtmVarData
from model.ctm_tag_data import CtmTagData
from exceptions import CtmXmlParserException

SUPPORTED_DEF_TABLE_SIMPLE_ITEM_TYPES: Final = [
    'FOLDER',
    # 'SCHED_TABLE',
    # 'TABLE'
]

SUPPORTED_DEF_TABLE_SMART_ITEM_TYPES: Final = [
    'SMART_FOLDER',
    # 'SMART_TABLE',
    # 'SCHED_GROUP'
]

SUPPORTED_DEF_TABLE_ITEM_TYPES: Final = SUPPORTED_DEF_TABLE_SIMPLE_ITEM_TYPES + SUPPORTED_DEF_TABLE_SMART_ITEM_TYPES


class CtmXmlParser:

    def __init__(self,
                 xsd_path: str = './resources/Folder.xsd',
                 logger: Logger = None):
        self._xsd_path: str = xsd_path
        self._logger: Logger = logger or create_console_logger(self.__class__.__name__)
        self._validate_xsd_path()

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def xsd_path(self) -> str:
        return self._xsd_path

    def validate_xml(self, xml_path: str) -> bool:
        """
        :param xml_path: XML file to be validated.
        :return: True, if the XML file conforms to the XSD schema, false otherwise.
        """
        self.logger.debug(f'Validating source XML file {xml_path} against XSD schema {self.xsd_path}')
        xmlschema_doc = etree.parse(self.xsd_path)
        self.logger.debug(f'XSD schema at path {self.xsd_path} loaded. {xmlschema_doc}')
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml_doc = etree.parse(xml_path)
        self.logger.debug(f'XML document at path {xml_path} loaded. {xml_doc}')
        result = xmlschema.validate(xml_doc)
        if not result:
            self.logger.warning(f'XML file at path {xml_path} failed validation against XSD '
                                f'schema at path{self.xsd_path}')
        return result

    def parse_xml(self, xml_file: str) -> CtmDefTable:
        if not os.path.exists(xml_file):
            self.logger.fatal(f"XML file at path '{xml_file}' could not be found.")
            raise CtmXmlParserException(
                f"XML file at path '{xml_file}' could not be found."
            )
        if not self.validate_xml(xml_file):
            self.logger.fatal(f"XML file at path '{xml_file}' does not conform to schema at path '{self.xsd_path}'.")
            raise CtmXmlParserException(
                f"XML file at path '{xml_file}' does not conform to schema at path '{self.xsd_path}'."
            )

        self.logger.info(f"XML at path '{xml_file}' conforms to schema at path '{self.xsd_path}'.")
        result = etree.parse(xml_file)
        root = result.getroot()
        self.logger.debug(f"Root element tag is {root.tag}. Parsing definition table...")
        return self.parse_def_table(root)

    def parse_def_table(self, xml_element: etree.ElementTree) -> CtmDefTable:
        result = CtmDefTable()
        for x in xml_element:
            if x.tag in SUPPORTED_DEF_TABLE_ITEM_TYPES:
                child = self.parse_def_table_item(x)
                self.logger.info(f"Processed {child}")
                result.items.append(child)
            else:
                raise CtmXmlParserException(
                    f"Unsupported DEF_TABLE child element {x.tag}"
                )
        return result

    def parse_def_table_item(self, xml_element: etree.ElementTree) -> CtmDefTableItem:
        if xml_element.tag in SUPPORTED_DEF_TABLE_SIMPLE_ITEM_TYPES:
            return self.parse_simple_folder(xml_element)
        elif xml_element.tag in SUPPORTED_DEF_TABLE_SMART_ITEM_TYPES:
            return self.parse_smart_folder(xml_element)
        self.logger.warning(
            f"Processing non-folder item of type '{xml_element.tag}'..."
        )
        return CtmDefTableItem(xml_element.tag)

    def parse_attribute_value_or_default(self, xml_element: etree.ElementTree, attr_key: str) -> Optional[str]:
        if attr_key in xml_element.attrib:
            return xml_element.attrib[attr_key]
        self.logger.warning(
            f"XML element '{xml_element.tag}' does not have an attribute'{attr_key}'. Returning default value of None."
        )
        return None

    def parse_simple_folder(self, xml_element: etree.ElementTree) -> CtmDefTableItem:
        data_center = self.parse_attribute_value_or_default(xml_element, 'DATACENTER')
        folder_name = self.parse_attribute_value_or_default(xml_element, 'FOLDER_NAME')
        self.logger.info(f"Parsing simple folder {xml_element.tag}. Server = {data_center}, Folder = {folder_name}")
        if xml_element.tag not in SUPPORTED_DEF_TABLE_SIMPLE_ITEM_TYPES:
            raise CtmXmlParserException(
                f"The XML element {xml_element.tag} is not a simple folder type."
            )
        result = CtmSimpleFolder(xml_element.tag)
        result.data_center = data_center
        result.folder_name = folder_name
        return result

    def parse_smart_folder(self, xml_element: etree.ElementTree) -> CtmDefTableItem:
        data_center = self.parse_attribute_value_or_default(xml_element, 'DATACENTER')
        folder_name = self.parse_attribute_value_or_default(xml_element, 'FOLDER_NAME')
        self.logger.info(f"Parsing smart folder {xml_element.tag}. Server = {data_center}, Folder = {folder_name}")
        if xml_element.tag not in SUPPORTED_DEF_TABLE_SMART_ITEM_TYPES:
            raise CtmXmlParserException(
                f"The XML element {xml_element.tag} is not a smart folder type."
            )
        result = CtmSmartFolder(xml_element.tag)
        result.data_center = data_center
        result.folder_name = folder_name
        result.description = self.parse_attribute_value_or_default(xml_element, 'DESCRIPTION')
        result.application = self.parse_attribute_value_or_default(xml_element, 'APPLICATION')
        result.sub_application = self.parse_attribute_value_or_default(xml_element, 'SUB_APPLICATION')
        result.mem_name = self.parse_attribute_value_or_default(xml_element, 'MEMNAME')
        result.job_name = self.parse_attribute_value_or_default(xml_element, 'JOBNAME')
        result.node_id = self.parse_attribute_value_or_default(xml_element, 'NODEID')
        result.priority = self.parse_attribute_value_or_default(xml_element, 'PRIORITY')
        result.cyclic = self.parse_attribute_value_or_default(xml_element, 'CYCLIC')
        result.run_as = self.parse_attribute_value_or_default(xml_element, 'RUN_AS')
        result.owner = self.parse_attribute_value_or_default(xml_element, 'OWNER')
        result.author = self.parse_attribute_value_or_default(xml_element, 'AUTHOR')
        result.created_by = self.parse_attribute_value_or_default(xml_element, 'CREATED BY')
        for child in xml_element:
            if child.tag == 'VARIABLE':
                var_data = self.parse_var_data(child)
                self.logger.debug(f"Processed child variable {child.tag}: {var_data.__dict__}")
                result.variables.append(var_data)
            if child.tag == 'RULE_BASED_CALENDAR':
                tag_data = self.parse_tag_data(child)
                self.logger.debug(f"Processed child rule based calendar {child.tag}: {tag_data.__dict__}")
                result.rule_based_calendars.append(tag_data)
            else:
                self.logger.warning(f"Unsupported SMART_FOLDER child element {child.tag}")
        return result

    def parse_var_data(self, xml_element: etree.ElementTree) -> CtmVarData:
        if xml_element.tag != 'VARIABLE':
            raise CtmXmlParserException(
                f"The XML element {xml_element.tag} is not a Control-M variable."
            )
        result = CtmVarData()
        result.name = self.parse_attribute_value_or_default(xml_element, "NAME")
        result.value = self.parse_attribute_value_or_default(xml_element, "VALUE")
        return result

    def parse_tag_data(self, xml_element: etree.ElementTree) -> CtmTagData:
        if xml_element.tag != 'RULE_BASED_CALENDAR':
            raise CtmXmlParserException(
                f"The XML element {xml_element.tag} is not a Control-M variable."
            )

        tag_name = self.parse_attribute_value_or_default(xml_element, 'TAG_NAME')
        result = CtmTagData(tag_name or xml_element.tag)
        result.name = self.parse_attribute_value_or_default(xml_element, "NAME")
        result.max_wait = self.parse_attribute_value_or_default(xml_element, "MAXWAIT")
        result.days_and_or = self.parse_attribute_value_or_default(xml_element, "DAYS_AND_OR")
        result.jan = self.parse_attribute_value_or_default(xml_element, "JAN")
        result.feb = self.parse_attribute_value_or_default(xml_element, "FEB")
        result.mar = self.parse_attribute_value_or_default(xml_element, "MAR")
        result.apr = self.parse_attribute_value_or_default(xml_element, "APR")
        result.may = self.parse_attribute_value_or_default(xml_element, "MAY")
        result.jun = self.parse_attribute_value_or_default(xml_element, "JUN")
        result.jul = self.parse_attribute_value_or_default(xml_element, "JUL")
        result.aug = self.parse_attribute_value_or_default(xml_element, "AUG")
        result.sep = self.parse_attribute_value_or_default(xml_element, "SEP")
        result.oct = self.parse_attribute_value_or_default(xml_element, "OCT")
        result.nov = self.parse_attribute_value_or_default(xml_element, "NOV")
        result.dec = self.parse_attribute_value_or_default(xml_element, "DEC")
        result.days_cal = self.parse_attribute_value_or_default(xml_element, "DAYSCAL")
        result.weeks_cal = self.parse_attribute_value_or_default(xml_element, "WEEKSCAL")
        result.conf_cal = self.parse_attribute_value_or_default(xml_element, "CONFCAL")
        result.shift = self.parse_attribute_value_or_default(xml_element, "SHIFT")
        result.shift_num = self.parse_attribute_value_or_default(xml_element, "SHIFTNUM")
        result.retro = self.parse_attribute_value_or_default(xml_element, "RETRO")
        result.date = self.parse_attribute_value_or_default(xml_element, "DATE")
        result.days = self.parse_attribute_value_or_default(xml_element, "DAYS")
        result.weekdays = self.parse_attribute_value_or_default(xml_element, "WEEKDAYS")
        result.weekdays = self.parse_attribute_value_or_default(xml_element, "WEEKDAYS")
        result.active_from = self.parse_attribute_value_or_default(xml_element, "ACTIVE_FROM")
        result.tags_active_from = self.parse_attribute_value_or_default(xml_element, "TAGS_ACTIVE_FROM")
        result.active_till = self.parse_attribute_value_or_default(xml_element, "ACTIVE_TILL")
        result.tags_active_till = self.parse_attribute_value_or_default(xml_element, "TAGS_ACTIVE_TILL")
        result.level = self.parse_attribute_value_or_default(xml_element, "LEVEL")
        return result

    def _validate_xsd_path(self) -> None:
        if not os.path.exists(self._xsd_path):
            self.logger.fatal(f"XSD schema at path '{self.xsd_path}' could not be found/")
            raise CtmXmlParserException(
                f"XSD schema at path '{self.xsd_path}' could not be found."
            )
        self.logger.debug(f"XSD schema at path '{self.xsd_path}' found.")


parser = CtmXmlParser()
tree = parser.parse_xml('./resources/PROD_CTM.all.xml')
print(tree)
