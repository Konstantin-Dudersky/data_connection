"""data."""

from ipaddress import IPv4Address

from data_connection import ReaderSide
from data_connection.readers import opcua_client

from .schemas import DataModel

reader_side = ReaderSide[DataModel](
    model=DataModel.construct(),
    writer_side_host=IPv4Address("127.0.0.1"),
    writer_side_port=8011,
    writer_side_endpoint="/ws",
    send_to_writer_side_interval=0.2,
)


opcua = opcua_client.Reader(
    url="opc.tcp://10.101.80.184:4840",
    comm_cycle=0.5,
    debug_comm_cycle=False,
    datapoints=[
        opcua_client.Field[str](
            datapoint=reader_side.data.test_str,
            node_id="ns=4;i=2",
        ),
        opcua_client.Field[bool](
            datapoint=reader_side.data.test_bool,
            node_id="ns=4;i=3",
        ),
        opcua_client.Field[float](
            datapoint=reader_side.data.test_float,
            node_id="ns=4;i=4",
        ),
        opcua_client.Field[int](
            datapoint=reader_side.data.inner.test_int,
            node_id="ns=4;i=5",
        ),
        opcua_client.Field[str](
            datapoint=reader_side.data.inner.test_wstring,
            node_id="ns=4;i=6",
        ),
    ],
)
