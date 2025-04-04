from dataclasses import dataclass

@dataclass
class WorkerResultCommand:
    command: str = ''
    data: any = ''
    result: any = ''

    def __init__(self):
        pass
