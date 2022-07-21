"""Channel."""

from time import perf_counter_ns
from typing import Generic

from typing_extensions import Self

from .signal import AccessEnum, Signal, Signaltype
from .utils.logger import LoggerLevel, get_logger

log = get_logger(__name__, LoggerLevel.INFO)


class Channel(Generic[Signaltype]):
    """Класс channel."""

    __access: AccessEnum
    __id: int
    __read_ts: int = 0
    __signal: Signal[Signaltype] | None = None
    __write_ts: int = 0

    def __init__(
        self: Self,
        access: AccessEnum,
        debug: bool = False,
    ) -> None:
        """Класс channel.

        :param access: тип доступа
        :param debug: вывод сообщений в лог
        """
        self.__access = access
        if debug:
            log.setLevel(LoggerLevel.DEBUG)
        self.__id = id(self)

    def set_signal_link(self: Self, signal: Signal[Signaltype]) -> None:
        """Установить ссылку из channel на signal.

        :param signal: ссылка на класс signal
        """
        self.__signal = signal

    def _pre_read(self: Self) -> bool:
        if self.__signal is None:
            return False
        if self.__access not in (AccessEnum.READONLY, AccessEnum.READWRITE):
            return False
        if self.__signal.read_ts <= self.__read_ts:
            return False
        log.debug(
            "%s, need to read, read_ts: %s, signal.read_ts: %s",
            repr(self),
            self.__read_ts,
            self.__signal.read_ts,
        )
        return True

    def _post_read(self: Self, value: Signaltype) -> bool:
        if self.__signal is None:
            return False
        log.debug(
            "%s, read, value: %s, read_ts: %s",
            repr(self),
            value,
            self.__read_ts,
        )
        self.__signal.value = value
        self.__read_ts = perf_counter_ns()
        self.__write_ts = perf_counter_ns()
        return True

    def _pre_write(self: Self) -> Signaltype | None:
        if self.__signal is None:
            return None
        if self.__access not in (AccessEnum.WRITEONLY, AccessEnum.READWRITE):
            return None
        if self.__signal.write_ts <= self.__write_ts:
            return None
        log.debug(
            "%s, need to write, write_ts: %s, signal.write_ts: %s",
            repr(self),
            self.__write_ts,
            self.__signal.write_ts,
        )
        return self.__signal.value

    def _post_write(self: Self, value: Signaltype) -> bool:
        self.__write_ts = perf_counter_ns()
        log.debug(
            "%s, write, value: %s, write_ts: %s",
            repr(self),
            value,
            self.__write_ts,
        )
        return True

    def __repr__(self: Self) -> str:
        """Represent as string.

        :return: string representaiton
        """
        return f"{self.__class__.__name__} {str(self.__id)}"
