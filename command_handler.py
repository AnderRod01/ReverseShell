"""
Safe and simulated command handler.
Add new allowed commands here. Do NOT execute arbitrary commands by default.
Each command returns a dict with: ok (bool), output (str), meta (dict).
"""
import datetime
import os
import subprocess




class CommandHandler:
    def __init__(self):
        self.WHITELIST =  {'echo', 'uptime', 'ls', 'help', 'hostname'}
        
    def handle(self, name: str, payload: dict):
        if name != "exec":
            return {
                "ok": False,
                "output": f"Unknown command: {name}",
                "meta": {}
            }
        return self.cmd_exec_whitelisted(payload)

    def cmd_exec_whitelisted(self, payload):
        cmd = payload.get("cmd")

        if not cmd:
            return {'ok': False, 'output': "Missing argument: cmd", 'meta': {}}

        # arguments are not allowed (ls -l / etc)
        if " " in cmd:
            return {
                "ok": False,
                "output": "Arguments are not allowed. Only bare commands are permitted.",
                "meta": {}
            }

        # verify whitelist
        if cmd not in self.WHITELIST:
            return {
                "ok": False,
                "output": f"Command NOT allowed: {cmd}",
                "meta": {"allowed": list(self.WHITELIST)}
            }

        # Execute the command safely
        try:
            result = subprocess.run(
                [cmd],
                capture_output=True,
                text=True,
                timeout=5,
            )

            output = result.stdout.strip() if result.stdout else "(no output)"

            return {
                "ok": True,
                "output": output,
                "meta": {"return_code": result.returncode}
            }

        except Exception as e:
            return {
                "ok": False,
                "output": f"Execution error: {e}",
                "meta": {}
            }
