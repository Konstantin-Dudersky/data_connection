import asyncio
from typing import Any, Coroutine, NamedTuple

from data_connector.utils.logger import LoggerLevel, get_logger
from data_connector.utils.settings import settings
from data_connector.datapoint import DatapointSignal
from data_connector.channel import OpcUaItem, OpcUaChannel
from data_connector.signals import AccessEnum

atasks: list[Coroutine[Any, Any, None]] = []
log = get_logger(__name__, LoggerLevel.DEBUG)
get_logger("asyncua").setLevel(level=LoggerLevel.WARNING)


opcua = OpcUaChannel(
    url=settings.plc_url,
    atasks=atasks,
)


class Data(NamedTuple):
    test_bool: DatapointSignal[bool] = DatapointSignal[bool](
        False,
        channels=[
            opcua.add(
                OpcUaItem[bool]("node_id", access=AccessEnum.READWRITE),
            ),
        ],
    )


data: Data = Data()
opcua.init_channel_items()

for dp in data:
    print(dp)


async def run() -> None:
    """Create main task."""
    done, _ = await asyncio.wait(
        [
            *[asyncio.create_task(t) for t in atasks],
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
