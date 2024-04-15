import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Iterable


def configure_loggers(
        log_level: str = logging.WARNING,
        log_format: str = '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
        date_format: str = '%Y-%m-%d %H:%M:%S',
        filename: str | None = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 0,
        site_logger_names: Iterable[str] | None = None
) -> None:
    # Define a formatter based on the provided log_format
    formatter = logging.Formatter(log_format, date_format)

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    handlers = [console_handler]

    # Initialize file handler if filename is provided
    if filename:
        file_handler = RotatingFileHandler(
            filename, maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)

        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format=log_format,
        datefmt=date_format
    )
    if site_logger_names is not None:
        for logger_name in site_logger_names:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
            # logger.handlers = handlers
