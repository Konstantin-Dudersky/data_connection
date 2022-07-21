"""Скрипты установки."""

from .cmd_in_dir import main as cmd_in_dir
from .create_folder_abs import main as create_folder_abs
from .create_folder_rel import main as create_folder_rel
from .git_sync import main as git_sync
from .main import ComposeTask, Task, execute
from .ng_build import main as ng_build
from .ng_dist import main as ng_dist
from .poetry import main as poetry
from .port_redirect import main as port_redirect
from .python import main as python
from .samba import main as samba
from .systemd import main as systemd
from .tauri_build import main as tauri_build

__all__ = [
    "ComposeTask",
    "Task",
    "cmd_in_dir",
    "create_folder_abs",
    "create_folder_rel",
    "execute",
    "git_sync",
    "ng_build",
    "ng_dist",
    "poetry",
    "port_redirect",
    "python",
    "samba",
    "systemd",
    "tauri_build",
]
