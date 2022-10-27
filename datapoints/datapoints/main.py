import datetime as dt
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


@dataclass
class DatapointFloatDc:
    __read_value: float = 0.0
    __write_value: float = 0.0
    __read_ts: dt.datetime = dt.datetime.min
    __write_ts: dt.datetime = dt.datetime.min

    @property
    def value(self) -> float:
        self.__read_ts = dt.datetime.utcnow()
        return self.__read_value

    @value.setter
    def value(self, value: float) -> None:
        self.__write_ts = dt.datetime.utcnow()
        self.__write_value = value

    @property
    def read_ts(self) -> dt.datetime:
        return self.__read_ts

    @property
    def write_ts(self) -> dt.datetime:
        return self.__write_ts


class DatapointFloat(BaseModel):
    __value: float = 0.0
    read_ts: dt.datetime = dt.datetime.utcnow()
    write_ts: dt.datetime = dt.datetime.utcnow()

    @property
    def value(self):
        return self.__value

    def set_value(self, value: float):
        self.__value = value

    # class Config:
    #     underscore_attrs_are_private = True


class Data(BaseModel):
    data_1: DatapointFloatDc = DatapointFloatDc()
    data_2: DatapointFloatDc = DatapointFloatDc()


data = Data.construct()
data.data_1.value = 34
print(data)
