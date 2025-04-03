import os
import platform
import socket
import ssl
import time
import uuid
from datetime import datetime

from DataToObject.ServerCommand import ServerCommand
from DataToObject.WorkerResult import WorkerResult
from Utils.ObjectSerialization import data_to_base64_json_encoded_bytes, bytes_to_object
from Utils.ReceiveAll import socket_receive_all

# ------------ GLOBAL INITS
socket.setdefaulttimeout(5)

pwd = os.path.dirname(os.path.abspath(__file__))

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(os.path.join(pwd, '.ssh', 'rootCA.pem'))
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

version: str = "w1.0.0"
identifier: str = str(uuid.uuid4())
server_address = "localhost" # "192.168.220.2"
server_port = 55612


# ------------ FUNCTIONS
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

def handle_command(sock: socket.socket, command: ServerCommand) -> None:
    print('Executing ' + command.command)
    if command.command == command.CMD_LS:
        # TODO
        pass
    elif command.command == command.CMD_PING:
        # TODO
        pass

# ------------ PROGRAM
def main() -> None:
    global ssl_context, server_address, server_port

    while True:
        try:
            sock = ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname="localhost")
            sock.connect((server_address, server_port))

            data = data_to_base64_json_encoded_bytes(get_infos())
            sock.send(data)
            print('Data sent !\n')

            try:
                sock.accept()
                print('Received server command')
                data = socket_receive_all(sock)
                command = bytes_to_object(data, ServerCommand)
                handle_command(sock, command)
            except socket.timeout:
                pass

            sock.close()
        except Exception:
            pass

        time.sleep(60)

if __name__ == "__main__":
    main()
