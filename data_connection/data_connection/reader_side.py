"""Reader side."""

# pyright: reportUnnecessaryIsInstance=false

import ipaddress
from typing import Any

from .abstract_side import AbstractSide, TBaseModel, TModelField
from .field import Field, FieldPrepare


class ReaderSide(AbstractSide[TBaseModel]):
    """Reader side."""

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
                isinstance(field_xch, Field)
                and isinstance(field_int, Field)
                and isinstance(field_ext, Field)
            ):
                FieldPrepare.send_to_writer_side(
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
                isinstance(field_xch, Field)
                and isinstance(field_int, Field)
                and isinstance(field_ext, Field)
            ):
                FieldPrepare.rcv_from_writer_side(
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
                self.__prepare_rcv_dict(
                    dict_xch=field_xch,
                    dict_int=field_int,
                    dict_ext=field_ext,
                )
                continue
            raise ValueError(
                "Incrorrect type for field: {0}".format(field_key),
            )
