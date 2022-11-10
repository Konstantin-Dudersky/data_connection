#!/usr/bin/python3
"""Open obsidian vault.

Set the path to the vault in a variable VAULT_PATH.
Examples:
- absolute path:
VAULT_PATH: str  = "/home/user/path-to-vault"
- relative path - current folder:
VAULT_PATH: str  = ""
- relative path - subfolder of the root folder:
VAULT_PATH: str  = "../subfolder"
"""

import subprocess
from pathlib import Path

VAULT_PATH: str = ""

URI: str = "obsidian://{path}"

subprocess.run(["xdg-open", URI.format(path=Path(VAULT_PATH).resolve())])
