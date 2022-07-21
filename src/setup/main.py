#!/usr/bin/env python3
"""Скрипты установки."""

import sys
from typing import NamedTuple

import src


SYSTEMD_SERVICE = "kleck"


class Tasks(NamedTuple):
    client_ng_build: src.Task = src.Task(
        desc="Сборка проекта Angular",
        task=src.ng_build(work_dir_relative="../client", project="client"),
    )
    client_ng_dist: src.Task = src.Task(
        desc="Распаковать файлы фронтенда",
        task=src.ng_dist(
            source_dir_rel="../client",
            target_dir_rel="../server/static",
            project="client",
        ),
    )
    client_tauri_build: src.Task = src.Task(
        desc="Сборка tauri",
        task=src.tauri_build(
            work_dir_relative="../client",
            project="client",
        ),
    )
    git_sync: src.Task = src.Task(
        desc="Синхронизировать проект через git",
        task=src.git_sync(),
    )
    poetry_self_install: src.Task = src.Task(
        desc="Установить в системе poetry", task=src.poetry()
    )
    python_install: src.Task = src.Task(
        desc="Установка python",
        task=src.python("3.10.5"),
    )
    server_alembic_upgrade: src.Task = src.Task(
        desc="Обновить схему БД",
        task=src.cmd_in_dir(
            work_dir="../server",
            command="poetry run alembic upgrade head",
        ),
    )
    server_lint: src.Task = src.Task(
        desc="linting",
        task=src.cmd_in_dir(
            work_dir="../server",
            command="poetry run poe lint",
        ),
    )
    server_service_start: src.Task = src.Task(
        desc="Запустить сервис",
        task=src.cmd_in_dir(
            work_dir=".", command=f"sudo systemctl start {SYSTEMD_SERVICE}"
        ),
    )
    server_service_stop: src.Task = src.Task(
        desc="Остановить сервис",
        task=src.cmd_in_dir(
            work_dir=".", command=f"sudo systemctl stop {SYSTEMD_SERVICE}"
        ),
    )
    server_poetry_update: src.Task = src.Task(
        desc="Обновление пакетов poetry",
        task=src.cmd_in_dir(
            work_dir="../server",
            command="poetry update --no-dev",
        ),
    )
    server_port_redirect: src.Task = src.Task(
        desc="Перенаправление портов",
        task=src.port_redirect(from_port=80, to_port=8000),
    )
    server_systemd: src.Task = src.Task(
        desc="Создание сервиса systemd",
        task=src.systemd(
            service_name=SYSTEMD_SERVICE,
            description="kleck",
            work_dir_relative="../server",
        ),
    )
    server_share_folder: src.Task = src.Task(
        desc="Создание общей папки", task=src.samba("../../share")
    )


TASKS = Tasks()


class ComposeTasks(NamedTuple):
    build: src.ComposeTask = src.ComposeTask(
        desc="Сборка проекта",
        subtasks=[
            TASKS.server_lint,
            TASKS.client_ng_build,
        ],
    )
    install: src.ComposeTask = src.ComposeTask(
        desc="Установка проекта на целевой системе",
        subtasks=[
            TASKS.python_install,
            TASKS.poetry_self_install,
            TASKS.server_port_redirect,
            TASKS.server_systemd,
            TASKS.server_share_folder,
        ],
    )
    update: src.ComposeTask = src.ComposeTask(
        desc="Обновить проект на целевой системе",
        subtasks=[
            TASKS.server_service_stop,
            TASKS.git_sync,
            TASKS.server_poetry_update,
            TASKS.client_ng_dist,
            TASKS.server_alembic_upgrade,
            TASKS.server_service_start,
        ],
    )


COMPOSE_TASKS = ComposeTasks()


if __name__ == "__main__":
    src.execute(sys.argv[1], TASKS, COMPOSE_TASKS)
