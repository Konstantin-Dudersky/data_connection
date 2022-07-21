import sys
from typing import Callable, NamedTuple


class Task:
    def __init__(
        self: "Task",
        desc: str,
        task: Callable[[], None],
    ) -> None:
        self.__desc = desc
        self.__task = task
        self.__command: str = ""

    @property
    def command(self: "Task") -> str:
        return self.__command

    @command.setter
    def command(self: "Task", value: str) -> None:
        self.__command = value

    def execute(self: "Task") -> None:
        print("-" * 80)
        print(f"-> {self.__command} - {self.__desc}")
        self.__task()

    def __str__(self: "Task") -> str:
        return f"* {self.__command} - {self.__desc}"


class ComposeTask:
    def __init__(
        self: "ComposeTask",
        desc: str,
        subtasks: list[Task],
    ) -> None:
        self.__desc = desc
        self.__subtasks = subtasks
        self.__command: str = ""

    @property
    def command(self: "ComposeTask") -> str:
        return self.__command

    @command.setter
    def command(self: "ComposeTask", value: str) -> None:
        self.__command = value

    def execute(self: "ComposeTask") -> None:
        print("-" * 80)
        print(f"-> {self.__command} - {self.__desc}")
        for task in self.__subtasks:
            task.execute()

    def __str__(self: "ComposeTask") -> str:
        out = f"* {self.__command} - {self.__desc}:\n"
        for task in self.__subtasks:
            out += f"\t{task}\n"
        return out


def execute(arg: str, simple_tasks: NamedTuple, compose_tasks: NamedTuple):
    for command, task in simple_tasks._asdict().items():
        task.command = command
    for command, task in compose_tasks._asdict().items():
        task.command = command
    if len(sys.argv) <= 1:
        print("Не указана запускаемая задача")
        sys.exit(1)
    task_arg = arg
    if task_arg == "--help":
        print()
        print("Задачи:")
        for task in simple_tasks:
            print(task)
        print()
        print("Комбинированные задачи:")
        for task2 in compose_tasks:
            print(task2)
        sys.exit(0)
    if task_arg in simple_tasks._asdict().keys():
        simple_tasks._asdict()[task_arg].execute()
        sys.exit(0)
    if task_arg in compose_tasks._asdict().keys():
        compose_tasks._asdict()[task_arg].execute()
        sys.exit(0)
    print(f"Задача {task_arg} не найдена!")
