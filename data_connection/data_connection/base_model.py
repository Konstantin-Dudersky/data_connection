"""Базовая модель для схемы данных."""

# pyright: reportIncompatibleVariableOverride=false

from typing import Any, Callable, Type
from pydantic import (
    BaseModel as PydanticBaseModel,
    BaseConfig as PydanticBaseConfig,
)

from .field import Field


class BaseModel(PydanticBaseModel):
    """Базовая модель."""

    class Config(PydanticBaseConfig):
        """Конфигурация базовой модели."""

        json_encoders: dict[  # noqa: WPS234
            Type[Field[Any]],
            Callable[[Field[Any]], dict[str, Any]],
        ] = {
            Field: lambda datapoint: datapoint.json_encoder(),
        }
