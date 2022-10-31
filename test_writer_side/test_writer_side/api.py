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
    writer_side.data.test_dp1.value = value
    print(writer_side.data)
    return writer_side.data.dict()


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
