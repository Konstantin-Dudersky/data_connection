"""Подключение дебаггера."""

import logging

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def debugger_init(init: bool, port: int = 5678) -> None:
    """Запуск дебаггера.
    :param init: True = инициализировать
    """
    if not init:
        return

    import debugpy  # noqa: WPS433

    debugpy.listen(("0.0.0.0", port))
    log.warning("Запущен режим debug, ждем подключение отладчика")
    debugpy.wait_for_client()
