"""Создать папку."""

import os

from typing import Callable


def main(abs_path: str = "~/share") -> Callable[[], None]:
    """Создать папку."""

    def _main() -> None:
        if not os.path.exists(abs_path):
            print(f"-> Папка {abs_path} создана")
            os.mkdir(abs_path)

    return _main
