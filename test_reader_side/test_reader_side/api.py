import uvicorn
from fastapi import FastAPI

from .data import reader_side

api = FastAPI()

reader_side.configure_fastapi(
    api=api,
    endpoint_ws="/ws",
)


async def server_task(port: int) -> None:
    """Задача для запуска сервера api.
    :param api: ссылка на api
    :param port: порт
    """
    config = uvicorn.Config(
        api,
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True,
    )
    await uvicorn.Server(  # pyright: ignore [reportUnknownMemberType]
        config,
    ).serve()  # pyright: ignore [reportUnknownMemberType]
