from typing import Any, Callable, Type
from pydantic import BaseModel

from data_connection.datapoint import Datapoint


class InnerModel(BaseModel):
    test_int: Datapoint[int] = Datapoint[int](0)
    test_wstring: Datapoint[str] = Datapoint[str]("")


class DataModel(BaseModel):
    test_float: Datapoint[float] = Datapoint[float](0.1)
    test_bool: Datapoint[bool] = Datapoint[bool](False)
    test_str: Datapoint[str] = Datapoint[str]("")
    inner: InnerModel = InnerModel()

    class Config:
        json_encoders: dict[
            Type[Datapoint[Any]],
            Callable[[Datapoint[Any]], dict[str, Any]],
        ] = {
            Datapoint: lambda datapoint: datapoint.json_encoder(),
        }
