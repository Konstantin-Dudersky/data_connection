from pydantic import BaseModel


class DataModel(BaseModel):
    test_bool: bool = False
    test_int: int = 0


data = DataModel.construct()
