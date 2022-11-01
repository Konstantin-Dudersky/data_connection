"""Чтение данных по OPC UA."""

import asyncio
import logging
from time import perf_counter_ns
from typing import Any, Final, Generic, Iterable, TypeVar

from asyncua.client.client import Client
from asyncua.common.node import Node
from asyncua.ua import DataValue, Variant, VariantType
from asyncua.ua.uaerrors import UaStatusCodeError

from ..datapoint import Datapoint

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

TDatapoint = TypeVar("TDatapoint", bound=Datapoint[Any])

NS_IN_MS: Final[float] = 1000000


class DatapointOpcUA(Generic[TDatapoint]):
    __datapoint: Datapoint[TDatapoint]
    __node_id: str
    __node: Node | None

    def __init__(
        self,
        datapoint: Datapoint[TDatapoint],
        node_id: str,
    ) -> None:
        self.__datapoint = datapoint
        self.__node_id = node_id
        self.__node = None

    async def read(self) -> None:
        """Прочитать значение."""
        if not self.__node:
            return
        value: TDatapoint = (
            await self.__node.read_value()
        )  # pyright: reportUnknownMemberType=false
        self.__datapoint.set_from_reader_side(value)

    async def write(self) -> None:
        """Записать значение."""
        pass

    @property
    def node_id(self) -> str:
        """Возвращает идентификатор узла.

        Returns
        -------
        Идентификатор узла
        """
        return self.__node_id

    def node(self, node: Node) -> None:
        """Задать узел из OPC UA клиента.

        Parameters
        ----------
        node: Node
            Узел
        """
        self.__node = node


class Reader(object):
    __url: str
    __session_timeout: int
    __debug_perf: bool
    __datapoints: Iterable[DatapointOpcUA[Any]]

    def __init__(
        self,
        url: str,
        session_timeout: int = 30000,
        debug_perf: bool = False,
        datapoints: Iterable[DatapointOpcUA[Any]] | None = None,
    ) -> None:
        """Подключение к OPC UA.

        Parameters
        ----------
        url: str
            Строка подключения к OPC UA серверу
        session_timeout: int
            Таймаут сессии
        debug_perf: bool
            True - выводить время цикла
        """
        if not datapoints:
            raise ValueError("OPC UA datapoint list empty")
        self.__url = url
        self.__session_timeout = session_timeout
        self.__debug_perf = debug_perf
        self.__client = Client(url=self.__url, timeout=2)
        self.__client.session_timeout = session_timeout
        self.__datapoints = datapoints
        for datapoint in self.__datapoints:
            node: Node = self.__client.get_node(datapoint.node_id)
            datapoint.node(node=node)

    async def task(self) -> None:
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
                    log.exception("opc ua connection error: {0}".format(exc))
            self.__ready = False
            await asyncio.sleep(5)

    async def __task(self) -> None:
        begin_time: int = perf_counter_ns()
        # for datapoint in self.__datapoints:
        #     await datapoint.write()
        for datapoint in self.__datapoints:
            await datapoint.read()
        self.__ready = True
        end_time: int = perf_counter_ns()
        if self.__debug_perf:
            log.info(
                "Plc task cycle time: {0:.2f} ms".format(
                    (end_time - begin_time) / NS_IN_MS,
                ),
            )
