# data_exchange

## Описание

Обмен данными между микросервисами.

Зависимости:
- [websockets](https://websockets.readthedocs.io/en/stable/index.html)
- [fastapi](https://fastapi.tiangolo.com/)
- [pydantic](https://pydantic-docs.helpmanual.io/)


Данные передаются с помощью websocket. Клиентская часть работает с помощью https://websockets.readthedocs.io/en/stable/. Серверная на fastapi.

Обмен данными настрававется с двух сторон:
- reader_side - напр., сервис OPC UA клиент. "Читает" данные с полевого уровня и передает на вышестоящие сервисы.
- writer_side - напр. сервис API или Modbus TCP сервер. Данные "записываются" с верхнего уровня из передаются на полевой.

writer_side имеет более высокий приоритет, чем reader_side. Например, мы поменяли параметр на стороне writer_side. В этот же момент данные считываются на стороне reader_side. Значение из writer_side будет иметь более высокий приоритет, чем reader_side, если разница между метками времени этих значений будет меньше, чем значение в параметре `writer_priority_delay`.

Данные описываются в виде модели данных [pydantic](https://pydantic-docs.helpmanual.io/).



## Разработка

Установить виртуальное окружение

```sh
poetry install
```

Опубликовать пакет

```sh
poetry build && poetry publish
```
