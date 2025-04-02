import socket
from DataToObject.WorkerResult import WorkerResult
import json
from datetime import datetime
import base64
from Utils.DictToDataclass import dataclass_from_dict

workers: dict = {}
collectedData = {}

serverPort = 55612

def receive_all(sock, buffer_size=4096):
    response = b""
    while True:
        chunk = sock.recv(buffer_size)
        if not chunk:
            break
        
        response += chunk
    
    return response

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 55612))
sock.listen()

def recap():
    print('\n---------\n')

    for uuid, worker in workers.items():
        print("Worker: " + str(uuid))
        print('\tcreated_at: ' + str(worker['created_at']))
        print('\tlast_ping_at: ' + str(worker['last_ping_at']))
        print('\tcreated_at: ' + str(worker['created_at']))
        print('\tconnexions_count: ' + str(worker['connexions_count']))
    
    print('\n---------\n')

while True:
    worker_sock, worker_address = sock.accept()
    print("Received data from " + str(worker_address))

    data = receive_all(worker_sock)
    worker_sock.close()

    data_decoded = json.loads(base64.b64decode(data.decode()))
    worker_result = dataclass_from_dict(WorkerResult, data_decoded)
    print("Deserialized data of worker " + str(worker_address) + '\n')

    if worker_result.worker_identifier not in workers.keys():
        workers[worker_result.worker_identifier] = {
            'created_at': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            'connexions_count': 1,
            'addresses': [worker_address],
            'last_known_address': worker_address,
        }
        collectedData[worker_result.worker_identifier] = []
    
    workers[worker_result.worker_identifier]['last_ping_at'] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    workers[worker_result.worker_identifier]['connexions_count'] += 1

    collectedData[worker_result.worker_identifier].append(worker_result)

    recap()

sock.close()
# TODO Bonus: JSON DUMPS workers and collectedData dans un JSON
# TODO Bonus: reload depuis
