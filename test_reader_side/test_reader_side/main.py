import asyncio
import logging

from .api import server_task
from .data import reader_side
from .logger import logger_init

logger_init("test_reader_side")

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


async def counter() -> None:
    counter: int = 0
    while True:
        counter += 1
        reader_side.data.test_dp1.value = counter
        await asyncio.sleep(2)


def main() -> None:
    """Entry point."""

    async def _main() -> None:
        done, _ = await asyncio.wait(
            [
                asyncio.create_task(server_task(8010)),
                asyncio.create_task(reader_side.task()),
                asyncio.create_task(counter()),
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
