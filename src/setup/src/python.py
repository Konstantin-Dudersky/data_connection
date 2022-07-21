#!/usr/bin/env python3
"""Установка python на deb-based системах.

Актуальная версия - https://www.python.org/ftp/python
"""

import os
import urllib.request
from pathlib import Path
from typing import Callable

URL = "https://www.python.org/ftp/python/{python_ver}/Python-{python_ver}.tgz"


def main(python_ver: str) -> Callable[[], None]:
    """Устанавливает python.

    :param python_ver: версия python для установки
    """

    def _main() -> None:
        print("-> Загружаем зависимости")
        os.system(
            "sudo apt -y install build-essential zlib1g-dev libncurses5-dev",
        )
        os.system("sudo apt -y install libgdbm-dev libnss3-dev libsqlite3-dev")
        os.system(
            "sudo apt -y install libssl-dev libsqlite3-dev libreadline-dev",
        )
        os.system("sudo apt -y install libffi-dev libbz2-dev liblzma-dev")
        home_dir = str(Path.home())
        temp_dir = os.path.join(home_dir, "temp")
        if not os.path.exists(temp_dir):
            print("-> Папка ~/temp создана")
            os.mkdir(temp_dir)
        os.chdir(temp_dir)
        print("-> Загружаем исходный код с ftp-сервера")
        urllib.request.urlretrieve(
            URL.format(python_ver=python_ver),
            f"Python-{python_ver}.tgz",
        )
        print("-> Распаковываем файлы")
        os.system(f"tar -xf Python-{python_ver}.tgz")
        python_dir = os.path.join(temp_dir, f"Python-{python_ver}")
        os.chdir(python_dir)
        print("-> Конфигурируем исходники")
        os.system("./configure --enable-optimizations")
        os.system('make -j "$(nproc)"')
        os.system("sudo make altinstall")

    return _main


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
