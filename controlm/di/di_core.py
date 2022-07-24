from dependency_injector import containers, providers
from common.logging import create_console_logger
from common.caching import CacheStore
from common.threading import TaskRunner


class DICore(containers.DeclarativeContainer):

    config = providers.Configuration()
    logger = providers.Object(create_console_logger('default'))
    shared_cache = providers.Singleton(
        CacheStore,
        identifier=providers.Object('shared_cache'),
        logger=providers.Object(None)
    )
    shared_task_runner = providers.Singleton(
        TaskRunner,
        providers.Object('shared_task_runner'))
    task_runner = providers.Factory(TaskRunner)
