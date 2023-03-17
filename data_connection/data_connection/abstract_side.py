"""Абстрактный класс для передачи данных."""

# pyright: reportUnusedFunction=false

import asyncio
import ipaddress
import logging
import pickle  # noqa: S403
from time import perf_counter_ns
from typing import Any, Final, Generic, Iterable, TypeVar

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK
from websockets.legacy import client

from .field import Field

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.INFO)

NS_IN_S: Final[float] = 1e9
URL: Final[str] = "ws://{host}:{port}{endpoint}"
TBaseModel = TypeVar("TBaseModel", bound=BaseModel)
TModelField = Field[Any] | dict[str, Any]


def isinstance_iterable(
    __obj: Iterable[TModelField],
    __class_or_tuple: type,
) -> bool:
    """Все элементы последовательности соответстуют типу.

    Parameters
    ----------
    __obj: Iterable[TModelField]
        Последовательность объектов
    __class_or_tuple: type
        Тип для проверки

    Returns
    -------
    True - все элементы соответсвуют
    """
    for __obj_item in __obj:
        if not isinstance(__obj_item, __class_or_tuple):
            return False
    return True


class AbstractSide(Generic[TBaseModel]):  # noqa: WPS214
    """Абстрактный класс для передачи данных."""

    __data_ext: TBaseModel
    __data_int: TBaseModel
    __model: TBaseModel
    __send_interval: float
    __other_host: ipaddress.IPv4Address
    __other_port: int
    __other_endpoint: str

    def __init__(
        self,
        model: TBaseModel,
        other_host: ipaddress.IPv4Address,
        other_port: int,
        other_endpoint: str,
        send_interval: float = 1.0,
    ) -> None:
        """Абстрактный класс для передачи данных.

        Parameters
        ----------
        model: TBaseModel
            модель данных pydantic
        other_host: ipaddress.IPv4Address
            Адрес компонента с запущенным websocket-сервером
        other_port: int
            Порт компонента с запущенным websocket-сервером
        other_endpoint: str
            URL компонента с запущенным websocket-сервером
        send_interval: float
            Задержка между рассылкой сообщений
        """
        self.__model: TBaseModel = model
        self.__other_host = other_host
        self.__other_port = other_port
        self.__other_endpoint = other_endpoint
        self.__send_interval = send_interval
        self.__data_ext = self.__model.construct()
        self.__data_int = self.__model.construct()

    @property
    def data(self) -> TBaseModel:  # noqa: WPS110
        """Данные.

        Returns
        -------
        Данные
        """
        return self.__data_ext

    def configure_fastapi(
        self,
        api: FastAPI,
        endpoint_status: str = "/data/status",
        endpoint_ws: str = "/data/ws",
    ) -> None:
        """Сконфигурировать FastAPI.

        Parameters
        ----------
        api: FastAPI
            Приложение FastAPI
        endpoint_status: str
            Адрес для доступа к состоянию данных
        endpoint_ws: str
            Адрес для подключения протокола websocket
        """

        @api.get(endpoint_status)
        def status() -> TBaseModel:
            return self.data

        @api.websocket(endpoint_ws)
        async def ws(websocket: WebSocket) -> None:
            await self._ws_server(websocket)

    async def task(self) -> None:
        """Асинхронная задача для добавления в группу задач."""
        await self._ws_client()

    async def _ws_server(self, websocket: WebSocket) -> None:
        """Рассылка данных через WebSocket.

        Функция вызывается в FastAPI endpoint

        Parameters
        ----------
        websocket: WebSocket
            объект для работы с протоколом websocket, созданный fastapi.
        """
        await websocket.accept()
        log.info("connection open with client: {0}".format(websocket.client))
        while True:  # noqa: WPS457
            begin: int = perf_counter_ns()
            data_xch: TBaseModel = self.__model.construct()
            self._prepare_send_model(
                data_xch=data_xch,
                data_int=self.__data_int,
                data_ext=self.__data_ext,
            )
            try:
                await websocket.send_bytes(pickle.dumps(data_xch))
            except ConnectionClosedOK:
                log.info(
                    "connection closed from client: {0}".format(
                        websocket.client,
                    ),
                )
                break
            end: int = perf_counter_ns()
            await asyncio.sleep(self.__send_interval - (end - begin) / NS_IN_S)

    async def _ws_client(self) -> None:

        """Получение данных через WebSocket."""
        url: str = URL.format(
            host=self.__other_host,
            port=self.__other_port,
            endpoint=self.__other_endpoint,
        )
        websocket_client = client.connect(url)
        websocket_client.BACKOFF_MAX = 10
        async for websocket in websocket_client:
            try:
                async for message in websocket:
                    msg_model: TBaseModel = self.__model.parse_raw(
                        b=message,
                        content_type="application/pickle",
                        allow_pickle=True,
                    )
                    log.debug("recieved message: {0}".format(msg_model))
                    self._prepare_rcv_model(
                        data_xch=msg_model,
                        data_int=self.__data_int,
                        data_ext=self.__data_ext,
                    )
            except ConnectionClosed:
                await asyncio.sleep(1)

    def _prepare_send_model(
        self,
        data_xch: TBaseModel,
        data_int: TBaseModel,
        data_ext: TBaseModel,
    ) -> None:
        raise NotImplementedError

    def _prepare_rcv_model(
        self,
        data_xch: TBaseModel,
        data_int: TBaseModel,
        data_ext: TBaseModel,
    ) -> None:
        raise NotImplementedError

    def _field_to_datapoint(
        self,
        field: Field[Any] | Any,
    ) -> Field[Any] | None:
        if not isinstance(field, Field):
            return None
        return field
