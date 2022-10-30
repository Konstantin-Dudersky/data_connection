"""Reader side."""

import ipaddress
from typing import Any

from pydantic import BaseModel

from .abstract_side import AbstractSide
from .datapoint import DatapointBase, DatapointProcess, DpAny, Datapoint


class ReaderSide(AbstractSide):
    """Reader side."""

    def __init__(
        self,
        model: BaseModel,
        writer_side_host: ipaddress.IPv4Address,
        writer_side_port: int,
        writer_side_endpoint: str,
        send_to_writer_side_interval: float = 1.0,
    ) -> None:
        """Reader side."""
        super().__init__(
            model=model,
            other_host=writer_side_host,
            other_port=writer_side_port,
            other_endpoint=writer_side_endpoint,
            send_interval=send_to_writer_side_interval,
        )

    def _prepare_send(
        self,
        data_xch: BaseModel,
        data_ext: BaseModel,
        data_int: BaseModel,
    ) -> None:
        field_keys = data_ext.dict().keys()
        for field_key in field_keys:
            field_ext: Any = data_ext.dict()[field_key]
            if not isinstance(field_ext, Datapoint):
                raise ValueError("{0} is not Datapoint".format(field_key))
            field_int: Any = data_int.dict()[field_key]
            if not isinstance(field_int, Datapoint):
                raise ValueError("{0} is not Datapoint".format(field_key))
            field_xch: Datapoint = data_xch.dict()[field_key]
            DatapointProcess.prepare_send_to_writer_side(
                field_xch=field_xch,
                field_int=field_int,
                field_ext=field_ext,
            )

    def _prepare_rcv(
        self,
        data_rcv: BaseModel,
        data_int: BaseModel,
        data_ext: BaseModel,
    ) -> None:
        pass
