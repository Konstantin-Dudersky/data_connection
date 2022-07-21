"""OPC UA channel."""

# pyright: reportGeneralTypeIssues=false
# pyright: reportUnknownMemberType=false

import asyncio
from asyncio import sleep as asleep
from time import perf_counter_ns
from typing import Any

from asyncua.client.client import Client
from asyncua.common.node import Node
from asyncua.ua import DataValue, Variant, VariantType
from asyncua.ua.uaerrors import UaStatusCodeError

from typing_extensions import Self


from .channel import Channel
from .signal import AccessEnum, Signaltype
from .utils.logger import LoggerLevel, get_logger


log = get_logger(__name__, LoggerLevel.INFO)


class ChannelOpcUa(Channel[Signaltype]):
    """Channel for opc ua."""

    __node_id: str
    __node: Node | None = None

    def __init__(
        self: Self,
        node_id: str,
        access: AccessEnum,
        debug: bool = False,
    ) -> None:
        """Channel for opc ua.

        :param node_id: node id opc ua item
        :param access: тип доступа
        :param debug: вывод сообщений в лог
        """
        super().__init__(access, debug)
        self.__node_id = node_id

    def set_client(self: Self, client: Client) -> None:
        """Инициализировать Node.

        :param client: ссылка на клиента
        """
        self.__node = client.get_node(self.__node_id)

    async def read(self: Self) -> bool:
        """Читает значение из ПЛК.

        :return: данные считаны
        """
        if not self._pre_read() or self.__node is None:
            return await asleep(0, False)
        value: Signaltype = await self.__node.read_value()
        if not self._post_read(value):
            return await asleep(0, False)
        return await asleep(0, True)

    async def write(self: Self) -> bool:
        """Записывает значение в ПЛК.

        :raises TypeError: неизвестный тип данных сигнала
        :return: данные записаны
        """
        if self.__node is None:
            return await asleep(0, False)
        value: Signaltype | None = self._pre_write()
        match value:
            case bool():
                variant_type: VariantType = VariantType.Boolean
            case int():
                variant_type: VariantType = VariantType.Int16
            case str():
                variant_type: VariantType = VariantType.String
            case None:
                return await asleep(0, False)
            case _:
                raise TypeError(
                    (f"{repr(self)}, неизвестрый тип: " f"{value}"),
                )

        await self.__node.write_value(
            DataValue(Value=Variant(value, variant_type)),
        )
        if not self._post_write(value):
            return await asleep(0, False)
        return await asleep(0, True)


class DriverOpcUa:
    """Driver for OPC UA client."""

    __url: str
    __client: Client
    __ready: bool = True
    __debug_perf: bool
    __items: list[ChannelOpcUa[Any]] = []

    def __init__(
        self: Self,
        url: str,
        session_timeout: int = 30000,
        debug_perf: bool = False,
    ) -> None:
        """Create PLC object.

        :param url: строка подключения к OPC UA серверу
        :param session_timeout: таймаут сессии
        :param debug_perf: True - выводить время цикла
        """
        self.__url = url
        self.__client = Client(url=self.__url, timeout=2)
        self.__client.session_timeout = session_timeout
        self.__debug_perf = debug_perf

    @property
    def ready(self: Self) -> bool:
        """PLC готов для работы.

        :return: True - plc готов
        """
        return self.__ready

    def add(
        self: Self,
        channel: ChannelOpcUa[Any],
    ) -> ChannelOpcUa[Any]:
        """Добавить channel.

        :param channel: добавить channel к driver
        :return: обновленный channel
        """
        channel.set_client(self.__client)
        self.__items.append(channel)
        return channel

    async def task(self: Self) -> None:
        """Задача для коммуникации."""
        while True:
            try:
                async with self.__client:
                    while True:
                        await self.__task()
            except ConnectionError:
                if self.__ready:
                    log.exception("opc ua connection error: ConnectionError")
            except OSError:
                if self.__ready:
                    log.exception("opc ua connection error: OSError")
            except asyncio.exceptions.TimeoutError:
                if self.__ready:
                    log.exception("opc ua connection: TimeoutError")
            except UaStatusCodeError as exc:  # type: ignore
                if self.__ready:
                    log.exception("opc ua connection error: %s", exc)
            self.__ready = False
            await asleep(5)

    async def __task(self: Self) -> None:
        begin_time: int = perf_counter_ns()
        for item in self.__items:
            await item.write()
        for item in self.__items:
            await item.read()
        self.__ready = True
        end_time: int = perf_counter_ns()
        if self.__debug_perf:
            log.info(
                "Plc task cycle time: %.2f ms",
                (end_time - begin_time) / 1000000.0,
            )
