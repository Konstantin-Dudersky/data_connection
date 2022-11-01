from pydantic import BaseModel

from data_connection.datapoint import Bool, Float, Int, Str, Datapoint


class InnerModel(BaseModel):
    test_int: Int = Int()
    test_wstring: Str = Str()


class DataModel(BaseModel):
    test_float: Datapoint[float] = Datapoint[float](0)
    test_bool: Bool = Bool()
    test_str: Str = Str()
    inner: InnerModel = InnerModel()
