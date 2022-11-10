"""Modbus TCP клиент для чтения / записи данных с Modbus TCP сервера."""

from typing import Generic

from ..field import TField


class Field(Generic[TField]):
    """Один регистр для чтения / записи."""


class FieldGroup(Generic[TField]):
    """Группировка региситров для запроса."""
