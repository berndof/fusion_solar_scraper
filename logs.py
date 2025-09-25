__all__ = ["collector_logger"]

from typing import TextIO
import logging
from logging import Formatter, Logger, StreamHandler
from logging.handlers import RotatingFileHandler
import os

os.makedirs(name="log", exist_ok=True)
LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper())

LOG_FILE = "log/collector.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 5

collector_logger: Logger = logging.getLogger(name="collector")
collector_logger.setLevel(level=LOG_LEVEL)
collector_logger.propagate = False  # evita duplicação de logs no console

file_handler: RotatingFileHandler = RotatingFileHandler(
    filename=LOG_FILE,
    maxBytes=MAX_LOG_SIZE,
    backupCount=BACKUP_COUNT,
    encoding="utf-8",
)
formatter: Formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(fmt=formatter)
collector_logger.addHandler(hdlr=file_handler)

if LOG_LEVEL == logging.DEBUG:
    console_handler: StreamHandler[TextIO] = logging.StreamHandler()
    console_handler.setFormatter(fmt=formatter)
    collector_logger.addHandler(hdlr=console_handler)
