"""Prove Ask memory against a temporary Core on :18837, never the installed Core."""
import argparse
import json
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


def request(path, token=None, body=None, timeout=3):
    headers = {'Authorization': 'Bearer ' + token} if token else {}
    with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{PORT}{path}', headers={**headers, 'Content-Type': 'application/json'}, data=json.dumps(body).encode() if body is not None else None), timeout=timeout) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--check-memory', action='store_true', help='Synthetic Ask memory proof across a Core restart, using the configured local model')
    args = parser.parse_args()
    if not args.check:
        args.check_memory = True
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', PORT)) == 0:
            raise SystemExit(f'Port {PORT} is already in use; preview was not started.')
    with tempfile.TemporaryDirectory(prefix='piblo-preview-') as temp:
        tmp = Path(temp)
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
                    'MAZ_TTS_ENABLED': 'false', 'MAZ_BUDDY_DB': str(tmp / 'buddy.sqlite3'),
                    'MAZ_CORE_ENABLED': 'false', 'MAZ_NOW_PATH': str(tmp / 'NOW.md'), 'MAZ_LIVE_MEMORY_FILE': str(tmp / 'memory.md')})
        for key in ('DATA_DIR', 'WORK_DIR', 'CONTROL_DIR', 'DUMPS_DIR', 'TEACH_DIR', 'SKILL_VAULT_DIR',
                    'SKILL_DRAFT_DIR', 'DEBUG_DIR', 'FLOW_DIR'):
            env['MAZ_' + key] = str(tmp / key.lower())
        core = subprocess.Popen([sys.executable, '-m', 'mazhost'], cwd=tmp, env=env)
        try:
            for _ in range(120):
                if core.poll() is not None:
                    raise RuntimeError('Preview Core exited during startup.')
                try:
                    if request('/health').get('ok') and 'notes' in request('/memory/recall', token):
                        break
                except (OSError, urllib.error.URLError):
                    time.sleep(.25)
            else:
                raise RuntimeError('Preview Core did not become ready.')
            try:
                request('/memory/recall')
                raise RuntimeError('Preview unexpectedly allowed unauthenticated access.')
            except urllib.error.HTTPError as error:
                if error.code not in (401, 403):
                    raise
            if args.check_memory:
                session = request('/session/start', token, {})['session_id']
                saved = request('/turn/text', token, {'session_id': session, 'text': 'Remember that my appointment is Friday at noon.', 'route': 'local'})
                assert saved['provider'] == 'memory-local', saved
                request('/buddy/alert', token, {'source': 'reminder', 'kind': 'reminder', 'title': 'Synthetic reminder', 'delay_seconds': 8})
                core.terminate()
                core.wait(timeout=10)
                core = subprocess.Popen([sys.executable, '-m', 'mazhost'], cwd=tmp, env=env)
                for _ in range(120):
                    if core.poll() is not None:
                        raise RuntimeError('Restarted preview Core exited.')
                    try:
                        if request('/health').get('ok'):
                            break
                    except (OSError, urllib.error.URLError):
                        time.sleep(.25)
                else:
                    raise RuntimeError('Restarted preview Core did not become ready.')
                notes = request('/memory/recall?q=appointment', token)['notes']
                assert any('Friday at noon' in note['text'] for note in notes)
                fresh = request('/session/start', token, {})['session_id']
                recalled = request('/turn/text', token, {'session_id': fresh, 'text': 'When is my appointment?', 'route': 'local'}, timeout=90)
                assert not recalled.get('degraded'), recalled
                assert 'friday' in recalled['reply'].lower() and ('noon' in recalled['reply'].lower() or '12' in recalled['reply']), recalled
                print('Synthetic Ask memory survived a Core restart and a fresh conversation; local-model reply:', recalled['reply'])
                request('/buddy/alert', token, {'source': 'Phone', 'title': 'Mum', 'body': 'Synthetic: call tonight'})
                digest = request('/turn/text', token, {'session_id': fresh, 'text': 'Catch me up', 'route': 'local'})
                assert digest['provider'] == 'catchup-local' and 'Mum' in digest['reply'] and digest['reply'].endswith('Everything else can wait.'), digest
                print('Synthetic spoken Catch me up reply:', digest['reply'])
                for _ in range(60):   # the reminder was pending when Core stopped; it must still fire
                    if any(a['title'] == 'Synthetic reminder' and a['fired'] for a in request('/buddy/alerts', token)['alerts']):
                        break
                    time.sleep(.5)
                else:
                    raise AssertionError('Pending reminder was lost across the Core restart.')
                print('Pending reminder survived the Core restart and fired.')
            print('Isolated Core health and token authentication passed.')
        finally:
            core.terminate()
            try:
                core.wait(timeout=10)
            except subprocess.TimeoutExpired:
                core.kill()
                core.wait()


if __name__ == '__main__':
    main()
