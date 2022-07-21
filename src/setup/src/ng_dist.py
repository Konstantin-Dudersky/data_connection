import os
from typing import Callable


def main(
    source_dir_rel: str = "../client/",
    target_dir_rel: str = "../server/static/",
    project: str = "client",
) -> Callable[[], None]:
    """
    Разворачивание проекта.

    :param source_dir_rel: относительный путь к папке с архивом
    :param target_dir_rel: относительный путь к целевой папке
    :param project: _description_, defaults to "client"
    """

    def _main() -> None:
        os.system("sudo apt install -y unzip")
        curr_dir = os.getcwd()
        source_file = os.path.abspath(
            os.path.join(curr_dir, source_dir_rel, "dist", project + ".zip"),
        )
        print(f"-> Исходный файл: {source_file}")
        target_dir = os.path.abspath(os.path.join(curr_dir, target_dir_rel))
        print(f"-> Целевая папка: {target_dir}")
        os.system(f"unzip -uo {source_file} -d {target_dir}")

    return _main
