from ipaddress import IPv4Address

from data_exchange.reader_side import ReaderSide

from .schemas import data

reader_side = ReaderSide(
    model=data,
    writer_side_host=IPv4Address("127.0.0.1"),
    writer_side_port=8011,
    writer_side_endpoint="/ws",
    send_to_writer_side_interval=10.0,
)
