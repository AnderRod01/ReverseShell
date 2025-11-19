#!/usr/bin/env python3
"""
Control server para el laboratorio de reverse-shell (simulación segura).
Ejecutar: python server.py --host 0.0.0.0 --port 9000
"""
import argparse
import json
import socket
from typing import Optional

class ClientSession:
    def __init__(self, conn: socket.socket, addr):
        self.conn = conn
        self.addr = addr
        self.buf = b""

    def send(self, obj: dict):
        data = (json.dumps(obj) + "\n").encode('utf-8')
        self.conn.sendall(data)

    def recv_message(self) -> Optional[dict]:
        while b"\n" not in self.buf:
            chunk = self.conn.recv(4096)
            if not chunk:
                return None
            self.buf += chunk
        line, sep, rest = self.buf.partition(b"\n")
        self.buf = rest
        return json.loads(line.decode('utf-8'))

class ControlServer:
    def __init__(self, host='0.0.0.0', port=9000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_session: Optional[ClientSession] = None

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f"Listening on {self.host}:{self.port}... Waiting for client...")
        conn, addr = self.sock.accept()
        print("Client connected from", addr)
        self.client_session = ClientSession(conn, addr)
        self.interactive_loop()

    def interactive_loop(self):
        cs = self.client_session
        if not cs:
            return
        try:
            while True:
                cmd = input("server> ").strip()
                if not cmd:
                    continue
                if cmd.lower() in ("quit", "exit"):
                    print("Closing connection and exiting.")
                    cs.conn.close()
                    break
                # parse simple command: first word is command name; rest is argument string
                parts = cmd.split(maxsplit=1)
                name = parts[0]
                payload = {}
                if len(parts) > 1:
                    payload['text'] = parts[1]
                message = {"type": "command", "id": "cmd1", "command": name, "payload": payload}
                cs.send(message)
                # wait for response
                resp = cs.recv_message()
                if resp is None:
                    print("Client disconnected.")
                    break
                print("Response:", resp)
        except KeyboardInterrupt:
            print('\nInterrupted. Closing.')
            if cs:
                cs.conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=9000, type=int)
    args = parser.parse_args()
    s = ControlServer(host=args.host, port=args.port)
    s.start()
