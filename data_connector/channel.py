import asyncio
from asyncio import sleep as asleep
from time import perf_counter_ns
from typing import Any, Coroutine, Generic

from typing_extensions import Self

from .signals import AccessEnum, Signal, SignalType

from .utils.logger import LoggerLevel, get_logger

log = get_logger(__name__, LoggerLevel.DEBUG)


class ChannelItem(Generic[SignalType]):

    __access: AccessEnum
    __id: int
    __read_ts: int = 0
    __signal: Signal[SignalType] | None = None
    __write_ts: int = 0

    def __init__(
        self: Self,
        access: AccessEnum,
        debug: bool = False,
    ) -> None:
        """Базовый класс для данных OPC UA.

        :param access: тип доступа
        :param debug: вывод сообщений в лог
        """
        self.__access = access
        if debug:
            log.setLevel(LoggerLevel.DEBUG)
        self.__id = id(self)

    def _pre_read(self: Self) -> bool:
        if self.__signal is None:
            return False
        if self.__access not in (AccessEnum.READONLY, AccessEnum.READWRITE):
            return False
        if self.__signal.read_ts <= self.__read_ts:
            return False
        log.debug(
            "%s, need to read, read_ts: %s, signal.read_ts: %s",
            repr(self),
            self.__read_ts,
            self.__signal.read_ts,
        )
        return True

    def _post_read(self: Self, value: SignalType) -> bool:
        if self.__signal is None:
            return False
        log.debug(
            "%s, read, value: %s, read_ts: %s",
            repr(self),
            value,
            self.__read_ts,
        )
        self.__signal.value = value
        self.__read_ts = perf_counter_ns()
        self.__write_ts = perf_counter_ns()
        return True

    def set_signal_link(self: Self, signal: Signal[SignalType]) -> None:
        """_summary_

        :param signal: ссылка на класс signal
        """
        self.__signal = signal

    def _pre_write(self: Self) -> SignalType | None:
        if self.__signal is None:
            return None
        if self.__access not in (AccessEnum.WRITEONLY, AccessEnum.READWRITE):
            return None
        if self.__signal.write_ts <= self.__write_ts:
            return None
        log.debug(
            "%s, need to write, write_ts: %s, signal.write_ts: %s",
            repr(self),
            self.__write_ts,
            self.__signal.write_ts,
        )
        return self.__signal.value

    def _post_write(self: Self, value: SignalType) -> bool:
        self.__write_ts = perf_counter_ns()
        log.debug(
            "%s, write, value: %s, write_ts: %s",
            repr(self),
            value,
            self.__write_ts,
        )
        return True

    def __repr__(self: Self) -> str:
        """Represent as string.

        :return: string representaiton
        """
        return f"{self.__class__.__name__} {str(self.__id)}"


from asyncua.client.client import Client
from asyncua.common.node import Node
from asyncua.ua import DataValue, Variant, VariantType
from asyncua.ua.uaerrors import UaStatusCodeError


class OpcUaItem(ChannelItem[SignalType]):
    __node_id: str
    __node: Node | None = None

    def __init__(
        self: Self,
        node_id: str,
        access: AccessEnum,
        debug: bool = False,
    ) -> None:
        """

        :param node_id: node id opc ua item
        :param access: тип доступа
        :param debug: вывод сообщений в лог
        """
        super().__init__(access, debug)
        self.__node_id = node_id

    def init_item(self: Self, client: Client) -> None:
        self.__node = client.get_node(self.__node_id)

    async def read(self: Self) -> bool:
        """Читает значение из ПЛК.

        :return: данные считаны
        """
        if not self._pre_read() or self.__node is None:
            return await asleep(0, False)
        value: SignalType = await self.__node.read_value()
        if not self._post_read(value):
            return await asleep(0, False)
        return await asleep(0, True)

    async def write(self: Self) -> bool:
        """Записывает значение в ПЛК.

        :raises TypeError: неизвестный тип данных сигнала
        :return: данные записаны
        """
        value: SignalType | None = self._pre_write()
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


class OpcUaChannel:

    __url: str
    __client: Client
    __ready: bool = True
    __debug_perf: bool
    __items: list[OpcUaItem[Any]] = []

    def __init__(
        self: Self,
        url: str,
        # runner: TaskRunner,
        atasks: list[Coroutine[Any, Any, None]],
        debug_perf: bool = False,
    ) -> None:
        """Create PLC object.

        :param url: строка подключения к OPC UA серверу
        :param runner: ссылка на список асинхронных задач
        :param debug_perf: True - выводить время цикла
        """
        self.__url = url
        self.__client = Client(url=self.__url, timeout=2)
        self.__client.session_timeout = 60000
        self.__debug_perf = debug_perf
        atasks.append(self.task())
        # runner.append(name=self.__class__.__name__, obj=self)

    def init_channel_items(self: Self) -> None:
        for item in self.__items:
            item.init_item(self.__client)

    def add(
        self: Self,
        item: OpcUaItem[Any],
    ) -> OpcUaItem[Any]:
        self.__items.append(item)
        return item

    @property
    def ready(self: Self) -> bool:
        """PLC готов для работы.

        :return: True - plc готов
        """
        return self.__ready

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
            await asyncio.sleep(5)

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
        # self.set_perf(end_time - begin_time)
