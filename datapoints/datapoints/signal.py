"""Signals."""

from enum import Enum, auto
from time import perf_counter_ns
from typing import Generic, TypeVar

from typing_extensions import Self

from .utils.logger import LoggerLevel, get_logger


log = get_logger(__name__, LoggerLevel.INFO)


class AccessEnum(Enum):
    """Тип доступа."""

    READONLY = auto()
    WRITEONLY = auto()
    READWRITE = auto()


Signaltype = TypeVar("Signaltype", bool, int, str, None)


class Signal(Generic[Signaltype]):
    """Базовый класс для сигналов."""

    __id: int
    __read_ts: int
    __value: Signaltype
    __write_ts: int

    def __init__(
        self: Self,
        default: Signaltype,
        debug: bool = False,
    ) -> None:
        """Базовый класс для сигналов.

        :param default: начальное значение
        :param debug: True - выводить в лог данные о чтении / записи
        """
        self.__id = id(self)
        self.__read_ts = 0
        self.__write_ts = 0
        self.__value = default
        if debug:
            log.setLevel(LoggerLevel.DEBUG)

    @property
    def read_ts(self: Self) -> int:
        """Метка времени чтения.

        :return: Метка времени чтения
        """
        return self.__read_ts

    @property
    def write_ts(self: Self) -> int:
        """Метка времени записи.

        :return: Метка времени записи
        """
        return self.__write_ts

    @property
    def value(self: Self) -> Signaltype:
        """Возвращает значение.

        :return: значение
        """
        self.__read_ts = perf_counter_ns()
        log.debug(
            "%s, read, value: %s, read_ts: %s",
            repr(self),
            self.__value,
            self.__read_ts,
        )
        return self.__value

    @value.setter
    def value(self: Self, value: Signaltype) -> None:
        """Устанавливает значение.

        :param value: новое значение
        """
        self.__value: Signaltype = value
        self.__write_ts = perf_counter_ns()
        log.debug(
            "%s, write, value: %s, write_ts: %s",
            repr(self),
            self.__value,
            self.__write_ts,
        )

    def __repr__(self: Self) -> str:
        """Represent as string.

        :return: string representation
        """
        return f"{self.__class__.__name__} {str(self.__id)}"
