import logging
from .console_color_formatter import ConsoleColorFormatter


def create_console_logger(
        logger_name: str = __name__,
        min_log_level: int = logging.DEBUG,
        console_log_level: int = logging.DEBUG) -> logging.Logger:

    logger = logging.getLogger(logger_name)
    logger.setLevel(min_log_level)

    ch = logging.StreamHandler()
    ch.setLevel(console_log_level)
    ch.setFormatter(ConsoleColorFormatter())
    logger.addHandler(ch)

    return logger
