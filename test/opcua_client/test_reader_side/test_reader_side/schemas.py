from data_connection import BaseModel, Field


class InnerModel(BaseModel):
    test_int: Field[int] = Field[int](0)
    test_wstring: Field[str] = Field[str]("")


class DataModel(BaseModel):
    test_float: Field[float] = Field[float](0.1)
    test_bool: Field[bool] = Field[bool](False)
    test_str: Field[str] = Field[str]("")
    inner: InnerModel = InnerModel()
