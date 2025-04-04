import platform
import subprocess

def ping(host: str) -> bool:
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0
