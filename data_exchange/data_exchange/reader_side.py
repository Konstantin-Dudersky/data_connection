"""Reader side."""

import ipaddress

from pydantic import BaseModel

from .abstract_side import AbstractSide


class ReaderSide(AbstractSide):
    """Reader side."""

    def __init__(
        self,
        model: BaseModel,
        other_host: ipaddress.IPv4Address,
        other_port: int,
        other_endpoint: str,
        send_interval: float = 1.0,
    ) -> None:
        """Reader side."""
        super().__init__(
            model,
            other_host,
            other_port,
            other_endpoint,
            send_interval,
        )
