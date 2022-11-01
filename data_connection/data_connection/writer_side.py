"""Writer side."""

# pyright: reportUnnecessaryIsInstance=false

import datetime as dt
import ipaddress
from typing import Any

from .abstract_side import AbstractSide, TBaseModel, TModelField
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

    def _prepare_send_model(
        self,
        data_xch: TBaseModel,
        data_int: TBaseModel,
        data_ext: TBaseModel,
    ) -> None:
        self.__prepare_send_dict(
            dict_xch=data_xch.dict(),
            dict_int=data_int.dict(),
            dict_ext=data_ext.dict(),
        )

    def _prepare_rcv_model(
        self,
        data_xch: TBaseModel,
        data_int: TBaseModel,
        data_ext: TBaseModel,
    ) -> None:
        self.__prepare_rcv_dict(
            dict_xch=data_xch.dict(),
            dict_int=data_int.dict(),
            dict_ext=data_ext.dict(),
        )

    def __prepare_send_dict(  # noqa: WPS231
        self,
        dict_xch: dict[str, Any],
        dict_int: dict[str, Any],
        dict_ext: dict[str, Any],
    ) -> None:
        field_keys = dict_ext.keys()
        for field_key in field_keys:
            field_xch: TModelField = dict_xch[field_key]
            field_int: TModelField = dict_int[field_key]
            field_ext: TModelField = dict_ext[field_key]
            # try Datapoint
            if (  # noqa: WPS337
                isinstance(field_xch, Datapoint)
                and isinstance(field_int, Datapoint)
                and isinstance(field_ext, Datapoint)
            ):
                DatapointPrepare.send_to_reader_side(
                    field_xch=field_xch,
                    field_int=field_int,
                    field_ext=field_ext,
                )
                continue
            # try BaseModel
            if (  # noqa: WPS337
                isinstance(field_xch, dict)
                and isinstance(field_int, dict)
                and isinstance(field_ext, dict)
            ):
                self.__prepare_send_dict(
                    dict_xch=field_xch,
                    dict_int=field_int,
                    dict_ext=field_ext,
                )
                continue
            raise ValueError(
                "Incrorrect type for field: {0}".format(field_key),
            )

    def __prepare_rcv_dict(  # noqa: WPS231
        self,
        dict_xch: dict[str, Any],
        dict_int: dict[str, Any],
        dict_ext: dict[str, Any],
    ) -> None:
        field_keys = dict_ext.keys()
        for field_key in field_keys:
            field_xch: TModelField = dict_xch[field_key]
            field_int: TModelField = dict_int[field_key]
            field_ext: TModelField = dict_ext[field_key]
            # try Datapoint
            if (  # noqa: WPS337
                isinstance(field_xch, Datapoint)
                and isinstance(field_int, Datapoint)
                and isinstance(field_ext, Datapoint)
            ):
                DatapointPrepare.rcv_from_reader_side(
                    field_xch=field_xch,
                    field_int=field_int,
                    field_ext=field_ext,
                    delay=dt.timedelta(seconds=self.__writer_priority_delay),
                )
                continue
            # try BaseModel
            if (  # noqa: WPS337
                isinstance(field_xch, dict)
                and isinstance(field_int, dict)
                and isinstance(field_ext, dict)
            ):
                self.__prepare_rcv_dict(
                    dict_xch=field_xch,
                    dict_int=field_int,
                    dict_ext=field_ext,
                )
                continue
            raise ValueError(
                "Incrorrect type for field: {0}".format(field_key),
            )
