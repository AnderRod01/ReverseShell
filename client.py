
"""
Reverse client (safe simulation).
Edit SERVER_HOST and SERVER_PORT at the beginning if you need to point to another server.
Run: python client.py
"""
import socket
import json
import time
from command_handler import CommandHandler

# Change server address and port if needed
SERVER_HOST = '0.0.0.0'  
SERVER_PORT = 9000

class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.handler = CommandHandler()


    def connect_and_run(self):
        while True:
            try:
                print(f"[CLIENT] Connecting to {self.server_host}:{self.server_port}...")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.server_host, self.server_port))
                print("[CLIENT] Connected.")
                self.session_loop(s)
            except Exception as e:
                print(f"[CLIENT] Connection failed: {e}. Retrying in 3 seconds...")
                time.sleep(3)

    def session_loop(self, s: socket.socket):
        with s:
            buffer = ""
            while True:
                data = s.recv(1024)
                if not data:
                    print("[CLIENT] Server closed connection.")
                    break

                buffer += data.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_message(line, s)

    def handle_message(self, line, sock):
        try:
            msg = json.loads(line)
        except Exception as e:
            print("[CLIENT] Invalid JSON:", e)
            return

        if msg.get("type") == "command":
            command = msg.get("command")
            payload = msg.get("payload", {})
            cmd_id = msg.get("id")

            result = self.handler.handle(command, payload)

            response = {
                "type": "response",
                "id": cmd_id,
                "status": "ok" if result["ok"] else "error",
                "output": result["output"],
                "meta": result.get("meta", {})
            }

            sock.sendall((json.dumps(response) + "\n").encode())

if __name__ == "__main__":
    c = Client(SERVER_HOST, SERVER_PORT)
    c.connect_and_run()