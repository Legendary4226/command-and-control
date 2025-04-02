from dataclasses import dataclass

@dataclass
class WorkerResult:
    worker_version: str = ''
    worker_identifier: str = ''

    os_name: str = ''
    os_version: str = ''
    machine: str = ''
    python_version: str = ''
    processor: str = ''

    created_at: str = ''
