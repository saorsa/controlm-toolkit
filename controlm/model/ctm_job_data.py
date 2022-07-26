from typing import Optional, List
from .ctm_def_table_item import CtmDefTableItem
from .ctm_var_data import CtmVarData


class CtmJobData (CtmDefTableItem):

    def __init__(self, tag_name: str):
        super().__init__(tag_name)
        self.job_isn: Optional[int] = -1
        self.application: Optional[str] = None
        self.sub_application: Optional[str] = None
        self.group: Optional[str] = None
        self.mem_name: Optional[str] = None
        self.job_name: Optional[str] = None
        self.description: Optional[str] = None
        self.created_by: Optional[str] = None
        self.author: Optional[str] = None
        self.run_as: Optional[str] = None
        self.owner: Optional[str] = None
        self.priority: Optional[str] = None
        self.critical: Optional[str] = None
        self.task_type: Optional[str] = None
        self.cyclic: Optional[str] = None
        self.node_id: Optional[str] = None
        self.doc_lib: Optional[str] = None
        self.doc_mem: Optional[str] = None
        self.interval: Optional[str] = None
        self.override_path: Optional[str] = None
        self.over_lib: Optional[str] = None
        self.mem_lib: Optional[str] = None
        self.cmd_line: Optional[str] = None
        self.confirm: Optional[str] = None
        self.days_cal: Optional[str] = None
        self.weeks_cal: Optional[str] = None
        self.conf_call: Optional[str] = None
        self.retro: Optional[str] = None
        self.max_wait: Optional[int] = None
        self.max_rerun: Optional[int] = None
        self.auto_arch: Optional[str] = None
        self.max_days: Optional[int] = None
        self.max_runs: Optional[int] = None
        self.time_from: Optional[str] = None
        self.time_to: Optional[str] = None
        self.days: Optional[str] = None
        self.weekdays: Optional[str] = None
        self.jan: Optional[str] = None
        self.feb: Optional[str] = None
        self.mar: Optional[str] = None
        self.apr: Optional[str] = None
        self.jun: Optional[str] = None
        self.jul: Optional[str] = None
        self.aug: Optional[str] = None
        self.sep: Optional[str] = None
        self.oct: Optional[str] = None
        self.nov: Optional[str] = None
        self.dec: Optional[str] = None
        self.date: Optional[str] = None
        self.rerun_mem: Optional[str] = None
        self.days_and_or: Optional[str] = None
        self.category: Optional[str] = None
        self.shift: Optional[str] = None
        self.shift_num: Optional[str] = None
        self.pds_name: Optional[str] = None
        self.minimum: Optional[str] = None
        self.prevent_nct2: Optional[str] = None
        self.option: Optional[str] = None
        self.from_: Optional[str] = None
        self.par: Optional[str] = None
        self.sys_db: Optional[str] = None
        self.due_out: Optional[str] = None
        self.retention_days: Optional[str] = None
        self.retention_gen: Optional[str] = None
        self.task_class: Optional[str] = None
        self.prev_day: Optional[str] = None
        self.adjust_condition: Optional[str] = None
        self.jobs_in_group: Optional[str] = None
        self.large_size: Optional[str] = None
        self.ind_cyclic: Optional[str] = None
        self.creation_user: Optional[str] = None
        self.creation_date: Optional[str] = None
        self.creation_time: Optional[str] = None
        self.change_user: Optional[str] = None
        self.change_date: Optional[str] = None
        self.change_time: Optional[str] = None
        self.job_version: Optional[str] = None
        self.rule_based_calendar_relationship: Optional[str] = None
        self.tag_relationship: Optional[str] = None
        self.timezone: Optional[str] = None
        self.application_type: Optional[str] = None
        self.application_version: Optional[str] = None
        self.application_form: Optional[str] = None
        self.cm_version: Optional[str] = None
        self.multy_agent: Optional[str] = None
        self.active_from: Optional[str] = None
        self.active_till: Optional[str] = None
        self.scheduling_environment: Optional[str] = None
        self.system_affinity: Optional[str] = None
        self.request_nje_node: Optional[str] = None
        self.stat_cal: Optional[str] = None
        self.instream_jcl: Optional[str] = None
        self.use_instream_jcl: Optional[str] = None
        self.due_out_days_offset: Optional[str] = None
        self.from_days_offset: Optional[str] = None
        self.to_days_offset: Optional[str] = None
        self.version_op_code: Optional[str] = None
        self.is_current_version: Optional[str] = None
        self.version_serial: Optional[str] = None
        self.version_host: Optional[str] = None
        self.cyclic_interval_sequence: Optional[str] = None
        self.cyclic_times_sequence: Optional[str] = None
        self.cyclic_times_sequence: Optional[str] = None
        self.cyclic_tolerance: Optional[str] = None
        self.cyclic_type: Optional[str] = None
        self.parent_folder: Optional[str] = None
        self.parent_table: Optional[str] = None
        self.end_folder: Optional[str] = None
        self.order_date: Optional[str] = None
        self.f_procs: Optional[str] = None
        self.t_pg_ms: Optional[str] = None
        self.t_procs: Optional[str] = None
        self.variables: List[CtmVarData] = []
