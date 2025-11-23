
"""
Control server for the reverse-shell lab (safe simulation).
Run: python server.py --host 0.0.0.0 --port 9000
"""
import argparse
import json
import socket
from typing import Optional

class ClientSession:

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.cmd_counter = 0

    # Sends a command to the client in JSON format.
    def send_command(self, command_str):
        self.cmd_counter += 1
        cmd_id = f"cmd{self.cmd_counter}"

        parts = command_str.split(maxsplit=1)
        name = parts[0]
        payload = {}

        # Only allowed: exec <cmd> 
        if name == "exec":
            if len(parts) < 2:
                print("To use: exec <comando>")
                return
            payload["cmd"] = parts[1]

        msg = {
            "type": "command",
            "id": cmd_id,
            "command": name,
            "payload": payload
        }

        self.conn.sendall((json.dumps(msg) + "\n").encode())

        # wait for client response
        buffer = ""
        while True:
            data = self.conn.recv(4096)
            if not data:
                print("[SERVER] Client closed connection.")
                break

            buffer += data.decode()
            if "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                self.print_response(line)
                break

    def print_response(self, line):
        try:
            msg = json.loads(line)
        except:
            print("[SERVER] Invalid JSON", line)
            return

        print("\n--- RESPONSE ---")
        print(json.dumps(msg, indent=2))
        print("----------------\n")


class ControlServer:
    """
    Control server with classes:
    - Accepts a client
    - Uses ClientSession to send commands
    """

    def __init__(self, host="0.0.0.0", port=9000):
        self.host = host
        self.port = port
        self.sock = None
        self.session = None

    def start(self):
        print(f"[SERVER] Listening to {self.host}:{self.port}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

        conn, addr = self.sock.accept()
        print(f"[SERVER] Client connected from {addr}")

        self.session = ClientSession(conn, addr)

        self.server_loop()

    def server_loop(self):
        while True:
            try:
                cmd = input("server> ").strip()
                if not cmd:
                    continue

                self.session.send_command(cmd)

            except KeyboardInterrupt:
                print("\n[SERVER] Closing server.")
                break

        self.session.conn.close()
        self.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()

    server = ControlServer(args.host, args.port)
    server.start()