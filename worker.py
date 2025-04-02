import socket, json, base64, uuid, dataclasses, time, ssl, os
from datetime import datetime

from DataToObject.WorkerResult import WorkerResult

socket.setdefaulttimeout(5)

pwd = os.path.dirname(os.path.abspath(__file__))

sslContext = ssl.create_default_context()
sslContext.load_verify_locations(os.path.join(pwd, '.ssh', 'rootCA.pem'))
sslContext.check_hostname = False
sslContext.verify_mode = ssl.CERT_NONE

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
        try:
            sock = sslContext.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname="localhost")
            sock.connect((serverAddress, serverPort))

            data = dataToJsonEncodedToBase64Str(getInfos())
            sock.send(data)
            print('Data sent !\n')
            
            sock.close()
        except Exception:
            pass
        time.sleep(60)

if __name__ == "__main__":
    main()
