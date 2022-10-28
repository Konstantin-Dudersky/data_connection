"""Datapoint."""

from typing import Generic

from typing_extensions import Self

from .channel import Channel
from .signal import Signal, Signaltype


class DpSignal(Generic[Signaltype]):
    """Простой datapoint, содержащий только signal."""

    __signal: Signal[Signaltype]

    def __init__(
        self: Self,
        default: Signaltype,
        channels: tuple[Channel[Signaltype]] | None = None,
    ) -> None:
        """Простой datapoint, содержащий только signal.

        :param default: начальное значение
        :param channels: список связанных объектов channel
        """
        self.__signal = Signal[Signaltype](default=default)
        if channels is not None:
            for channel in channels:
                channel.set_signal_link(self.__signal)

    @property
    def value(self: Self) -> Signaltype:
        """Возвращает значение.

        :return: значение
        """
        return self.__signal.value

    @value.setter
    def value(self: Self, value: Signaltype) -> None:
        """Устанавливает значение.

        :param value: новое значение
        """
        self.__signal.value = value
