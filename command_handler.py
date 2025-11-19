"""
Manejador de comandos seguro y simulado.
Añade aquí nuevos comandos permitidos. NO ejecutar comandos arbitrarios por defecto.
Cada comando devuelve un dict con: ok (bool), output (str), meta (dict).
"""
import datetime
import os

class CommandHandler:
    def __init__(self):
        # map command names to methods
        self.commands = {
            'echo': self.cmd_echo,
            'time': self.cmd_time,
            'ls': self.cmd_list_simulated,
            'getcwd': self.cmd_getcwd,
            'help': self.cmd_help,
        }

    def handle(self, name: str, payload: dict):
        fn = self.commands.get(name)
        if not fn:
            return {'ok': False, 'output': f'Unknown command: {name}', 'meta': {}}
        try:
            return fn(payload)
        except Exception as e:
            return {'ok': False, 'output': f'Handler error: {e}', 'meta': {}}

    def cmd_echo(self, payload):
        text = payload.get('text', '')
        return {'ok': True, 'output': text, 'meta': {}}

    def cmd_time(self, payload):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        return {'ok': True, 'output': now, 'meta': {}}

    def cmd_getcwd(self, payload):
        # seguro: devuelve el cwd del proceso Python
        try:
            cwd = os.getcwd()
            return {'ok': True, 'output': cwd, 'meta': {}}
        except Exception as e:
            return {'ok': False, 'output': str(e), 'meta': {}}

    def cmd_list_simulated(self, payload):
        # Simula listado de ficheros; no ejecutar comandos del sistema
        simulated = ['README.md', 'notes.txt', 'data.csv']
        return {'ok': True, 'output': '\n'.join(simulated), 'meta': {'count': len(simulated)}}

    def cmd_help(self, payload):
        names = list(self.commands.keys())
        return {'ok': True, 'output': 'Available commands: ' + ', '.join(names), 'meta': {}}
