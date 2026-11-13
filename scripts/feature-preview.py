"""Run an isolated local preview. Stop it by closing the preview window."""
import argparse
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
PORT = 18837


def request(path, token=None):
    headers = {'Authorization': 'Bearer ' + token} if token else {}
    with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{PORT}{path}', headers=headers), timeout=2) as response:
        return response.status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault-dir')
    parser.add_argument('--wakeword-model-dir')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', PORT)) == 0:
            raise SystemExit(f'Port {PORT} is already in use; preview was not started.')
    app = ROOT / 'app'
    if not args.check and not (app / 'dist/main/main.js').is_file():
        raise SystemExit('Build the app first: npm run build:main and npm run build:renderer')
    with tempfile.TemporaryDirectory(prefix='piblo-preview-') as temp:
        tmp = Path(temp)
        vault = Path(args.vault_dir).expanduser().resolve() if args.vault_dir else tmp / 'demo'
        if args.vault_dir and not vault.is_dir():
            raise SystemExit('Vault folder does not exist.')
        if not args.vault_dir:
            vault.mkdir()
            (vault / 'Example note.txt').write_text('This is an isolated preview file.\n', encoding='utf-8')
        token = secrets.token_urlsafe(32)
        (tmp / '.env').write_text(f'MAZ_TOKEN={token}\nMAZ_PORT={PORT}\n', encoding='utf-8')
        env = {k: v for k, v in os.environ.items() if not k.startswith(('MAZ_', 'PIBLO_', 'NOD_'))}
        installed = Path(os.environ.get('LOCALAPPDATA', '')) / 'Piblo/Core/.env'
        model_keys = ('MAZ_LOCAL_ENGINE', 'MAZ_LLAMACPP_URL', 'MAZ_LLAMACPP_MODEL', 'MAZ_OLLAMA_URL', 'MAZ_OLLAMA_MODEL', 'MAZ_OLLAMA_BACKUP_MODEL')
        if installed.is_file():
            env.update({k: v for k, v in dotenv_values(installed).items() if k in model_keys and v is not None})
        env.update({'PYTHONPATH': str(ROOT / 'host'), 'MAZ_TOKEN': token, 'MAZ_BIND': '127.0.0.1',
                    'MAZ_PORT': str(PORT), 'MAZ_DISCOVERY_PORT': '0', 'MAZ_AUTOUPDATE': 'false',
                    'MAZ_BRIDGE_ENABLED': 'false', 'MAZ_REMOTE_DETECT': 'false', 'MAZ_PRIVATE_MODE': 'true',
                    'MAZ_VAULT_DIR': str(vault), 'MAZ_WAKEWORD_MODEL_DIR': args.wakeword_model_dir or '',
                    'MAZ_NOW_PATH': str(tmp / 'NOW.md'), 'MAZ_LIVE_MEMORY_FILE': str(tmp / 'memory.md')})
        for key in ('DATA_DIR', 'WORK_DIR', 'CONTROL_DIR', 'DUMPS_DIR', 'TEACH_DIR', 'SKILL_VAULT_DIR',
                    'SKILL_DRAFT_DIR', 'DEBUG_DIR', 'FLOW_DIR'):
            env['MAZ_' + key] = str(tmp / key.lower())
        core = subprocess.Popen([sys.executable, '-m', 'mazhost'], cwd=tmp, env=env)
        try:
            for _ in range(120):
                if core.poll() is not None:
                    raise RuntimeError('Preview Core exited during startup.')
                try:
                    if request('/health') == 200 and request('/vault', token) == 200:
                        break
                except (OSError, urllib.error.URLError):
                    time.sleep(.25)
            else:
                raise RuntimeError('Preview Core did not become ready.')
            try:
                request('/vault')
                raise RuntimeError('Preview unexpectedly allowed unauthenticated access.')
            except urllib.error.HTTPError as error:
                if error.code not in (401, 403):
                    raise
            if args.check:
                print('Isolated Core health and token authentication passed.')
            else:
                env.update({'NOD_CORE_DIR': str(tmp), 'NOD_CORE_PORT': str(PORT)})
                subprocess.run(['node', str(app / 'scripts/feature-preview.mjs'), str(tmp / 'userdata')], cwd=app, env=env, check=True)
        finally:
            core.terminate()
            try:
                core.wait(timeout=10)
            except subprocess.TimeoutExpired:
                core.kill()
                core.wait()


if __name__ == '__main__':
    main()
