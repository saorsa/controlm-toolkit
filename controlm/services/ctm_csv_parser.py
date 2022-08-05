from logging import Logger
from typing import List

from controlm.services.dto import DtoHostInfo
from corelib.logging import create_console_logger


class CtmCsvParser:

    def __init__(self,
                 logger: Logger = None):
        self._logger: Logger = logger or create_console_logger(__name__)

    def parse_node_ids(self,
                       csv_path: str = './resources/PROD_CTM.Nodes.csv',
                       delimiter: str = '|',
                       skip_lines_count: int = 2) -> List[DtoHostInfo]:
        try:
            with open(csv_path) as tmp:
                lines = tmp.readlines()
                index = 0
                results: List[DtoHostInfo] = []
                for line in lines:
                    if index >= skip_lines_count:
                        cols = line.split(sep=delimiter)
                        if len(cols) > 3:
                            results.append(DtoHostInfo(
                                server=cols[0].strip(), group=cols[1].strip(), host=cols[2].strip()))
                            self._logger.debug(f"{cols[0].strip()}, {cols[1].strip()}, {cols[2].strip()}")
                    index += 1
                return results
        except BaseException as ex:
            self._logger.fatal(ex)
            raise ex
