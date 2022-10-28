from fastapi import FastAPI, WebSocket

from .main import reader_side

api = FastAPI()


@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await reader_side.ws_server(websocket)
