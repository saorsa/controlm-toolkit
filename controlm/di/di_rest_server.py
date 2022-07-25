from dependency_injector import containers, providers
from .di_data import DIData


class DIRestServer(containers.DeclarativeContainer):
    config = providers.Configuration()
    data_container = providers.Container(
        DIData,
        config=config.data
    )
    logger = data_container.logger
    shared_cache = data_container.shared_cache
    shared_task_runner = data_container.shared_task_runner
    shared_cache_manager = data_container.shared_cache_manager
    ctm_repository = data_container.ctm_repository
