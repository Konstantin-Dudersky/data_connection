from typing import Any, Callable, Type
from pydantic import BaseModel

# from data_connection.datapoint import Bool, Float, Int, Str, Datapoint
from data_connection.datapoint import Datapoint


# class InnerModel(BaseModel):
#     test_int: Int = Int()
#     test_wstring: Str = Str()


class DataModel(BaseModel):
    test_float: Datapoint[float] = Datapoint[float](0)
    # test_bool: Bool = Bool()
    # test_str: Str = Str()
    # inner: InnerModel = InnerModel()

    class Config:
        json_encoders: dict[
            Type[Datapoint[Any]],
            Callable[[Datapoint[Any]], dict[str, Any]],
        ] = {
            Datapoint: lambda datapoint: datapoint.json_encoder(),
        }
