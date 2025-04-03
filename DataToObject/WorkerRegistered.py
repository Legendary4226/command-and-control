from dataclasses import dataclass

from DataToObject.ServerCommand import ServerCommand
from DataToObject.WorkerResult import WorkerResult


@dataclass
class WorkerRegistered:
    collected_data: list[WorkerResult]
    command_queue: list[ServerCommand]

    created_at: str = ''
    connexions_count: int = 0
    last_known_address: tuple[str, int] = None
    last_ping_at: str = ''

    def __init__(self):
        self.collected_data = []
        self.command_queue = []
