"""Prove saved captures on an isolated Core (:18837), with no installed services."""
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

ROOT = Path(__file__).resolve().parents[1]
PORT = 18837


def request(path, token=None, body=None):
    headers = {'Authorization': 'Bearer ' + token} if token else {}
    req = urllib.request.Request(
        f'http://127.0.0.1:{PORT}{path}',
        headers={**headers, 'Content-Type': 'application/json'},
        data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.load(response)


def start(tmp, env):
    core = subprocess.Popen([sys.executable, '-m', 'mazhost'], cwd=tmp, env=env)
    try:
        for _ in range(120):
            if core.poll() is not None:
                raise RuntimeError('Preview Core exited; see its logs/core.log.')
            try:
                if request('/health').get('ok'):
                    return core
            except OSError:
                time.sleep(.25)
        raise RuntimeError('Preview Core did not become ready.')
    except BaseException:
        stop(core)
        raise


def stop(core):
    core.terminate()
    try:
        core.wait(timeout=10)
    except subprocess.TimeoutExpired:
        core.kill()
        core.wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Run the isolated API proof (default)')
    parser.add_argument('--serve', action='store_true', help='Keep the synthetic preview open for browser checks')
    args = parser.parse_args()
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', PORT)) == 0:
            raise SystemExit(f'Port {PORT} is in use; preview was not started.')
    artifacts = ROOT / '.device-diagnostic'
    artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='saved-preview-', dir=artifacts) as temp:
        tmp = Path(temp)
        token = secrets.token_urlsafe(32)
        (tmp / '.env').write_text(f'MAZ_TOKEN={token}\nMAZ_PORT={PORT}\n', encoding='utf-8')
        env = {k: v for k, v in os.environ.items() if not k.startswith(('MAZ_', 'PIBLO_', 'NOD_'))}
        env.update({'PYTHONPATH': str(ROOT / 'host'), 'MAZ_TOKEN': token, 'MAZ_BIND': '127.0.0.1',
                    'MAZ_PORT': str(PORT), 'MAZ_DISCOVERY_PORT': '0', 'MAZ_AUTOUPDATE': 'false',
                    'MAZ_BRIDGE_ENABLED': 'false', 'MAZ_REMOTE_DETECT': 'false', 'MAZ_PRIVATE_MODE': 'true',
                    'MAZ_TTS_ENABLED': 'false', 'MAZ_KOKORO_PCM_PORT': '0',
                    'MAZ_OLLAMA_URL': 'http://127.0.0.1:9', 'MAZ_LLAMACPP_URL': 'http://127.0.0.1:9',
                    'MAZ_BUDDY_DB': str(tmp / 'buddy.sqlite3'), 'MAZ_CORE_ENABLED': 'false',
                    'MAZ_NOW_PATH': str(tmp / 'NOW.md'), 'MAZ_LIVE_MEMORY_FILE': str(tmp / 'memory.md')})
        for key in ('DATA_DIR', 'WORK_DIR', 'CONTROL_DIR', 'DUMPS_DIR', 'TEACH_DIR', 'SKILL_VAULT_DIR',
                    'SKILL_DRAFT_DIR', 'DEBUG_DIR', 'FLOW_DIR'):
            env['MAZ_' + key] = str(tmp / key.lower())
        core = start(tmp, env)
        try:
            try:
                request('/dumps')
                raise AssertionError('Unauthenticated dump access was allowed.')
            except urllib.error.HTTPError as error:
                assert error.code == 401
            empty = request('/dumps/catch-up', token)
            assert empty['dumps'] == [] and empty['actions'] == []
            texts = ['Amberkite: I need to bring the blue folder.', 'Amberkite: I need to book a quiet room.']
            ids = [request('/dumps', token, {'text': text, 'source': 'web', 'project': 'preview'})['dump_id'] for text in texts]
            stop(core)
            core = start(tmp, env)
            listed = request('/dumps', token)['dumps']
            assert {d['id'] for d in listed} == set(ids)
            for dump_id, text in zip(ids, texts):
                original = request('/dumps/' + dump_id, token)
                assert original['transcript'] == text and original['created']
                assert 'nonexistent-term' not in original['body']
            print('PASS: authenticated saved captures survived a Core restart; both originals match.', flush=True)
            digest = request('/dumps/catch-up', token)
            assert {d['id'] for d in digest['dumps']} == set(ids)
            assert {a['id'] for a in digest['actions']} == set(ids)
            assert digest['window_start'] < digest['window_end']
            for action in digest['actions']:
                assert action['text'] in request('/dumps/' + action['id'], token)['body']
            request('/dumps/' + ids[0] + '/done', token, {'agent': 'web'})
            refreshed = request('/dumps/catch-up', token)
            assert [a['id'] for a in refreshed['actions']] == [ids[1]]
            assert len(refreshed['dumps']) == 2
            print('PASS: catch-up empty state, source links, coverage and done-state refresh; no model used.', flush=True)
            if args.serve:
                print(f'Browser preview: http://127.0.0.1:{PORT}/ui; private token file: {tmp / ".env"}', flush=True)
                while core.poll() is None:
                    time.sleep(.5)
        finally:
            stop(core)


if __name__ == '__main__':
    main()
