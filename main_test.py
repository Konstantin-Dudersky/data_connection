"""Test."""

import asyncio
from asyncio import sleep as asleep
from typing import Any, Coroutine, NamedTuple

from datapoints import (
    AccessEnum,
    ChannelOpcUa,
    DpSignal,
    DriverOpcUaClient,
)
from datapoints.utils.logger import LoggerLevel, get_logger

atasks: list[Coroutine[Any, Any, None]] = []
log = get_logger(__name__, LoggerLevel.DEBUG)
get_logger("asyncua").setLevel(level=LoggerLevel.WARNING)


opcua: DriverOpcUaClient = DriverOpcUaClient(
    url="opc.tcp://10.101.80.220:4840",
)
atasks.append(opcua.task())


class Data(NamedTuple):
    """Data."""

    test_bool_ws: DpSignal[bool] = DpSignal[bool](
        False,
        channels=(
            opcua.add(
                ChannelOpcUa[bool]("ns=4;i=2", access=AccessEnum.WRITEONLY),
            ),
        ),
    )


data: Data = Data()


async def _run() -> None:
    while True:
        data.test_bool_ws.value = not data.test_bool_ws.value
        await asleep(2)


async def run() -> None:
    """Create main task."""
    done, _ = await asyncio.wait(
        [
            *[asyncio.create_task(t) for t in atasks],
            asyncio.create_task(_run()),
        ],
        return_when=asyncio.FIRST_EXCEPTION,
    )
    try:
        _ = [d.result() for d in done]
    except BaseException:  # pylint: disable=broad-except
        log.exception(
            "Необработанное исключение, программа заканчивает выполнение",
        )


def main() -> None:
    """Entry point."""
    asyncio.run(run(), debug=True)


if __name__ == "__main__":
    main()
