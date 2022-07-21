"""Выполнить команду в указанной папке."""

import os
from typing import Callable


def main(work_dir: str, command: str) -> Callable[[], None]:
    """Выполнить команду в папке.

    :param work_dir: относительный путь к папке
    :param command: команда
    :return: функция
    """

    def _main() -> None:
        curr_dir = os.getcwd()
        work_dir_abs_full = os.path.join(curr_dir, work_dir)
        work_dir_abs = os.path.abspath(work_dir_abs_full)
        print(f"-> Рабочая папка: {work_dir_abs}")
        os.chdir(work_dir_abs)
        print(f"-> Выполняем команду: {command}")
        os.system(command)

    return _main
