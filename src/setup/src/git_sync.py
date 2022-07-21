"""Синхронизировать проект с github."""

import os
from typing import Callable


def main() -> Callable[[], None]:
    """Синхронизация проекта с Github."""

    def _main() -> None:
        print("-> Синхронизация проекта с Github")
        os.system(
            "git fetch origin && git reset --hard origin/main "
            "&& git clean -f -d",
        )
        print("-> Проект синхронизирован")

    return _main
