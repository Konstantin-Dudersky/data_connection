"""data."""

import os
from ipaddress import IPv4Address

from data_connection import BaseModel, Field, ReaderSide
from data_connection.readers import opcua_client


class InnerModel(BaseModel):
    test_int: Field[int] = Field[int](0)
    test_wstring: Field[str] = Field[str]("")


class DataModel(BaseModel):
    test_float: Field[float] = Field[float](0.1)
    test_bool: Field[bool] = Field[bool](False, "rw")
    test_str: Field[str] = Field[str]("")
    inner: InnerModel = InnerModel()


reader_side = ReaderSide[DataModel](
    model=DataModel.construct(),
    writer_side_host=IPv4Address(os.environ["WRITER_SIDE_HOST"]),
    writer_side_port=int(os.environ["WRITER_SIDE_PORT"]),
    writer_side_endpoint="/ws",
    send_to_writer_side_interval=0.2,
)


opcua = opcua_client.Reader(
    url="opc.tcp://10.101.80.184:4840",
    comm_cycle=0.5,
    debug_comm_cycle=False,
    fields=[
        opcua_client.Field[str](
            field=reader_side.data.test_str,
            node_id="ns=4;i=2",
        ),
        opcua_client.Field[bool](
            field=reader_side.data.test_bool,
            node_id="ns=4;i=3",
        ),
        opcua_client.Field[float](
            field=reader_side.data.test_float,
            node_id="ns=4;i=4",
        ),
        opcua_client.Field[int](
            field=reader_side.data.inner.test_int,
            node_id="ns=4;i=5",
        ),
        opcua_client.Field[str](
            field=reader_side.data.inner.test_wstring,
            node_id="ns=4;i=6",
        ),
    ],
)
