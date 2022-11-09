"""Настройка логгирования.

В точке входа в программу:

from src.shared.logger import logger_init
logger_init()

В файлах:

import logging
log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.INFO)
"""

import logging
import os
import socket
from logging.handlers import RotatingFileHandler

CHAR_IN_LINE: int = 80
FORMAT: str = (
    "%(levelname)s: %(asctime)s | "
    + "%(name)s:%(lineno)d - %(funcName)s | "
    + "\n-> %(message)s"
)


# Formatters ------------------------------------------------------------------


class StreamFormatter(logging.Formatter):
    """Custom formatter for console output."""

    color_green: str = "\x1b[32;20m"
    color_grey: str = "\x1b[38;20m"
    color_yellow: str = "\x1b[33;20m"
    color_red: str = "\x1b[31;20m"
    color_bold_red: str = "\x1b[31;1m"
    reset: str = "\x1b[0m"

    def get_format(self: "StreamFormatter", text: str, levelno: int) -> str:
        """Цвет сообщения.

        :param text: текст, цвет которого нужно изменить
        :param levelno: класс сообщения
        :return: текст с измененным текстом
        """
        out_text: str = ""
        match levelno:
            case logging.DEBUG:
                out_text = self.color_grey + text + self.reset
            case logging.INFO:
                out_text = self.color_green + text + self.reset
            case logging.WARNING:
                out_text = self.color_yellow + text + self.reset
            case logging.ERROR:
                out_text = self.color_red + text + self.reset
            case logging.CRITICAL:
                out_text = self.color_bold_red + text + self.reset
            case _:
                out_text = text
        return out_text

    def format(self: "StreamFormatter", record: logging.LogRecord) -> str:
        """Format function.

        :param record: запись логгера
        :return: отформатированная запись логгера
        """
        log_fmt = self.get_format(FORMAT, record.levelno)
        formatter = logging.Formatter(log_fmt)
        formatted_str: str = (
            formatter.format(record)
            + "\n"
            + self.get_format("-" * CHAR_IN_LINE, record.levelno)
        )
        # логгинг не идет в debug console
        # print(formatter.format(record))  # noqa: WPS421
        return formatted_str


class FileFormatter(logging.Formatter):
    """Custom formatter for file output."""

    def format(self: "FileFormatter", record: logging.LogRecord) -> str:
        """Format function.

        :param record: запись логгера
        :return: отформатированная запись логгера
        """
        formatter = logging.Formatter(FORMAT)
        return "{0}\n{1}".format(formatter.format(record), "-" * CHAR_IN_LINE)


# Loggers ---------------------------------------------------------------------


def logger_init(service: str = "log") -> None:
    """Инициализация логгера.

    :param service: подпапка для хранения логов
    """
    os.makedirs("logs", exist_ok=True)
    handlers: list[logging.Handler] = []
    # логгирование в файл
    file_handler: logging.Handler = RotatingFileHandler(
        filename="logs/{0}.log".format(service),
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding=None,
        delay=False,
    )
    file_handler.setFormatter(FileFormatter())
    handlers.append(file_handler)
    # логгирование в консоль
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(StreamFormatter())
    handlers.append(stream_handler)
    logging.basicConfig(
        format=FORMAT,
        level=logging.INFO,
        handlers=handlers,
    )
    logger = logging.getLogger(__name__)
    logger.info("Start at host: %s", socket.gethostname())
