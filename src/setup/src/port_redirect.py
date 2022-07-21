"""Перенаправление портов."""

import os
from typing import Callable


def main(from_port: int = 80, to_port: int = 8000) -> Callable[[], None]:
    """Перенаправление портов."""

    def _main() -> None:
        os.system(
            (
                "sudo iptables -t nat -A PREROUTING -p tcp "
                f"--dport {from_port} "
                f" -j REDIRECT --to-port {to_port}"
            ),
        )
        os.system('sudo sh -c "iptables-save > /etc/iptables.rules"')
        os.system("sudo apt-get install iptables-persistent")
        print(
            "-> Если при перезагрузке редирект не сохраняется, "
            "то дописать в файл "
            ":\n/etc/rc.local\nстроку:\niptables-restore "
            "< /etc/iptables.rules",
        )

    return _main
