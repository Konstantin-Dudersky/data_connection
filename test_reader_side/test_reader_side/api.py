import uvicorn
from fastapi import FastAPI, WebSocket

from .data import reader_side

api = FastAPI()


@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await reader_side.ws_server(websocket)


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
