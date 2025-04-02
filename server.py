import ssl, os, sys, socket, json, base64
from datetime import datetime
from threading import Thread

from DataToObject.WorkerResult import WorkerResult
from Utils.DictToDataclass import dataclass_from_dict

socket.setdefaulttimeout(5)

workers: dict = {}
collectedData: dict = {}
threadWorking = True

serverPort = 55612

pwd = os.path.dirname(os.path.abspath(__file__))

sslContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
sslContext.load_cert_chain(
    certfile=os.path.join(pwd, '.ssh', 'rootCA.pem'), 
    keyfile=os.path.join(pwd, '.ssh', 'rootCA.key')
)
sslContext.check_hostname = False
sslContext.verify_mode = ssl.CERT_NONE

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

    if len(workers) == 0:
        print('Aucun worker')

    for uuid, worker in workers.items():
        print("Worker: " + str(uuid))
        print('\tcreated_at: ' + str(worker['created_at']))
        print('\tlast_ping_at: ' + str(worker['last_ping_at']))
        print('\tcreated_at: ' + str(worker['created_at']))
        print('\tconnexions_count: ' + str(worker['connexions_count']))
    
    print('\n---------\n')

def thread_listen():
    while threadWorking:
        try: 
            worker_sock, worker_address = sock.accept()
            with sslContext.wrap_socket(worker_sock, server_side=True) as secure_conn:
                handle_worker(secure_conn, worker_address)
        except socket.timeout:
            pass

def handle_worker(worker_sock: socket, worker_address: any):
    print("\nReceived data from " + str(worker_address))

    data = receive_all(worker_sock)
    worker_sock.close()

    data_decoded = json.loads(base64.b64decode(data.decode()))
    worker_result = dataclass_from_dict(WorkerResult, data_decoded)
    print("Deserialized data of worker " + str(worker_address) + '\n')

    if worker_result.worker_identifier not in workers.keys():
        workers[worker_result.worker_identifier] = {
            'created_at': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            'connexions_count': 0,
            'addresses': [worker_address],
            'last_known_address': worker_address,
        }
        collectedData[worker_result.worker_identifier] = []
    
    workers[worker_result.worker_identifier]['last_ping_at'] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    workers[worker_result.worker_identifier]['connexions_count'] += 1

    collectedData[worker_result.worker_identifier].append(worker_result)

    print('> ', end='')
    sys.stdout.flush()
    

thread = Thread(target=thread_listen)
thread.start()

while True:
    command = input('> ')

    if command == 'exit':
        print('Exiting...')
        threadWorking=False
        thread.join(500)
        sock.close()
        break
    elif command == 'r':
        recap()

sock.close()

# TODO Bonus: JSON DUMPS workers and collectedData dans un JSON
# TODO Bonus: reload depuis
