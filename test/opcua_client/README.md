Чтение данных с контроллера S7-1200 по OPC UA.

Сборка:

```sh
docker buildx bake --builder builder -f docker-bake.hcl --push opcua_client
```

Запуск:

```sh
docker compose --profile opcua_client pull \
	&& docker compose --profile opcua_client up -d
```

Останов:

```sh
docker compose --profile opcua_client down
```

API:
- ==reader_side==
состояние - http://localhost:8010/data/status
- ==writer_side==
состояние - http://localhost:8011/data/status
изменить значение переменной - http://localhost:8011/data-change?value=25
