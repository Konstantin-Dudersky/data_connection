import uvicorn
from fastapi import FastAPI, Query, WebSocket


from .data import data, writer_side, DataModel

api: FastAPI = FastAPI()


@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await writer_side.ws_server(websocket)


@api.get("/data-change")
def data_change(value: float = Query()) -> DataModel:
    data.test_dp1.value = value
    print(data.dict())
    return data.dict()


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
    )
    await uvicorn.Server(  # pyright: ignore [reportUnknownMemberType]
        config,
    ).serve()  # pyright: ignore [reportUnknownMemberType]
