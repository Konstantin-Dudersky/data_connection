
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

@app.exception_handler(
    RequestValidationError,
)  # pyright: reportUntypedFunctionDecorator=false
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Логгирование неправильных запросов.

    :param request: запрос
    :param exc: исключение
    :return: json с перечнем ошибок
    """
    logger.error(
        "Неправильный запрос.\n-> Запрос: %s\n-> Ошибки: %s",
        request.url,
        exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )