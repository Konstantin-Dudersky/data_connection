"""data."""

import os
from ipaddress import IPv4Address

from data_connection import WriterSide
from test_reader_side.data import DataModel


writer_side: WriterSide[DataModel] = WriterSide[DataModel](
    model=DataModel.construct(),
    reader_side_host=IPv4Address(os.environ["READER_SIDE_HOST"]),
    reader_side_port=int(os.environ["READER_SIDE_PORT"]),
    reader_side_endpoint="/ws",
    send_to_reader_side_interval=0.2,
    writer_priority_delay=10.0,
)
