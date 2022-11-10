import asyncio
import logging


from .api import server_task
from .data import writer_side
from .logger import logger_init
from .debugger import debugger_init

logger_init("test_writer_side")

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

debugger_init(False, 56782)


async def test() -> None:
    while True:
        await asyncio.sleep(1)


def main() -> None:
    """Entry point."""

    async def _main() -> None:
        done, _ = await asyncio.wait(
            [
                asyncio.create_task(server_task(8000)),
                asyncio.create_task(writer_side.task()),
                asyncio.create_task(test()),
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
