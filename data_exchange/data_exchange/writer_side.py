"""Writer side."""

# pyright: reportUnnecessaryIsInstance=false

import datetime as dt
import ipaddress
from typing import Any

from .abstract_side import AbstractSide, TBaseModel
from .datapoint import Datapoint, DatapointPrepare


class WriterSide(AbstractSide[TBaseModel]):
    """Writer side."""

    __writer_priority_delay: float

    def __init__(
        self,
        model: TBaseModel,
        reader_side_host: ipaddress.IPv4Address,
        reader_side_port: int = 8000,
        reader_side_endpoint: str = "data",
        send_to_reader_side_interval: float = 1.0,
        writer_priority_delay: float = 1.0,
    ) -> None:
        """Writer side.

        Parameters
        ----------
        model: TBaseModel
            модель данных pydantic
        reader_side_host: ipaddress.IPv4Address
            Адрес компонента с запущенным websocket-сервером
        reader_side_port: int
            Порт компонента с запущенным websocket-сервером
        reader_side_endpoint: str
            URL компонента с запущенным websocket-сервером
        send_to_reader_side_interval: float
            Задержка между рассылкой сообщений
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
        data_xch: TBaseModel,
        data_int: TBaseModel,
        data_ext: TBaseModel,
    ) -> None:
        field_keys = data_ext.dict().keys()
        for field_key in field_keys:
            field_ext: Datapoint[Any] = data_ext.dict()[field_key]
            if not isinstance(field_ext, Datapoint):
                raise ValueError("{0} is not Datapoint".format(field_key))
            field_int: Datapoint[Any] = data_int.dict()[field_key]
            if not isinstance(field_int, Datapoint):
                raise ValueError("{0} is not Datapoint".format(field_key))
            field_xch: Datapoint[Any] = data_xch.dict()[field_key]
            DatapointPrepare.send_to_reader_side(
                field_xch=field_xch,
                field_int=field_int,
                field_ext=field_ext,
            )

    def _prepare_rcv(
        self,
        data_xch: TBaseModel,
        data_int: TBaseModel,
        data_ext: TBaseModel,
    ) -> None:
        field_keys = data_xch.dict().keys()
        for field_key in field_keys:
            field_xch: Datapoint[Any] = data_xch.dict()[field_key]
            field_int: Datapoint[Any] = data_int.dict()[field_key]
            field_ext: Datapoint[Any] = data_ext.dict()[field_key]
            DatapointPrepare.rcv_from_reader_side(
                field_xch=field_xch,
                field_int=field_int,
                field_ext=field_ext,
                delay=dt.timedelta(seconds=self.__writer_priority_delay),
            )
