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
from model.ctm_job_data import CtmJobData
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
        self.logger.debug(
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
            elif child.tag == 'RULE_BASED_CALENDAR':
                tag_data = self.parse_tag_data(child)
                self.logger.debug(f"Processed child rule based calendar {child.tag}: {tag_data.__dict__}")
                result.rule_based_calendars.append(tag_data)
            elif child.tag == 'JOB':
                job_data = self.parse_job_data(child)
                self.logger.debug(f"Processed child job {child.tag}: {job_data.__dict__}")
                result.jobs.append(job_data)
            else:
                self.logger.debug(f"Unsupported SMART_FOLDER child element {child.tag}")
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

    def parse_job_data(self, xml_element: etree.ElementTree) -> CtmJobData:
        if xml_element.tag != 'JOB':
            raise CtmXmlParserException(
                f"The XML element {xml_element.tag} is not a Control-M variable."
            )
        result = CtmJobData(xml_element.tag)
        result.job_isn = self.parse_attribute_value_or_default(xml_element, "JOBISN")
        result.application = self.parse_attribute_value_or_default(xml_element, "APPLICATION")
        result.sub_application = self.parse_attribute_value_or_default(xml_element, "SUB_APPLICATION")
        result.group = self.parse_attribute_value_or_default(xml_element, "GROUP")
        result.mem_name = self.parse_attribute_value_or_default(xml_element, "MEMNAME")
        result.job_name = self.parse_attribute_value_or_default(xml_element, "JOBNAME")
        result.description = self.parse_attribute_value_or_default(xml_element, "DESCRIPTION")
        result.created_by = self.parse_attribute_value_or_default(xml_element, "CREATED_BY")
        result.author = self.parse_attribute_value_or_default(xml_element, "AUTHOR")
        result.run_as = self.parse_attribute_value_or_default(xml_element, "RUN_AS")
        result.owner = self.parse_attribute_value_or_default(xml_element, "OWNER")
        result.priority = self.parse_attribute_value_or_default(xml_element, "PRIORITY")
        result.critical = self.parse_attribute_value_or_default(xml_element, "CRITICAL")
        result.task_type = self.parse_attribute_value_or_default(xml_element, "TASKTYPE")
        result.cyclic = self.parse_attribute_value_or_default(xml_element, "CYCLIC")
        result.node_id = self.parse_attribute_value_or_default(xml_element, "NODEID")
        result.doc_lib = self.parse_attribute_value_or_default(xml_element, "DOCLIB")
        result.doc_mem = self.parse_attribute_value_or_default(xml_element, "DOCMEM")
        result.interval = self.parse_attribute_value_or_default(xml_element, "INTERVAL")
        result.override_path = self.parse_attribute_value_or_default(xml_element, "OVERRIDE_PATH")
        result.over_lib = self.parse_attribute_value_or_default(xml_element, "OVERLIB")
        result.mem_lib = self.parse_attribute_value_or_default(xml_element, "MEMLIB")
        result.cmd_line = self.parse_attribute_value_or_default(xml_element, "CMDLINE")
        result.confirm = self.parse_attribute_value_or_default(xml_element, "CONFIRM")
        result.days_cal = self.parse_attribute_value_or_default(xml_element, "DAYSCAL")
        result.weeks_cal = self.parse_attribute_value_or_default(xml_element, "WEEKSCAL")
        result.conf_call = self.parse_attribute_value_or_default(xml_element, "CONFCAL")
        result.retro = self.parse_attribute_value_or_default(xml_element, "RETRO")
        result.max_wait = self.parse_attribute_value_or_default(xml_element, "MAXWAIT")
        result.max_rerun = self.parse_attribute_value_or_default(xml_element, "MAXRERUN")
        result.auto_arch = self.parse_attribute_value_or_default(xml_element, "AUTOARCH")
        result.max_days = self.parse_attribute_value_or_default(xml_element, "MAXDAYS")
        result.max_runs = self.parse_attribute_value_or_default(xml_element, "MAXRUNS")
        result.time_from = self.parse_attribute_value_or_default(xml_element, "TIMEFROM")
        result.time_to = self.parse_attribute_value_or_default(xml_element, "TIMETO")
        result.days = self.parse_attribute_value_or_default(xml_element, "DAYS")
        result.weekdays = self.parse_attribute_value_or_default(xml_element, "WEEKDAYS")
        result.jan = self.parse_attribute_value_or_default(xml_element, "JAN")
        result.feb = self.parse_attribute_value_or_default(xml_element, "FEB")
        result.mar = self.parse_attribute_value_or_default(xml_element, "MAR")
        result.apr = self.parse_attribute_value_or_default(xml_element, "APR")
        result.jun = self.parse_attribute_value_or_default(xml_element, "JUN")
        result.jul = self.parse_attribute_value_or_default(xml_element, "JUL")
        result.aug = self.parse_attribute_value_or_default(xml_element, "AUG")
        result.sep = self.parse_attribute_value_or_default(xml_element, "SEP")
        result.oct = self.parse_attribute_value_or_default(xml_element, "OCT")
        result.nov = self.parse_attribute_value_or_default(xml_element, "NOV")
        result.dec = self.parse_attribute_value_or_default(xml_element, "DEC")
        result.date = self.parse_attribute_value_or_default(xml_element, "DATE")
        result.rerun_mem = self.parse_attribute_value_or_default(xml_element, "RERUNMEM")
        result.category = self.parse_attribute_value_or_default(xml_element, "DAYS_AND_OR")
        result.shift = self.parse_attribute_value_or_default(xml_element, "SHIFT")
        result.shift_num = self.parse_attribute_value_or_default(xml_element, "SHIFTNUM")
        result.pds_name = self.parse_attribute_value_or_default(xml_element, "PDSNAME")
        result.minimum = self.parse_attribute_value_or_default(xml_element, "MINIMUM")
        result.prevent_nct2 = self.parse_attribute_value_or_default(xml_element, "PREVENTNCT2")
        result.option = self.parse_attribute_value_or_default(xml_element, "OPTION")
        result.from_ = self.parse_attribute_value_or_default(xml_element, "FROM")
        result.par = self.parse_attribute_value_or_default(xml_element, "PAR")
        result.sys_db = self.parse_attribute_value_or_default(xml_element, "SYSDB")
        result.due_out = self.parse_attribute_value_or_default(xml_element, "DUE_OUT")
        result.retention_days = self.parse_attribute_value_or_default(xml_element, "RETEN_DAYS")
        result.retention_gen = self.parse_attribute_value_or_default(xml_element, "RETEN_GEN")
        result.task_class = self.parse_attribute_value_or_default(xml_element, "TASK_CLASS")
        result.prev_day = self.parse_attribute_value_or_default(xml_element, "PREV_DAY")
        result.adjust_condition = self.parse_attribute_value_or_default(xml_element, "ADJUST_COND")
        result.jobs_in_group = self.parse_attribute_value_or_default(xml_element, "JOBS_IN_GROUP")
        result.large_size = self.parse_attribute_value_or_default(xml_element, "LARGE_SIZE")
        result.ind_cyclic = self.parse_attribute_value_or_default(xml_element, "IND_CYCLIC")
        result.creation_user = self.parse_attribute_value_or_default(xml_element, "CREATION_USER")
        result.creation_date = self.parse_attribute_value_or_default(xml_element, "CREATION_DATE")
        result.creation_time = self.parse_attribute_value_or_default(xml_element, "CREATION_TIME")
        result.change_user = self.parse_attribute_value_or_default(xml_element, "CHANGE_USERID")
        result.change_date = self.parse_attribute_value_or_default(xml_element, "CHANGE_DATE")
        result.change_time = self.parse_attribute_value_or_default(xml_element, "CHANGE_TIME")
        result.job_version = self.parse_attribute_value_or_default(xml_element, "JOB_VERSION")
        result.rule_based_calendar_relationship =\
            self.parse_attribute_value_or_default(xml_element, "RULE_BASED_CALENDAR_RELATIONSHIP")
        result.tag_relationship = self.parse_attribute_value_or_default(xml_element, "TAG_RELATIONSHIP")
        result.timezone = self.parse_attribute_value_or_default(xml_element, "TIMEZONE")
        result.application_type = self.parse_attribute_value_or_default(xml_element, "APPL_TYPE")
        result.application_version = self.parse_attribute_value_or_default(xml_element, "APPL_VER")
        result.application_form = self.parse_attribute_value_or_default(xml_element, "APPL_FORM")
        result.cm_version = self.parse_attribute_value_or_default(xml_element, "CM_VER")
        result.multy_agent = self.parse_attribute_value_or_default(xml_element, "MULTY_AGENT")
        result.active_from = self.parse_attribute_value_or_default(xml_element, "ACTIVE_FROM")
        result.active_till = self.parse_attribute_value_or_default(xml_element, "ACTIVE_TILL")
        result.scheduling_environment = self.parse_attribute_value_or_default(xml_element, "SCHEDULING_ENVIRONMENT")
        result.system_affinity = self.parse_attribute_value_or_default(xml_element, "SYSTEM_AFFINITY")
        result.request_nje_node = self.parse_attribute_value_or_default(xml_element, "REQUEST_NJE_NODE")
        result.stat_cal = self.parse_attribute_value_or_default(xml_element, "STAT_CAL")
        result.instream_jcl = self.parse_attribute_value_or_default(xml_element, "INSTREAM_JCL")
        result.use_instream_jcl = self.parse_attribute_value_or_default(xml_element, "USE_INSTREAM_JCL")
        result.due_out_days_offset = self.parse_attribute_value_or_default(xml_element, "DUE_OUT_DAYSOFFSET")
        result.from_days_offset = self.parse_attribute_value_or_default(xml_element, "FROM_DAYSOFFSET")
        result.to_days_offset = self.parse_attribute_value_or_default(xml_element, "TO_DAYSOFFSET")
        result.version_op_code = self.parse_attribute_value_or_default(xml_element, "VERSION_OPCODE")
        result.is_current_version = self.parse_attribute_value_or_default(xml_element, "IS_CURRENT_VERSION")
        result.version_serial = self.parse_attribute_value_or_default(xml_element, "VERSION_SERIAL")
        result.version_host = self.parse_attribute_value_or_default(xml_element, "VERSION_HOST")
        result.cyclic_interval_sequence = self.parse_attribute_value_or_default(xml_element, "CYCLIC_INTERVAL_SEQUENCE")
        result.cyclic_times_sequence = self.parse_attribute_value_or_default(xml_element, "CYCLIC_TIMES_SEQUENCE")
        result.cyclic_tolerance = self.parse_attribute_value_or_default(xml_element, "CYCLIC_TOLERANCE")
        result.cyclic_type = self.parse_attribute_value_or_default(xml_element, "CYCLIC_TYPE")
        result.parent_folder = self.parse_attribute_value_or_default(xml_element, "PARENT_FOLDER")
        result.parent_table = self.parse_attribute_value_or_default(xml_element, "PARENT_TABLE")
        result.end_folder = self.parse_attribute_value_or_default(xml_element, "END_FOLDER")
        result.order_date = self.parse_attribute_value_or_default(xml_element, "ODATE")
        result.f_procs = self.parse_attribute_value_or_default(xml_element, "FPROCS")
        result.t_pg_ms = self.parse_attribute_value_or_default(xml_element, "TPGMS")
        result.t_procs = self.parse_attribute_value_or_default(xml_element, "TPROCS")
        for child in xml_element:
            if child.tag == 'VARIABLE':
                var_data = self.parse_var_data(child)
                self.logger.debug(f"Processed child variable {child.tag}: {var_data.__dict__}")
                result.variables.append(var_data)
            else:
                self.logger.debug(f"Unsupported JOB child element {child.tag}")
        return result

    def _validate_xsd_path(self) -> None:
        if not os.path.exists(self._xsd_path):
            self.logger.fatal(f"XSD schema at path '{self.xsd_path}' could not be found/")
            raise CtmXmlParserException(
                f"XSD schema at path '{self.xsd_path}' could not be found."
            )
        self.logger.debug(f"XSD schema at path '{self.xsd_path}' found.")


if __name__ == '__main__':
    parser = CtmXmlParser()
    tree = parser.parse_xml('./resources/PROD_CTM.all.xml')
    print(tree)
