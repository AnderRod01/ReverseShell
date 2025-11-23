# Reverse Shell Simulation
This project implements a safe, controlled reverse-shell simulation for cybersecurity education.
The client initiates a TCP connection to the server (reverse pattern). The server sends commands, and the client executes only operating-system commands explicitly allowed in a whitelist, using subprocess.run.

Security Notice
This project must only be executed inside an isolated lab environment (VMs or containers).
Do not deploy or adapt this code for real-world systems.


---

## Files
- `server.py` — server entrypoint (runs in `server` mode)
- `client.py` — client entrypoint (runs in `client` mode)
- `command_handler.py` — safe command implementations
- `report.md` — short risks & mitigations report

---

## How to run
1. Ensure Python 3.8+ is installed.
2. Start the server on the control machine (or VM):
   
```bash
python server.py --host 0.0.0.0 --port 9000
```

3. Start the client in the target VM (it will attempt to connect to the hard-coded server address):
   
```bash
python client.py
```
### Changing the client's hard-coded address
Open `client.py` and edit the constants at the top:
```python
SERVER_HOST = '192.168.1.100'  # change me
SERVER_PORT = 9000
```
---

## Communication Protocol (JSON over TCP)
The server and client exchange JSON messages terminated by a newline (\n).

### Message types
**Server -> Client**
- `type`: `command`
- `id`: (string or number) command identifier
- `command`: (string) command name, e.g. `echo`, `time`, `list_files`
- `payload`: optional object with command arguments

Example:
```json
{
  "type": "command",
  "id": "cmd12",
  "command": "exec",
  "payload": {
    "cmd": "hostname"
  }
}
```

**Client -> Server**
- `type`: `response`
- `id`: same as the command id
- `status`: `ok` | `error`
- `output`: string output (simulated command output)
- `meta`: optional object with additional info

Example:
```json
{
  "type": "response",
  "id": "cmd12",
  "status": "ok",
  "output": "lab-machine-01",
  "meta": {
    "return_code": 0
  }
}
```
**Error Response**
```json
{
  "type": "response",
  "id": "cmd12",
  "status": "error",
  "output": "Command NOT allowed: rm",
  "meta": {}
}
```

---
