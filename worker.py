import socket
import json
import base64
import uuid
from DataToObject.WorkerResult import WorkerResult
import dataclasses
from datetime import datetime
import time

workerVersion: str = "w1.0.0"
workerIdentifier: str = str(uuid.uuid4())
serverAddress = "localhost" # "192.168.220.2"
serverPort = 55612

def getInfos() -> object:
    data = object.__new__(WorkerResult)

    data.worker_identifier = workerIdentifier
    data.worker_version = workerVersion
    data.created_at = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    
    import platform

    data.os_name = platform.system()
    data.os_version = platform.version()
    data.machine = platform.machine()
    data.python_version = platform.python_version()
    data.processor = platform.processor()

    print(data)

    return data

def dataToJsonEncodedToBase64Str(data: object) -> str:
    return base64.b64encode(json.dumps(dataclasses.asdict(data)).encode())

def main():
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((serverAddress, serverPort))

        data = dataToJsonEncodedToBase64Str(getInfos())
        sock.send(data)
        print('Data sent !\n')
        
        sock.close()

        time.sleep(60)

if __name__ == "__main__":
    main()
