"""Простейший channel."""

from typing_extensions import Self

from .channel import Channel
from .signal import Signaltype


class ChannelVirt(Channel[Signaltype]):
    """Простейший channel."""

    @property
    def value(self: Self) -> Signaltype | None:
        """Возвращает значение.

        Считывание означает "запись" в канал.

        :return: значение или None
        """
        _v: Signaltype | None = self._pre_write()
        if _v is None:
            return None
        if not self._post_write(_v):
            return None
        return _v

    @value.setter
    def value(self: Self, value: Signaltype) -> bool:
        """Установить значение.

        Установка значение означает "считывание" канала
        :param value: новое значение
        :return: True , если значение успешно записано
        """
        if not self._pre_read():
            return False
        if not self._post_read(value):
            return False
        return True
