from data_exchange.writer_side import WriterSide
from test_reader_side.schemas import DataModel


data = DataModel.construct()

writer_side = WriterSide(
    model=data,
    reader_side_host="localhost",
    reader_side_port=8010,
    reader_side_endpoint="/ws",
    writer_priority_delay=10.0,
)
