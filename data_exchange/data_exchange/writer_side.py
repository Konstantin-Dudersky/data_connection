import datetime as dt
import ipaddress
from typing import Any

from pydantic import BaseModel

from .abstract_side import AbstractSide
from .datapoint import DatapointBase, DatapointProcess, Datapoint, DpAny


class WriterSide(AbstractSide):
    """Writer side."""

    __writer_priority_delay: float

    def __init__(
        self,
        model: BaseModel,
        reader_side_host: ipaddress.IPv4Address,
        reader_side_port: int = 8000,
        reader_side_endpoint: str = "data",
        send_to_reader_side_interval: float = 1.0,
        writer_priority_delay: float = 1.0,
    ) -> None:
        """Writer side.

        Parameters
        ----------
        writer_priority_delay: float
            Время в [с]. Если значение поменялось из программы пользователя,
            то на указанное время значение из _write_value будет иметь более
            высокий приоритер, чем _reader_side
        """
        super().__init__(
            model=model,
            other_host=reader_side_host,
            other_port=reader_side_port,
            other_endpoint=reader_side_endpoint,
            send_interval=send_to_reader_side_interval,
        )
        self.__writer_priority_delay = writer_priority_delay

    def _prepare_send(
        self,
        data_xch: BaseModel,
        data_ext: BaseModel,
        data_int: BaseModel,
    ) -> None:
        field_keys = data_ext.dict().keys()
        for field_key in field_keys:
            field_ext: Any = data_ext.dict()[field_key]
            if not isinstance(field_ext, DpAny):
                raise ValueError("{0} is not Datapoint".format(field_key))
            field_int: Any = data_int.dict()[field_key]
            if not isinstance(field_int, DpAny):
                raise ValueError("{0} is not Datapoint".format(field_key))
            field_xch: DpAny = data_xch.dict()[field_key]
            DatapointProcess.prepare_send_to_reader_side(
                field_xch=field_xch,
                field_int=field_int,
                field_ext=field_ext,
            )

    def _prepare_rcv(
        self,
        data_rcv: BaseModel,
        data_int: BaseModel,
        data_ext: BaseModel,
    ) -> None:
        field_keys = data_rcv.dict().keys()
        for field_key in field_keys:
            field_xch: DatapointBase = data_rcv.dict()[field_key]
            field_int: DatapointBase = data_int.dict()[field_key]
            field_ext: DatapointBase = data_ext.dict()[field_key]
            DatapointProcess.prepare_rcv_from_reader_side(
                field_xch=field_xch,
                field_int=field_int,
                field_ext=field_ext,
                delay=dt.timedelta(seconds=self.__writer_priority_delay),
            )
