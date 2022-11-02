"""API."""

import uvicorn
from fastapi import FastAPI, Query


from .data import writer_side, DataModel

api: FastAPI = FastAPI()

writer_side.configure_fastapi(
    api=api,
    endpoint_ws="/ws",
)


@api.get("/data-change")
def data_change(value: float = Query()) -> DataModel:
    writer_side.data.test_float.value = value
    return writer_side.data


async def server_task(port: int) -> None:
    """Задача для запуска сервера api.

    Parameters
    ----------
    port: int
        порт
    """
    config = uvicorn.Config(
        api,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
    await uvicorn.Server(  # pyright: ignore [reportUnknownMemberType]
        config,
    ).serve()  # pyright: ignore [reportUnknownMemberType]
