import os.path
from logging import Logger
from typing import Final, Optional
from lxml import etree
from common.logging import create_console_logger
from controlm.model.ctm_def_table import CtmDefTable
from controlm.model.ctm_def_table_item import CtmDefTableItem
from controlm.model.ctm_simple_folder import CtmSimpleFolder
from controlm.model.ctm_smart_folder import CtmSmartFolder
from controlm.model.ctm_var_data import CtmVarData
from controlm.model.ctm_tag_data import CtmTagData
from controlm.model.ctm_job_data import CtmJobData


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


class CtmXmlParserException (BaseException):

    def __init__(self, message: str, error_code: int = -1):
        self.message = message
        self.error_code = error_code


# noinspection DuplicatedCode
class CtmXmlParser:

    def __init__(self,
                 xsd_path: str = './resources/Folder.xsd',
                 logger: Logger = None):
        self._xsd_path: str = xsd_path
        self._logger: Logger = logger or create_console_logger(__name__)
        self._validate_xsd_path()

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def xsd_path(self) -> str:
        return self._xsd_path

    def validate_xml(self, xml_path: str) -> bool:
        """
        Validates the target XML file
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
        result = self.parse_def_table(root)
        self.logger.debug(f"Parsed definition table. {len(result.items)} items found...")
        return result

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
        tag: CtmTagData = CtmTagData(tag_name or xml_element.tag)
        tag.name = self.parse_attribute_value_or_default(xml_element, "NAME")
        tag.max_wait = self.parse_attribute_value_or_default(xml_element, "MAXWAIT")
        tag.days_and_or = self.parse_attribute_value_or_default(xml_element, "DAYS_AND_OR")
        tag.jan = self.parse_attribute_value_or_default(xml_element, "JAN")
        tag.feb = self.parse_attribute_value_or_default(xml_element, "FEB")
        tag.mar = self.parse_attribute_value_or_default(xml_element, "MAR")
        tag.apr = self.parse_attribute_value_or_default(xml_element, "APR")
        tag.may = self.parse_attribute_value_or_default(xml_element, "MAY")
        tag.jun = self.parse_attribute_value_or_default(xml_element, "JUN")
        tag.jul = self.parse_attribute_value_or_default(xml_element, "JUL")
        tag.aug = self.parse_attribute_value_or_default(xml_element, "AUG")
        tag.sep = self.parse_attribute_value_or_default(xml_element, "SEP")
        tag.oct = self.parse_attribute_value_or_default(xml_element, "OCT")
        tag.nov = self.parse_attribute_value_or_default(xml_element, "NOV")
        tag.dec = self.parse_attribute_value_or_default(xml_element, "DEC")
        tag.days_cal = self.parse_attribute_value_or_default(xml_element, "DAYSCAL")
        tag.weeks_cal = self.parse_attribute_value_or_default(xml_element, "WEEKSCAL")
        tag.conf_cal = self.parse_attribute_value_or_default(xml_element, "CONFCAL")
        tag.shift = self.parse_attribute_value_or_default(xml_element, "SHIFT")
        tag.shift_num = self.parse_attribute_value_or_default(xml_element, "SHIFTNUM")
        tag.retro = self.parse_attribute_value_or_default(xml_element, "RETRO")
        tag.date = self.parse_attribute_value_or_default(xml_element, "DATE")
        tag.days = self.parse_attribute_value_or_default(xml_element, "DAYS")
        tag.weekdays = self.parse_attribute_value_or_default(xml_element, "WEEKDAYS")
        tag.weekdays = self.parse_attribute_value_or_default(xml_element, "WEEKDAYS")
        tag.active_from = self.parse_attribute_value_or_default(xml_element, "ACTIVE_FROM")
        tag.tags_active_from = self.parse_attribute_value_or_default(xml_element, "TAGS_ACTIVE_FROM")
        tag.active_till = self.parse_attribute_value_or_default(xml_element, "ACTIVE_TILL")
        tag.tags_active_till = self.parse_attribute_value_or_default(xml_element, "TAGS_ACTIVE_TILL")
        tag.level = self.parse_attribute_value_or_default(xml_element, "LEVEL")
        return tag

    def parse_job_data(self, xml_element: etree.ElementTree) -> CtmJobData:
        if xml_element.tag != 'JOB':
            raise CtmXmlParserException(
                f"The XML element {xml_element.tag} is not a Control-M variable."
            )
        job: CtmJobData = CtmJobData(xml_element.tag)
        job.job_isn = self.parse_attribute_value_or_default(xml_element, "JOBISN")
        job.application = self.parse_attribute_value_or_default(xml_element, "APPLICATION")
        job.sub_application = self.parse_attribute_value_or_default(xml_element, "SUB_APPLICATION")
        job.group = self.parse_attribute_value_or_default(xml_element, "GROUP")
        job.mem_name = self.parse_attribute_value_or_default(xml_element, "MEMNAME")
        job.job_name = self.parse_attribute_value_or_default(xml_element, "JOBNAME")
        job.description = self.parse_attribute_value_or_default(xml_element, "DESCRIPTION")
        job.created_by = self.parse_attribute_value_or_default(xml_element, "CREATED_BY")
        job.author = self.parse_attribute_value_or_default(xml_element, "AUTHOR")
        job.run_as = self.parse_attribute_value_or_default(xml_element, "RUN_AS")
        job.owner = self.parse_attribute_value_or_default(xml_element, "OWNER")
        job.priority = self.parse_attribute_value_or_default(xml_element, "PRIORITY")
        job.critical = self.parse_attribute_value_or_default(xml_element, "CRITICAL")
        job.task_type = self.parse_attribute_value_or_default(xml_element, "TASKTYPE")
        job.cyclic = self.parse_attribute_value_or_default(xml_element, "CYCLIC")
        job.node_id = self.parse_attribute_value_or_default(xml_element, "NODEID")
        job.doc_lib = self.parse_attribute_value_or_default(xml_element, "DOCLIB")
        job.doc_mem = self.parse_attribute_value_or_default(xml_element, "DOCMEM")
        job.interval = self.parse_attribute_value_or_default(xml_element, "INTERVAL")
        job.override_path = self.parse_attribute_value_or_default(xml_element, "OVERRIDE_PATH")
        job.over_lib = self.parse_attribute_value_or_default(xml_element, "OVERLIB")
        job.mem_lib = self.parse_attribute_value_or_default(xml_element, "MEMLIB")
        job.cmd_line = self.parse_attribute_value_or_default(xml_element, "CMDLINE")
        job.confirm = self.parse_attribute_value_or_default(xml_element, "CONFIRM")
        job.days_cal = self.parse_attribute_value_or_default(xml_element, "DAYSCAL")
        job.weeks_cal = self.parse_attribute_value_or_default(xml_element, "WEEKSCAL")
        job.conf_call = self.parse_attribute_value_or_default(xml_element, "CONFCAL")
        job.retro = self.parse_attribute_value_or_default(xml_element, "RETRO")
        job.max_wait = self.parse_attribute_value_or_default(xml_element, "MAXWAIT")
        job.max_rerun = self.parse_attribute_value_or_default(xml_element, "MAXRERUN")
        job.auto_arch = self.parse_attribute_value_or_default(xml_element, "AUTOARCH")
        job.max_days = self.parse_attribute_value_or_default(xml_element, "MAXDAYS")
        job.max_runs = self.parse_attribute_value_or_default(xml_element, "MAXRUNS")
        job.time_from = self.parse_attribute_value_or_default(xml_element, "TIMEFROM")
        job.time_to = self.parse_attribute_value_or_default(xml_element, "TIMETO")
        job.days = self.parse_attribute_value_or_default(xml_element, "DAYS")
        job.weekdays = self.parse_attribute_value_or_default(xml_element, "WEEKDAYS")
        job.jan = self.parse_attribute_value_or_default(xml_element, "JAN")
        job.feb = self.parse_attribute_value_or_default(xml_element, "FEB")
        job.mar = self.parse_attribute_value_or_default(xml_element, "MAR")
        job.apr = self.parse_attribute_value_or_default(xml_element, "APR")
        job.jun = self.parse_attribute_value_or_default(xml_element, "JUN")
        job.jul = self.parse_attribute_value_or_default(xml_element, "JUL")
        job.aug = self.parse_attribute_value_or_default(xml_element, "AUG")
        job.sep = self.parse_attribute_value_or_default(xml_element, "SEP")
        job.oct = self.parse_attribute_value_or_default(xml_element, "OCT")
        job.nov = self.parse_attribute_value_or_default(xml_element, "NOV")
        job.dec = self.parse_attribute_value_or_default(xml_element, "DEC")
        job.date = self.parse_attribute_value_or_default(xml_element, "DATE")
        job.rerun_mem = self.parse_attribute_value_or_default(xml_element, "RERUNMEM")
        job.category = self.parse_attribute_value_or_default(xml_element, "DAYS_AND_OR")
        job.shift = self.parse_attribute_value_or_default(xml_element, "SHIFT")
        job.shift_num = self.parse_attribute_value_or_default(xml_element, "SHIFTNUM")
        job.pds_name = self.parse_attribute_value_or_default(xml_element, "PDSNAME")
        job.minimum = self.parse_attribute_value_or_default(xml_element, "MINIMUM")
        job.prevent_nct2 = self.parse_attribute_value_or_default(xml_element, "PREVENTNCT2")
        job.option = self.parse_attribute_value_or_default(xml_element, "OPTION")
        job.from_ = self.parse_attribute_value_or_default(xml_element, "FROM")
        job.par = self.parse_attribute_value_or_default(xml_element, "PAR")
        job.sys_db = self.parse_attribute_value_or_default(xml_element, "SYSDB")
        job.due_out = self.parse_attribute_value_or_default(xml_element, "DUE_OUT")
        job.retention_days = self.parse_attribute_value_or_default(xml_element, "RETEN_DAYS")
        job.retention_gen = self.parse_attribute_value_or_default(xml_element, "RETEN_GEN")
        job.task_class = self.parse_attribute_value_or_default(xml_element, "TASK_CLASS")
        job.prev_day = self.parse_attribute_value_or_default(xml_element, "PREV_DAY")
        job.adjust_condition = self.parse_attribute_value_or_default(xml_element, "ADJUST_COND")
        job.jobs_in_group = self.parse_attribute_value_or_default(xml_element, "JOBS_IN_GROUP")
        job.large_size = self.parse_attribute_value_or_default(xml_element, "LARGE_SIZE")
        job.ind_cyclic = self.parse_attribute_value_or_default(xml_element, "IND_CYCLIC")
        job.creation_user = self.parse_attribute_value_or_default(xml_element, "CREATION_USER")
        job.creation_date = self.parse_attribute_value_or_default(xml_element, "CREATION_DATE")
        job.creation_time = self.parse_attribute_value_or_default(xml_element, "CREATION_TIME")
        job.change_user = self.parse_attribute_value_or_default(xml_element, "CHANGE_USERID")
        job.change_date = self.parse_attribute_value_or_default(xml_element, "CHANGE_DATE")
        job.change_time = self.parse_attribute_value_or_default(xml_element, "CHANGE_TIME")
        job.job_version = self.parse_attribute_value_or_default(xml_element, "JOB_VERSION")
        job.rule_based_calendar_relationship =\
            self.parse_attribute_value_or_default(xml_element, "RULE_BASED_CALENDAR_RELATIONSHIP")
        job.tag_relationship = self.parse_attribute_value_or_default(xml_element, "TAG_RELATIONSHIP")
        job.timezone = self.parse_attribute_value_or_default(xml_element, "TIMEZONE")
        job.application_type = self.parse_attribute_value_or_default(xml_element, "APPL_TYPE")
        job.application_version = self.parse_attribute_value_or_default(xml_element, "APPL_VER")
        job.application_form = self.parse_attribute_value_or_default(xml_element, "APPL_FORM")
        job.cm_version = self.parse_attribute_value_or_default(xml_element, "CM_VER")
        job.multy_agent = self.parse_attribute_value_or_default(xml_element, "MULTY_AGENT")
        job.active_from = self.parse_attribute_value_or_default(xml_element, "ACTIVE_FROM")
        job.active_till = self.parse_attribute_value_or_default(xml_element, "ACTIVE_TILL")
        job.scheduling_environment = self.parse_attribute_value_or_default(xml_element, "SCHEDULING_ENVIRONMENT")
        job.system_affinity = self.parse_attribute_value_or_default(xml_element, "SYSTEM_AFFINITY")
        job.request_nje_node = self.parse_attribute_value_or_default(xml_element, "REQUEST_NJE_NODE")
        job.stat_cal = self.parse_attribute_value_or_default(xml_element, "STAT_CAL")
        job.instream_jcl = self.parse_attribute_value_or_default(xml_element, "INSTREAM_JCL")
        job.use_instream_jcl = self.parse_attribute_value_or_default(xml_element, "USE_INSTREAM_JCL")
        job.due_out_days_offset = self.parse_attribute_value_or_default(xml_element, "DUE_OUT_DAYSOFFSET")
        job.from_days_offset = self.parse_attribute_value_or_default(xml_element, "FROM_DAYSOFFSET")
        job.to_days_offset = self.parse_attribute_value_or_default(xml_element, "TO_DAYSOFFSET")
        job.version_op_code = self.parse_attribute_value_or_default(xml_element, "VERSION_OPCODE")
        job.is_current_version = self.parse_attribute_value_or_default(xml_element, "IS_CURRENT_VERSION")
        job.version_serial = self.parse_attribute_value_or_default(xml_element, "VERSION_SERIAL")
        job.version_host = self.parse_attribute_value_or_default(xml_element, "VERSION_HOST")
        job.cyclic_interval_sequence = self.parse_attribute_value_or_default(xml_element, "CYCLIC_INTERVAL_SEQUENCE")
        job.cyclic_times_sequence = self.parse_attribute_value_or_default(xml_element, "CYCLIC_TIMES_SEQUENCE")
        job.cyclic_tolerance = self.parse_attribute_value_or_default(xml_element, "CYCLIC_TOLERANCE")
        job.cyclic_type = self.parse_attribute_value_or_default(xml_element, "CYCLIC_TYPE")
        job.parent_folder = self.parse_attribute_value_or_default(xml_element, "PARENT_FOLDER")
        job.parent_table = self.parse_attribute_value_or_default(xml_element, "PARENT_TABLE")
        job.end_folder = self.parse_attribute_value_or_default(xml_element, "END_FOLDER")
        job.order_date = self.parse_attribute_value_or_default(xml_element, "ODATE")
        job.f_procs = self.parse_attribute_value_or_default(xml_element, "FPROCS")
        job.t_pg_ms = self.parse_attribute_value_or_default(xml_element, "TPGMS")
        job.t_procs = self.parse_attribute_value_or_default(xml_element, "TPROCS")
        for child in xml_element:
            if child.tag == 'VARIABLE':
                var_data = self.parse_var_data(child)
                self.logger.debug(f"Processed child variable {child.tag}: {var_data.__dict__}")
                job.variables.append(var_data)
            else:
                self.logger.debug(f"Unsupported JOB child element {child.tag}")
        return job

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
