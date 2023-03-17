import pickle

from data_connection import BaseModel, Field


class FullModel(BaseModel):
    test_float: Field[float] = Field[float](0.123)
    test_bool: Field[bool] = Field[bool](False, "rw")
    test_str: Field[str] = Field[str]("")
    test_int: Field[int] = Field[int](12456)


data = FullModel()


def test():
    data_bytes = pickle.dumps(data)
    data_unpicle = FullModel.parse_raw(
        b=data_bytes,
        content_type="application/pickle",
        allow_pickle=True,
    )
    assert data.test_float.value == data_unpicle.test_float.value
    assert data.test_int.value == data_unpicle.test_int.value
