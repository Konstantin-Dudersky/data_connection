import os
from typing import Callable


def main(
    work_dir_relative: str,
    project: str = "client",
) -> Callable[[], None]:
    def _main():
        curr_dir = os.getcwd()
        work_dir_abs_full = os.path.join(curr_dir, work_dir_relative)
        work_dir_abs = os.path.abspath(work_dir_abs_full)
        print(f"-> Рабочая папка: {work_dir_abs}")
        os.chdir(work_dir_abs)
        os.system("ng build")
        filename = f"dist/{project}.zip"
        os.system(f"zip -j -r {filename} dist/{project}/")
        print(f"-> Создан архив: {filename}")
        os.system(f"rm -rf dist/{project}/")

    return _main
