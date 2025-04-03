import socket

socket.setdefaulttimeout(5)

def socket_receive_all(sock: socket.socket, buffer_size: int = 4096) -> bytes:
    response = b""
    while True:
        try:
            chunk = sock.recv(buffer_size)
            if not chunk:
                break

            response += chunk

            if len(chunk) < buffer_size:
                break
        except socket.timeout:
            break
    
    return response
