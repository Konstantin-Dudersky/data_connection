"""Классы datapoint - отдельное значение."""

import datetime as dt
from typing import Any, Callable, Generator, Generic, Self, TypeVar

from pydantic import ValidationError
from pydantic.error_wrappers import ErrorList
from pydantic.fields import ModelField


TField = TypeVar("TField")


class Field(Generic[TField]):  # noqa: WPS214
    """Базовый класс для данных."""

    value_read: TField
    value_write: TField
    ts_read: dt.datetime = dt.datetime.min
    ts_write: dt.datetime = dt.datetime.min

    def __init__(self, default: TField) -> None:
        """Базовый класс для данных.

        Parameters
        ----------
        default: TField
            Начальное значение
        """
        self.value_read = default
        self.value_write = default

    def __repr__(self) -> str:
        """Строковое представление.

        Returns
        -------
        Строковое представление.
        """
        return "Datapoint({0})".format(self.json_encoder())

    @classmethod
    def __get_validators__(
        cls,
    ) -> Generator[Callable[[Self, ModelField], Self], None, None]:
        """Вызывается pydantic.

        Yields
        ------
        _validate
            Генератор для валидации
        """
        yield cls._validate

    @property
    def value(self) -> TField:
        """Значение для считываения клиентской программой.

        Обновляется метка времени чтения.

        Returns
        -------
        Значение
        """
        self.ts_read = dt.datetime.utcnow()
        return self.value_read

    @value.setter
    def value(self, value: TField) -> None:
        """Изменение значения на стороне writer_side.

        Обновляется метка времени записи.

        Parameters
        ----------
        value: TField
            Новое значение
        """
        self.ts_write = dt.datetime.utcnow()
        self.value_write = value  # noqa: WPS601
        self.value_read = value  # noqa: WPS601

    def set_from_reader_side(
        self,
        value: TField,
        ts: dt.datetime | None = None,
    ) -> None:
        """Установить значение со стороны reader_side.

        Parameters
        ----------
        value: TField
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

    def json_encoder(self) -> dict[str, Any]:
        """Кодирование в json.

        Returns
        -------
        Словарь.
        """
        return {
            "read": {
                "value": self.value_read,
                "ts": self.ts_read.isoformat(),
            },
            "write": {
                "value": self.value_write,
                "ts": self.ts_write.isoformat(),
            },
        }

    @classmethod
    def _validate(cls, value: Self, field: ModelField) -> Self:
        if not isinstance(value, cls):
            raise TypeError("Invalid value")
        if not field.sub_fields:
            return value
        dp_type: ModelField = field.sub_fields[0]
        errors: list[ErrorList] = []
        _, error = dp_type.validate(
            v=value.value_write,
            values={},
            loc="aged",
        )
        if error:
            errors.append(error)
        if errors:
            raise ValidationError(
                errors=errors,
                model=cls,  # pyright: ignore[reportGeneralTypeIssues]
            )
        return value


class FieldPrepare(Generic[TField]):
    """Преобразование полей перед отправкой / после получения."""

    @classmethod
    def send_to_writer_side(
        cls,
        field_xch: Field[TField],
        field_int: Field[TField],
        field_ext: Field[TField],
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
        field_xch: Field[TField],
        field_int: Field[TField],
        field_ext: Field[TField],
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
        field_xch: Field[TField],
        field_int: Field[TField],
        field_ext: Field[TField],
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
        field_xch: Field[TField],
        field_int: Field[TField],
        field_ext: Field[TField],
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
