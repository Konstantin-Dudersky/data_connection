from pydantic import BaseModel

from data_connection.datapoint import Float


class DataModel(BaseModel):
    test_dp1: Float = Float()
    test_dp2: Float = Float()
