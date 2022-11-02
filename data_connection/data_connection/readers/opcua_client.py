"""OPC UA клиент для чтения / записи данных с OPC UA сервера."""

import asyncio
import datetime as dt
import logging
from time import perf_counter_ns
from typing import Any, Callable, Coroutine, Final, Generic, Iterable

from asyncua.client.client import Client
from asyncua.common.node import Node
from asyncua.ua import DataValue, Variant, VariantType
from asyncua.ua.uaerrors import UaStatusCodeError, BadTypeMismatch

from ..datapoint import Datapoint as DatapointComm, TDatapoint

__all__: list[str] = [
    "Datapoint",
    "Reader",
]

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.INFO)


NS_IN_S: Final[float] = 1e9

# предупреждение о превышении цикла
CYCLE_TOO_LONG_RATE: Final[float] = 0.8

MSG_CYCLE_TOO_LONG: Final[
    str
] = """Communication cycle too long:
actual: {actual:.2f} ms
max: {max:.2f} ms"""

MSG_WRONG_TYPE: Final[
    str
] = """Incorrect type of value in datapoint:
{datapoint}
requested opc ua type: {variant_type}"""


class Datapoint(Generic[TDatapoint]):
    """Датапоинт для доступа к OPC UA."""

    __datapoint: DatapointComm[TDatapoint]
    __node_id: str
    __node: Node | None
    __last_ts_write: dt.datetime

    def __init__(
        self,
        datapoint: DatapointComm[TDatapoint],
        node_id: str,
    ) -> None:
        """Датапоинт для доступа к OPC UA.

        Parameters
        ----------
        datapoint: BaseDatapoint[TDatapoint],
            Ссылка на датапойнт из модели данных
        node_id: str
            Адрес узла в OPC UA
        """
        self.__datapoint = datapoint
        self.__node_id = node_id
        self.__node = None
        self.__last_ts_write = dt.datetime.min

    async def read(self) -> None:
        """Прочитать значение."""
        if not self.__node:
            return
        value: TDatapoint = (
            await self.__node.read_value()
        )  # pyright: reportUnknownMemberType=false
        self.__datapoint.set_from_reader_side(value)

    async def write(self) -> None:
        """Записать значение.

        Raises
        ------
        TypeError
             - неизвестный тип
        ValueError
            - тип данных в OPC UA сервере не соответсвует типу данных python
        """
        if not self.__node:
            return
        if self.__datapoint.ts_write <= self.__last_ts_write:
            return
        variant_type: VariantType | None = None
        match self.__datapoint.value_write:
            case bool():
                variant_type = VariantType.Boolean
            case int():
                variant_type = VariantType.Int16
            case str():
                variant_type = VariantType.String
            case float():
                variant_type = VariantType.Float
            case _:
                raise TypeError(
                    "Unknown type for datapoint: {0}".format(self.__datapoint),
                )
        try:
            await self.__node.write_value(
                DataValue(
                    Value=Variant(
                        Value=self.__datapoint.value_write,
                        VariantType=variant_type,
                    ),
                ),
            )
        except BadTypeMismatch:  # pyright: ignore
            raise ValueError(
                MSG_WRONG_TYPE.format(
                    datapoint=self.__datapoint,
                    variant_type=variant_type,
                ),
            )
        self.__last_ts_write = self.__datapoint.ts_write

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


def _handle_connection_exceptions(
    func: Callable[["Reader"], Coroutine[None, None, None]],
) -> Callable[["Reader"], Coroutine[None, None, None]]:
    """Декоратор для обработки ошибок связи.

    Parameters
    ----------
    func: Callable
        Функция для оборачивания в декоратор

    Returns
    -------
    Функция, обернутая в декоратор
    """

    async def inner(ref: "Reader") -> None:
        error: str = ""
        try:  # noqa: WPS225
            await func(ref)
        except ConnectionError:
            error = "opc ua connection error: ConnectionError"
        except OSError:
            error = "opc ua connection error: OSError"
        except asyncio.exceptions.TimeoutError:
            error = "opc ua connection: TimeoutError"
        except UaStatusCodeError as exc:  # type: ignore
            error = "opc ua connection error: {0}".format(exc)
        if ref.ready:
            log.error(error)
            ref.ready = False
        await asyncio.sleep(5)

    return inner


class Reader(object):
    """Подключение к OPC UA серверу."""

    __url: str
    __debug_comm_cycle: bool
    __datapoints: Iterable[Datapoint[Any]]
    __comm_cycle: float
    ready: bool

    def __init__(
        self,
        url: str,
        session_timeout: int = 30000,
        debug_comm_cycle: bool = False,
        datapoints: Iterable[Datapoint[Any]] | None = None,
        comm_cycle: float = 1,
    ) -> None:
        """Подключение к OPC UA серверу.

        Parameters
        ----------
        url: str
            Строка подключения к OPC UA серверу
        session_timeout: int
            Таймаут сессии, [с]
        debug_perf: bool
            True - выводить время цикла
        datapoints: Iterable[DatapointOpcUA[Any]]
            Перечень точек для опроса
        comm_cycle: float
            Период обмена данными с устройством, [c]

        Raises
        ------
        ValueError
            - пустой перечень точек
        """
        if not datapoints:
            raise ValueError("OPC UA datapoint list empty")
        self.__url = url
        self.__debug_comm_cycle = debug_comm_cycle
        self.__client = Client(url=self.__url, timeout=2)
        self.__client.session_timeout = (  # pyright: ignore
            session_timeout * 1000
        )
        self.__datapoints = datapoints
        for datapoint in self.__datapoints:
            node: Node = self.__client.get_node(datapoint.node_id)
            datapoint.node(node=node)
        self.ready = True
        self.__comm_cycle = comm_cycle

    async def task(self) -> None:
        """Асинхронная задача для коммуникации."""
        while True:  # noqa: WPS457
            await self.__task()

    @_handle_connection_exceptions
    async def __task(self) -> None:
        async with self.__client:
            while True:  # noqa: WPS457
                begin_time: int = perf_counter_ns()
                await self.__task_read_write()
                end_time: int = perf_counter_ns()
                await self.__task_sleep(begin_time, end_time)

    async def __task_read_write(self) -> None:
        """Чтение / запись данных."""
        log.debug("Start comm cycle")
        for dp_write in self.__datapoints:
            await dp_write.write()
        for dp_read in self.__datapoints:
            await dp_read.read()
        self.ready = True
        log.debug("End comm cycle")

    async def __task_sleep(self, begin_time: int, end_time: int) -> None:
        """Ожидание после окончания коммуникации, перед следующим вызовом.

        Parameters
        ----------
        begin_time: int
            Начало коммуникации
        end_time: int
            Конец коммуникации
        """
        comm_cycle_actual: float = (end_time - begin_time) / NS_IN_S
        if self.__debug_comm_cycle:
            log.info(
                "Comm cycle time: {0:.2f} ms".format(
                    comm_cycle_actual * 1000,
                ),
            )
        if comm_cycle_actual > CYCLE_TOO_LONG_RATE * self.__comm_cycle:
            log.warning(
                MSG_CYCLE_TOO_LONG.format(
                    actual=comm_cycle_actual * 1000,
                    max=self.__comm_cycle * 1000,
                ),
            )
        await asyncio.sleep(max(self.__comm_cycle - comm_cycle_actual, 0))
