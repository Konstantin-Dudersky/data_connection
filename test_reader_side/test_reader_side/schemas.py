from pydantic import BaseModel

from data_connection.datapoint import Bool, Float, Int, Str


class InnerModel(BaseModel):
    test_idp: Int = Int()


class DataModel(BaseModel):
    test_dp1: Float = Float()
    test_dp2: Bool = Bool()
    test_dp3: Str = Str()
    inner: InnerModel = InnerModel()
