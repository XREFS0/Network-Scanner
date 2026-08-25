import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Callable
from app.core.config import LOG_FILE_PATH


class LogEmitter:
    _callbacks = []

    @classmethod
    def register_callback(cls, callback: Callable[[str, str, str], None]):
        if callback not in cls._callbacks:
            cls._callbacks.append(callback)

    @classmethod
    def emit(cls, level: str, timestamp: str, message: str):
        for cb in cls._callbacks:
            try:
                cb(level, timestamp, message)
            except Exception:
                pass


class UICallbackHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            timestamp = self.formatter.formatTime(record, "%H:%M:%S") if self.formatter else ""
            LogEmitter.emit(record.levelname, timestamp, record.getMessage())
        except Exception:
            self.handleError(record)


def setup_logger(name: str = "NetSentinel") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    ui_handler = UICallbackHandler()
    ui_handler.setLevel(logging.DEBUG)
    ui_handler.setFormatter(formatter)
    logger.addHandler(ui_handler)

    return logger


logger = setup_logger()
