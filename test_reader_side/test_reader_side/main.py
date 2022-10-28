from data_exchange.reader_side import ReaderSide

from .schemas import data


reader_side = ReaderSide(
    model=data,
    other_host="localhost",
    other_port=8011,
    other_endpoint="/ws",
)
