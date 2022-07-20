from abc import ABC


class CtmBaseObject (ABC):

    def __init__(self, tag_name: str):
        self._tag_name: str = tag_name

    @property
    def tag_name(self) -> str:
        return self._tag_name
