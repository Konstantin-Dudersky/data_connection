import ipaddress
from typing import Final

from pydantic import BaseModel

from .abstract_side import AbstractSide


class WriterSide(AbstractSide):
    """Writer side."""

    def __init__(
        self,
        model: BaseModel,
        other_host: ipaddress.IPv4Address,
        other_port: int = 8000,
        other_endpoint: str = "data",
        send_interval: float = 1.0,
    ) -> None:
        """Writer side."""
        super().__init__(
            model,
            other_host,
            other_port,
            other_endpoint,
            send_interval,
        )
