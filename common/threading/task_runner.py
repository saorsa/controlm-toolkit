import threading
from abc import ABC
from logging import Logger
from threading import Lock
from uuid import uuid4
from typing import Optional, Dict
from common.logging import create_console_logger
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future


class TaskMetaData (ABC):

    def __init__(self,
                 key: str = None,
                 thread_id: int = None,
                 description: str = None,
                 started_at: datetime = None,
                 finished_at: datetime = None):
        self._key = key or f"{__name__}_{uuid4()}"
        self._thread_id: int = thread_id or -1
        self._description: Optional[str] = description
        self._started = started_at or datetime.now()
        self._finished: Optional[datetime] = finished_at

    @property
    def key(self) -> str:
        return self._key

    @property
    def thread_id(self) -> int:
        return self._thread_id

    def invalidate_thread(self):
        self._thread_id = threading.current_thread().native_id

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def started_at(self) -> datetime:
        return self._started

    @property
    def finished_at(self) -> Optional[datetime]:
        return self._finished

    def set_finished(self, finished_at: datetime) -> None:
        self._finished = finished_at

    @property
    def is_running(self) -> bool:
        return self._finished is None

    @property
    def is_finished(self) -> bool:
        return self._finished is not None


class TaskRunner (ABC):

    def __init__(self,
                 identifier: str = f"{__name__}_{uuid4()}",
                 logger: Logger = None):
        self._identifier = identifier
        self._thread_lock = Lock()
        self._thread_pool = ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix=identifier
        )
        self._logger = logger or create_console_logger(__name__)
        self._meta: Dict[int, TaskMetaData] = {}
        self._futures: [Future] = []
        self._logger.info(f"Task runner '{self.identifier}' initialized.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True)

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def tasks(self) -> [Future]:
        return self._futures

    def shutdown(self, wait: bool = True):
        self.logger.info("Task runner shutting down...")
        self._thread_pool.shutdown(wait=wait)
        self.logger.info("Task runner shut down.")

    def schedule_task(self, callable_fn, *args, **kwargs) -> Future:
        with self._thread_lock:
            task_meta: TaskMetaData = kwargs.get('task_meta') or TaskMetaData()
            kwargs['task_meta'] = task_meta
            future = self._thread_pool.submit(callable_fn, *args, **kwargs)
            future.add_done_callback(self._scheduled_task_completion_callback)
            future_id = id(future)
            self._futures.append(future)
            self._meta[future_id] = task_meta
            self.logger.debug(f"Scheduled background task [{future_id}]. "
                              f"Meta = {self._meta[future_id].__dict__}.")
            return future

    def _scheduled_task_completion_callback(self, future: Future):
        future_id = id(future)
        self.logger.debug(f"Background task notification callback [{future}]")
        if future.done():
            self.logger.info(f"Background task complete [{future}]")
            with self._thread_lock:
                self.logger.debug(f"Cleaning up background task [{future_id}]. "
                                  f"Meta = {self._meta[future_id].__dict__}.")
                self._futures.remove(future)
                del self._meta[future_id]
