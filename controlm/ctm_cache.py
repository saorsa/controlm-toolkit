from threading import Thread
from typing import Optional
from common.logging import create_console_logger
from .ctm_xml_parser import CtmXmlParser
from .ctm_rest_cache import shared_rest_cache
from datetime import datetime


class _CacheOpts:

    def __init__(self):
        self.active_thread: Optional[Thread] = None


_shared_cache_opts = _CacheOpts()


def _invalidate_cache() -> (datetime, datetime):
    date_start = datetime.now()
    parser = CtmXmlParser(
        logger=create_console_logger()
    )
    try:
        shared_rest_cache.set_cache_state_error(None)
        shared_rest_cache.set_cache_state_progress()
        def_table = parser.parse_xml('./resources/PROD_CTM.all.xml')
        data_center_keys = []
        data_center_aggregates = {}
        for item in def_table.items:
            if hasattr(item, 'data_center'):
                if item.data_center not in data_center_keys:
                    data_center_keys.append(item.data_center)
                if item.data_center not in data_center_aggregates:
                    data_center_aggregates[item.data_center] = {
                        'applications': {}
                    }
                data_center_apps = data_center_aggregates[item.data_center]['applications']
                if hasattr(item, 'application') and item.application:
                    if item.application not in data_center_apps:
                        data_center_apps[item.application] = []
                    active_app_subs = data_center_apps[item.application]
                    if hasattr(item, 'sub_application') and item.sub_application not in active_app_subs:
                        active_app_subs.append(item.sub_application)
        shared_rest_cache.set_cache_state_complete(def_table, data_center_keys, data_center_aggregates)
    except BaseException as ex:
        parser.logger.fatal(ex)
        shared_rest_cache.set_cache_state_error(ex)
    finally:
        _shared_cache_opts.active_thread = None
        date_end = datetime.now()
        parser.logger.warning(f"Parsing started at [{date_start}], finished at [{date_end}]. "
                              f"Duration = {(date_end - date_start).total_seconds()} seconds")
        return date_start, date_end


def schedule_invalidate_cache() -> Thread:
    if _shared_cache_opts.active_thread:
        return _shared_cache_opts.active_thread

    cache_thread = Thread(target=_invalidate_cache)
    _shared_cache_opts.activeThread = cache_thread
    cache_thread.start()
    return cache_thread
