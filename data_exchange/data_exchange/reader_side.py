"""Reader side."""

# pyright: reportUnnecessaryIsInstance=false

import datetime as dt
import ipaddress
from typing import Any

from .abstract_side import AbstractSide, TBaseModel
from .datapoint import Datapoint, DatapointPrepare


class ReaderSide(AbstractSide[TBaseModel]):
    """Reader side."""

    __last_get_changes: dt.datetime

    def __init__(
        self,
        model: TBaseModel,
        writer_side_host: ipaddress.IPv4Address,
        writer_side_port: int,
        writer_side_endpoint: str,
        send_to_writer_side_interval: float = 1.0,
    ) -> None:
        """Reader side.

        Parameters
        ----------
        model: TBaseModel
            модель данных pydantic
        writer_side_host: ipaddress.IPv4Address
            Адрес компонента с запущенным websocket-сервером
        writer_side_port: int
            Порт компонента с запущенным websocket-сервером
        writer_side_endpoint: str
            URL компонента с запущенным websocket-сервером
        send_to_writer_side_interval: float
            Задержка между рассылкой сообщений
        """
        super().__init__(
            model=model,
            other_host=writer_side_host,
            other_port=writer_side_port,
            other_endpoint=writer_side_endpoint,
            send_interval=send_to_writer_side_interval,
        )
        self.__last_get_changes = dt.datetime.min

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
            DatapointPrepare.send_to_writer_side(
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
        field_keys = data_ext.dict().keys()
        for field_key in field_keys:
            field_ext: Datapoint[Any] = data_ext.dict()[field_key]
            if not self._is_datapoint(field_ext):
                continue
            field_int: Datapoint[Any] = data_int.dict()[field_key]
            field_xch: Datapoint[Any] = data_xch.dict()[field_key]
            DatapointPrepare.rcv_from_writer_side(
                field_xch=field_xch,
                field_int=field_int,
                field_ext=field_ext,
            )
