from dataclasses import dataclass
from typing import ClassVar

@dataclass
class ServerCommand:
    CMD_PING: ClassVar[str] = 'ping'
    CMD_LS: ClassVar[str] = 'ls'
    CMD_CUSTOM: ClassVar[str] = 'custom'

    ALL: ClassVar[list[str]] = [
        CMD_PING, CMD_LS, CMD_CUSTOM,
    ]

    command: str = ''
    data: any = ''

    def __init__(self):
        pass
