"""Абстрактный класс для передачи данных."""

import asyncio
import ipaddress
import logging
from typing import Final

from fastapi import WebSocket
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK
from websockets.legacy import client

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

URL: Final[str] = "ws://{host}:{port}{endpoint}"


class AbstractSide(object):
    """Абстрактный класс для передачи данных."""

    __data_ext: BaseModel
    __data_int: BaseModel
    __model: BaseModel
    __send_interval: float
    __other_host: ipaddress.IPv4Address
    __other_port: int
    __other_endpoint: str

    def __init__(
        self,
        model: BaseModel,
        other_host: ipaddress.IPv4Address,
        other_port: int,
        other_endpoint: str,
        send_interval: float = 1.0,
    ) -> None:
        """Абстрактный класс для передачи данных.

        Parameters
        ----------
        model: BaseModel
            модель данных pydantic
        send_interval: float
            задержка между рассылкой сообщений
        """
        self.__data_ext = model
        self.__data_int = model.construct()
        self.__other_host = other_host
        self.__other_port = other_port
        self.__other_endpoint = other_endpoint
        self.__send_interval = send_interval
        self.__model = model

    async def ws_server(self, websocket: WebSocket) -> None:
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
            data_rcv: BaseModel = self.__model.construct()
            self._prepare_send(
                data_rcv,
                self.__data_ext,
                self.__data_int,
            )
            try:
                await websocket.send_text(data_rcv.json(by_alias=True))
            except ConnectionClosedOK:
                log.info(
                    "connection closed from client: {0}".format(
                        websocket.client,
                    ),
                )
                break
            await asyncio.sleep(self.__send_interval)

    async def ws_client(self) -> None:
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
                    log.debug("recieved message: {0}".format(message))
                    msg_model = self.__model.parse_raw(message)
                    self._prepare_rcv(
                        data_rcv=msg_model,
                        data_int=self.__data_int,
                        data_ext=self.__data_ext,
                    )
            except ConnectionClosed:
                await asyncio.sleep(1)

    async def task(self) -> None:
        """Асинхронная задача для добавления в группу задач."""
        await self.ws_client()

    def _prepare_send(
        self,
        data_xch: BaseModel,
        data_ext: BaseModel,
        data_int: BaseModel,
    ) -> None:
        raise NotImplementedError

    def _prepare_rcv(
        self,
        data_rcv: BaseModel,
        data_int: BaseModel,
        data_ext: BaseModel,
    ) -> None:
        raise NotImplementedError
