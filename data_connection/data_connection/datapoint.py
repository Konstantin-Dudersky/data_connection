"""Классы datapoint - отдельное значение."""

import datetime as dt
from dataclasses import dataclass, field
from typing import Generic, Self, TypeVar

__all__: list[str] = [
    "Bool",
    "Datapoint",
    "Float",
    "Int",
    "Str",
]

T = TypeVar("T")  # noqa: WPS111


@dataclass
class Datapoint(Generic[T]):
    """Базовый класс для данных."""

    _value_default: T = field(init=True)
    value_read: T = field(init=False)
    value_write: T = field(init=False)
    ts_read: dt.datetime = field(init=False, default=dt.datetime.min)
    ts_write: dt.datetime = field(init=False, default=dt.datetime.min)

    def __post_init__(self) -> None:
        """Инициалиация."""
        self.value_read = self._value_default
        self.value_write = self._value_default

    @property
    def value(self) -> T:
        """Значение для считываения клиентской программой.

        Обновляется метка времени чтения.

        Returns
        -------
        Значение
        """
        self.ts_read = dt.datetime.utcnow()
        return self.value_read

    @value.setter
    def value(self, value: T) -> None:
        """Изменение значения на стороне writer_side.

        Обновляется метка времени записи.

        Parameters
        ----------
        value: T
            Новое значение
        """
        self.ts_write = dt.datetime.utcnow()
        self.value_write = value  # noqa: WPS601
        self.value_read = value  # noqa: WPS601

    def set_from_reader_side(
        self,
        value: T,
        ts: dt.datetime | None = None,
    ) -> None:
        """Установить значение со стороны reader_side.

        Parameters
        ----------
        value: T
            Новое значение
        ts: dt.datetime
            Опционально - метка времени. Если отсутсвует, подставляется
            время выполнения функции
        """
        self.value_read = value
        self.ts_read = ts if ts else dt.datetime.utcnow()

    def update_read_from(self, other: Self) -> None:
        """Обновить поля чтения.

        Parameters
        ----------
        other: Self
            датапоинт, из которого скопировать данные
        """
        self.value_read = other.value_read
        self.ts_read = other.ts_read

    def update_write_from(self, other: Self) -> None:
        """Обновить поля записи.

        Parameters
        ----------
        other: Self
            датапоинт, из которого скопировать данные
        """
        self.value_write = other.value_write
        self.ts_write = other.ts_write


@dataclass
class Bool(Datapoint[bool]):
    """Значение int."""

    _value_default: bool = field(init=False, default=False)


@dataclass
class Int(Datapoint[int]):
    """Значение int."""

    _value_default: int = field(init=False, default=0)


@dataclass
class Float(Datapoint[float]):
    """Значение float."""

    _value_default: float = field(init=False, default=0.0)  # noqa: WPS358


@dataclass
class Str(Datapoint[str]):
    """Значение int."""

    _value_default: str = field(init=False, default="")


class DatapointPrepare(Generic[T]):
    """Преобразование полей перед отправкой / после получения."""

    @classmethod
    def send_to_writer_side(
        cls,
        field_xch: Datapoint[T],
        field_int: Datapoint[T],
        field_ext: Datapoint[T],
    ) -> None:
        """Подготовка перед передачей reader_side -> writer_side.

        Parameters
        ----------
        field_xch: Datapoint[T]
            Поле из области exchange
        field_int: Datapoint[T]
            Поле из области internal
        field_ext: Datapoint[T]
            Поле из области external
        """
        field_int.update_read_from(field_ext)
        field_xch.update_read_from(field_int)

    @classmethod
    def send_to_reader_side(
        cls,
        field_xch: Datapoint[T],
        field_int: Datapoint[T],
        field_ext: Datapoint[T],
    ) -> None:
        """Подготовка перед передачей writer_side -> reader_side.

        Parameters
        ----------
        field_xch: Datapoint[T]
            Поле из области exchange
        field_int: Datapoint[T]
            Поле из области internal
        field_ext: Datapoint[T]
            Поле из области external
        """
        field_int.update_write_from(field_ext)
        field_xch.update_write_from(field_int)

    @classmethod
    def rcv_from_reader_side(
        cls,
        field_xch: Datapoint[T],
        field_int: Datapoint[T],
        field_ext: Datapoint[T],
        delay: dt.timedelta,
    ) -> None:
        """Подготовка после передачи reader_side -> writer_side.

        Parameters
        ----------
        field_xch: Datapoint[T]
            Поле из области exchange
        field_int: Datapoint[T]
            Поле из области internal
        field_ext: Datapoint[T]
            Поле из области external
        delay: dt.timedelta
            Задержка, в течение которой значение writer_side имеет приоритет
            перед reader_side
        """
        if field_int.ts_write != field_ext.ts_write:
            # значение было изменено пользователем
            if field_xch.ts_read < field_ext.ts_write + delay:
                # задержка приоритета
                return
        field_int.update_read_from(field_xch)
        field_ext.update_read_from(field_int)

    @classmethod
    def rcv_from_writer_side(
        cls,
        field_xch: Datapoint[T],
        field_int: Datapoint[T],
        field_ext: Datapoint[T],
    ) -> None:
        """Подготовка после передачи reader_side -> writer_side.

        Parameters
        ----------
        field_xch: Datapoint[T]
            Поле из области exchange
        field_int: Datapoint[T]
            Поле из области internal
        field_ext: Datapoint[T]
            Поле из области external
        """
        field_int.update_write_from(field_xch)
        field_ext.update_write_from(field_int)
