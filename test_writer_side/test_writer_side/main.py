import asyncio
import logging


from .api import server_task
from .data import writer_side, data
from .logger import logger_init
from .debugger import debugger_init

logger_init("test_writer_side")

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

debugger_init(False, 56782)

# def main() -> None:
#     async def _main() -> None:
#         async with asyncio.TaskGroup() as tg:
#             tg.create_task(writer_side.task())
#             tg.create_task(server_task(8011))

#     try:
#         asyncio.run(_main())
#     except ExceptionGroup as eg:
#         print(eg.exceptions)


# test ------------------

from pydantic import BaseModel
from data_exchange.datapoint import Float, DatapointBase


class TestModel(BaseModel):
    test_dp: Float = Float()


def main() -> None:
    data = TestModel.construct()

    print(id(data.test_dp))

    for field in data:
        d = field[1]
        d.value = 12
        if isinstance(d, DatapointBase):
            print("isinstance!")
    data.dict()["test_dp"].value = 34
    print(data)


# test end ------------------


async def test() -> None:
    while True:
        print(data)
        await asyncio.sleep(1)


def main() -> None:
    """Entry point."""

    async def _main() -> None:
        done, _ = await asyncio.wait(
            [
                asyncio.create_task(server_task(8011)),
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
