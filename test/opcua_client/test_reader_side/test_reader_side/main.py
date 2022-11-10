import asyncio
import logging

from .api import server_task
from .data import opcua, reader_side
from .logger import logger_init

logger_init("test_reader_side")

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def main() -> None:
    """Entry point."""

    async def _main() -> None:
        done, _ = await asyncio.wait(
            [
                asyncio.create_task(server_task(8000)),
                asyncio.create_task(reader_side.task()),
                asyncio.create_task(opcua.task()),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )
        try:
            _ = [done_task.result() for done_task in done]
        except BaseException:  # noqa: WPS424
            log.exception(
                "Необработанное исключение, программа заканчивает выполнение",
            )

    asyncio.run(_main())
