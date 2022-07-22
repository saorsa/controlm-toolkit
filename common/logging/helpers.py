import logging
from .console_color_formatter import ConsoleColorFormatter


opts = {
    'added': False
}


def create_console_logger(
        logger_name: str = __name__,
        min_log_level: int = None,
        console_log_level: int = None) -> logging.Logger:

    logger = logging.getLogger(logger_name)
    min_log_level = min_log_level or logging.INFO
    logger.setLevel(min_log_level)

    ch = logging.StreamHandler()
    console_log_level = console_log_level or logging.WARNING
    ch.setLevel(console_log_level)
    ch.setFormatter(ConsoleColorFormatter())

    if not opts['added']:
        logger.addHandler(ch)
        opts['added'] = True

    return logger
