Чтение данных с контроллера S7-1200 по OPC UA.

Запуск:
- ==reader_side==

```sh
poetry run start
```

- ==writer_side==

```sh
poetry run start
```

API:
- ==reader_side==
состояние - http://localhost:8010/data/status
- ==writer_side==
состояние - http://localhost:8011/data/status
изменить значение переменной - http://localhost:8011/data-change?value=25
