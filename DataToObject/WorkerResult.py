from dataclasses import dataclass

@dataclass
class WorkerResult:
    version: str = ''
    identifier: str = ''

    os_name: str = ''
    os_version: str = ''
    machine: str = ''
    python_version: str = ''
    processor: str = ''

    created_at: str = ''

    def __init__(self):
        pass
