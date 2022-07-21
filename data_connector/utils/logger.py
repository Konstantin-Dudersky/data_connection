"""Setup logging.

in files:

from src.utils.logger import LoggerLevel, get_logger
logger = get_logger(__name__, LoggerLevel.INFO)
"""

import logging
import os
import socket
from enum import IntEnum
from logging import Handler, handlers

from .settings import settings

# from .telegram import TelegramHandler, bot

FORMAT = (
    "%(levelname)s: %(asctime)s | "
    "%(name)s:%(lineno)d - %(funcName)s | "
    "\n-> %(message)s"
)


# ------------------------------------------------------------------------------


class LoggerLevel(IntEnum):
    """Logging levels."""

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


# Formatters ------------------------------------------------------------------


class StreamFormatter(logging.Formatter):
    """Custom formatter for console output."""

    GREEN = "\x1b[32;20m"
    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    def get_format(self: "StreamFormatter", text: str, levelno: int) -> str:
        """Цвет сообщения.

        :param text: текст, цвет которого нужно изменить
        :param levelno: класс сообщения
        :return: текст с измененным текстом
        """
        match levelno:
            case logging.DEBUG:
                return self.GREY + text + self.RESET
            case logging.INFO:
                return self.GREEN + text + self.RESET
            case logging.WARNING:
                return self.YELLOW + text + self.RESET
            case logging.ERROR:
                return self.RED + text + self.RESET
            case logging.CRITICAL:
                return self.BOLD_RED + text + self.RESET
        return text

    def format(self: "StreamFormatter", record: logging.LogRecord) -> str:
        """Format function.

        :param record: запись логгера
        :return: отформатированная запись логгера
        """
        log_fmt = self.get_format(FORMAT, record.levelno)
        formatter = logging.Formatter(log_fmt)
        return (
            formatter.format(record)
            + "\n"
            + self.get_format("-" * 80, record.levelno)
        )


class FileFormatter(logging.Formatter):
    """Custom formatter for file output."""

    def format(self: "FileFormatter", record: logging.LogRecord) -> str:
        """Format function.

        :param record: запись логгера
        :return: отформатированная запись логгера
        """
        formatter = logging.Formatter(FORMAT)
        return formatter.format(record) + "\n" + "-" * 80


# Loggers ---------------------------------------------------------------------

os.makedirs("logs", exist_ok=True)

_handlers: list[Handler] = []
# логгирование в файл
file_handler = handlers.RotatingFileHandler(
    filename="logs/log.log",
    mode="a",
    maxBytes=5 * 1024 * 1024,
    backupCount=2,
    encoding=None,
    delay=False,
)
file_handler.setFormatter(FileFormatter())
_handlers.append(file_handler)
# логгирование в консоль
if settings.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(StreamFormatter())
    _handlers.append(stream_handler)
# логгирование в telegram
# telegram_handler = TelegramHandler(bot)
# _handlers.append(telegram_handler)

logging.basicConfig(
    format=FORMAT,
    level=logging.INFO,
    handlers=_handlers,
)

# ------------------------------------------------------------------------------


def get_logger(
    name: str,
    level: LoggerLevel = LoggerLevel.INFO,
) -> logging.Logger:
    """Return logger with name.

    :param name: название логгера
    :param level: уровень логгирования
    :return: объект логгера
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


# ------------------------------------------------------------------------------


_logger = get_logger(__name__)
_logger.info("Start at host: %s", socket.gethostname())
