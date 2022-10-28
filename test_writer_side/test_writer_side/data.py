from data_exchange.writer_side import WriterSide
from test_reader_side.schemas import DataModel


data = DataModel.construct()

writer_side = WriterSide(
    model=data,
    other_host="localhost",
    other_port=8010,
    other_endpoint="ws",
)
