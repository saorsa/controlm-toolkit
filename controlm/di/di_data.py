from dependency_injector import containers, providers
from controlm.services.ctm_repository import CtmRepository
from controlm.services.ctm_cache_manager import CtmCacheManager
from .di_core import DICore


class DIData(containers.DeclarativeContainer):

    config = providers.Configuration()
    core_container = providers.Container(
        DICore,
        config=config.core
    )
    logger = core_container.logger
    shared_cache = core_container.shared_cache
    shared_task_runner = core_container.shared_task_runner
    shared_cache_manager = providers.Singleton(
        CtmCacheManager,
        identifier=providers.Object("shared_cache_manager"),
        cache=shared_cache,
        task_runner=shared_task_runner,
    )
    ctm_repository = providers.Factory(
        CtmRepository,
        cache_manager=shared_cache_manager,
    )
