"""Create systemd service file."""

import getpass
import os
from pathlib import Path
from typing import Callable

SERVICE = """
[Unit]
Description={description}

[Service]
Restart=always
RestartSec=10s
Type=simple
User={user}
Group={user}
EnvironmentFile=/etc/environment
WorkingDirectory={work_dir}
ExecStart={poetry_bin} run python {start_file}

[Install]
WantedBy=multi-user.target"""


def main(
    service_name: str,
    description: str,
    work_dir_relative: str,
    start_file: str = "start.py",
) -> Callable[[], None]:
    """Создать сервис.

    :param service_name: название сервиса
    :param description: описание сервиса
    :param work_dir_relative: относительный путь для рабочей папки сервиса
    :param start_file: файл для запуска
    """

    def _main() -> None:
        home_dir = str(Path.home())
        poetry_bin = os.path.join(home_dir, ".local", "bin", "poetry")
        print(f"-> Poetry bin path: {poetry_bin}")
        curr_dir = os.getcwd()
        work_dir_abs_full = os.path.join(curr_dir, work_dir_relative)
        work_dir_abs = os.path.abspath(work_dir_abs_full)
        print(f"-> Work dir absolute path: {work_dir_abs}")
        service = SERVICE.format(
            description=description,
            user=getpass.getuser(),
            work_dir=work_dir_abs,
            poetry_bin=poetry_bin,
            start_file=start_file,
        )
        print(f"-> Final service file: \n{service}\n")
        filename = f"src/{service_name}.service"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(service)
        print(f"-> File {filename} created")
        os.system(f"sudo mv {filename} /etc/systemd/system")
        os.system("sudo systemctl daemon-reload")

    return _main


if __name__ == "__main__":
    main(
        service_name="service",
        description="description",
        work_dir_relative="../server",
    )
