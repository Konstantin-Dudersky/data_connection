"""Классы datapoint - отдельное значение."""

import datetime as dt
from dataclasses import field
from typing import Any, Generic, TypeVar

from pydantic.dataclasses import dataclass

T = TypeVar("T")  # noqa: WPS111


@dataclass
class DatapointBase(object):
    ts_read: dt.datetime = dt.datetime.min
    ts_write: dt.datetime = dt.datetime.min


@dataclass
class Datapoint(DatapointBase, Generic[T]):
    value_read: T = field(kw_only=True)
    value_write: T = field(kw_only=True)

    @property
    def value(self) -> T:
        self.ts_read = dt.datetime.utcnow()
        return self.value_read

    @value.setter
    def value(self, value: T) -> None:
        self.ts_write = dt.datetime.utcnow()
        self.value_write = value  # noqa: WPS601
        self.value_read = value  # noqa: WPS601


@dataclass
class Float(Datapoint[float]):
    """Значение с плавающей запятой."""

    value_read: float = 0
    value_write: float = 0


@dataclass
class Int(Datapoint[int]):
    """Целочисленное значение."""

    value_read: int = 0
    value_write: int = 0


@dataclass
class DpAny(Datapoint[Any]):
    value_read: Any = field(kw_only=True)
    value_write: Any = field(kw_only=True)


class DatapointProcess(Generic[T]):
    """Преобразование полей перед отправкой / после получения."""

    @classmethod
    def prepare_send_to_writer_side(
        cls,
        field_xch: Datapoint[Any],
        field_int: DpAny,
        field_ext: Datapoint[T],
    ) -> None:
        field_int.value_read = field_ext.value_write
        field_int.ts_read = field_ext.ts_write

        field_xch.value_read = field_int.value_read
        field_xch.ts_read = field_int.ts_read

    @classmethod
    def prepare_send_to_reader_side(
        cls,
        field_xch: Datapoint[T],
        field_int: Datapoint[T],
        field_ext: Datapoint[T],
    ) -> None:
        field_int.value_write = field_ext.value_write
        field_int.ts_write = field_ext.ts_write
        field_xch.value_write = field_int.value_write
        field_xch.ts_write = field_int.ts_write

    @classmethod
    def prepare_rcv_from_reader_side(
        cls,
        field_xch: Datapoint[T],
        field_int: Datapoint[T],
        field_ext: Datapoint[T],
        delay: dt.timedelta,
    ) -> None:
        if (
            field_int.ts_write != field_ext.ts_write
            and field_xch.ts_read < field_ext.ts_write + delay
        ):
            # значение было изменено пользователем
            return

        field_int.value_read = field_xch.value_read
        field_int.ts_read = field_xch.ts_read
        field_ext.value_read = field_int.value_read
        field_ext.ts_read = field_int.ts_read

    @classmethod
    def prepare_rcv_from_writer_side(
        cls,
        field_xch: Datapoint[T],
        field_int: Datapoint[T],
        field_ext: Datapoint[T],
    ) -> None:
        raise NotImplementedError
