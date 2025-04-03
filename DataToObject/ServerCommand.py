from dataclasses import dataclass
from typing import ClassVar

@dataclass
class ServerCommand:
    command: str
    data: any

    CMD_PING: ClassVar[str] = 'ping'
    CMD_LS: ClassVar[str] = 'ls'

    ALL: ClassVar[list[str]] = [
        CMD_PING, CMD_LS,
    ]

    def __init__(self):
        pass
