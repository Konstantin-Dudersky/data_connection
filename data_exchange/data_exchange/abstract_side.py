"""Абстрактный класс для передачи данных."""

import asyncio
import ipaddress
from typing import Final

from websockets.legacy import client
from websockets.exceptions import ConnectionClosed
from fastapi import WebSocket
from pydantic import BaseModel

URL: Final[str] = "ws://{host}:{port}{endpoint}"


class AbstractSide(object):
    """Абстрактный класс для передачи данных."""

    __data_ext: BaseModel
    __data_int: BaseModel
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
        self.__data_ext = model.construct()
        self.__data_int = model.construct()
        self.__other_host = other_host
        self.__other_port = other_port
        self.__other_endpoint = other_endpoint
        self.__send_interval = send_interval

    async def ws_server(self, websocket: WebSocket) -> None:
        """Рассылка данных через WebSocket.

        Функция вызывается в FastAPI endpoint

        Parameters
        ----------
        websocket: WebSocket
            объект для работы с протоколом websocket
        """
        await websocket.accept()
        while True:  # noqa: WPS457
            await websocket.send_json(self.__data_ext.json())
            await asyncio.sleep(self.__send_interval)

    async def ws_client(self):
        url: str = URL.format(
            host=self.__other_host,
            port=self.__other_port,
            endpoint=self.__other_endpoint,
        )
        async with client.connect(url) as websocket:
            try:
                async for message in websocket:
                    print(message)
            except ConnectionClosed:
                await asyncio.sleep(1)

    async def task(self):
        await self.ws_client()
