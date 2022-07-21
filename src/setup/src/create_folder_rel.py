"""Создать папку."""

import os

from typing import Callable

from .create_folder_abs import main as create_folder_abs


def main(rel_path: str = "../share") -> Callable[[], str]:
    """Создать папку."""

    def _main() -> str:
        curr_dir = os.getcwd()
        abs_path = os.path.abspath(os.path.join(curr_dir, rel_path))
        create_folder_abs(abs_path=abs_path)()
        return abs_path

    return _main
