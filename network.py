import socket
import json

class Network:
    def __init__(self, addr):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = addr  # Server IP
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def server_ip(self):
        return self.server

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return json.loads(self.client.recv(2048).decode('utf-8'))
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    def send(self, data):
        try:
            self.client.send(json.dumps(data).encode('utf-8'))
            return json.loads(self.client.recv(2048).decode('utf-8'))
        except socket.error as e:
            print(f"Socket error: {e}")
            return None
