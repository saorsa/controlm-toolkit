from abc import ABC
from typing import Optional


class DtoHostInfo(ABC):
    def __init__(self, **kwargs):
        self.server: Optional[str] = kwargs['server'] if 'server' in kwargs else None
        self.group: Optional[str] = kwargs['group'] if 'group' in kwargs else None
        self.host: Optional[str] = kwargs['host'] if 'host' in kwargs else None
