"""data."""

from ipaddress import IPv4Address

from data_connection.writer_side import WriterSide
from test_reader_side.schemas import DataModel


writer_side: WriterSide[DataModel] = WriterSide[DataModel](
    model=DataModel.construct(),
    reader_side_host=IPv4Address("127.0.0.1"),
    reader_side_port=8010,
    reader_side_endpoint="/ws",
    send_to_reader_side_interval=0.2,
    writer_priority_delay=10.0,
)
