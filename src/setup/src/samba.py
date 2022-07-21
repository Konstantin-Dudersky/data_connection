"""Setup share folder on IOT."""

import os
from typing import Callable

from .create_folder_rel import main as create_folder_rel


def main(rel_path: str) -> Callable[[], None]:
    def _main() -> None:
        abs_path = create_folder_rel(rel_path=rel_path)()

        share_name = "[share]"
        config_file = "/etc/samba/smb.conf"

        # read file
        with open(config_file, "r") as reader:
            lines = reader.readlines()

        # maybe config exist - find lines
        begin = -1
        end = -1
        for i in range(len(lines)):
            if lines[i].find("#" + share_name) >= 0:
                end = i
            elif lines[i].find(share_name) >= 0:
                begin = i

        # write file if config found
        if begin >= 0 and end >= 0:
            del lines[begin : end + 1]
            with open(config_file, "w") as reader:
                for line in lines:
                    reader.write(line)

        # new configuration - setup password for user
        if begin == -1 and end == -1:
            os.system('sudo smbpasswd -a "$USER"')

        # append new configuration
        config = f"""{share_name}
            comment = Share folder for IOT
            path = {abs_path}
            read only = no
            browsable = yes
        #{share_name}"""

        with open(config_file, "a") as reader:
            reader.write(config)

        print(f"Added configuration to file {config_file}: \n{config}")

    return _main
