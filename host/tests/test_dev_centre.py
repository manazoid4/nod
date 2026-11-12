from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_checklist_round_trip(tmp_path):
    from mazhost.dev_centre import build_dev_router
    folder = tmp_path / 'dev' / 'checklists'
    folder.mkdir(parents=True)
    path = folder / 'custom.md'
    path.write_text('# Heading\n\n- [ ] First task\nKeep this line\n', encoding='utf-8')
    app = FastAPI()
    app.include_router(build_dev_router(tmp_path, tmp_path))
    client = TestClient(app)
    lists = client.get('/dev/checklists').json()['lists']
    item = lists[0]['items'][0]
    assert client.post(f"/dev/checklists/custom/items/{item['id']}", json={'done': True}).status_code == 200
    assert path.read_text(encoding='utf-8') == '# Heading\n\n- [x] First task\nKeep this line\n'
    assert client.post(f"/dev/checklists/custom/items/{item['id']}", json={'done': False}).status_code == 200
    assert '- [ ] First task' in path.read_text(encoding='utf-8')


def make_client(tmp_path):
    from mazhost.dev_centre import build_dev_router
    app = FastAPI()
    app.include_router(build_dev_router(tmp_path, tmp_path))
    return TestClient(app)


def test_seed_only_if_empty_and_record_proof(tmp_path):
    client = make_client(tmp_path)
    lists = client.get('/dev/checklists').json()['lists']
    assert {row['id'] for row in lists} == {'founder-today', 'feature-tests', 'kickstarter-gates'}
    item = next(row for row in lists if row['id'] == 'feature-tests')['items'][0]
    assert client.post(f"/dev/checklists/feature-tests/items/{item['id']}", json={'done': True, 'note': 'seen'}).status_code == 200
    result = client.get('/dev/checklists').json()['lists']
    ticked = next(row for row in result if row['id'] == 'feature-tests')['items'][0]
    assert ticked['when'] and ticked['note'] == 'seen'
    assert client.post(f"/dev/checklists/feature-tests/items/{item['id']}", json={'done': False}).status_code == 200
    assert 'when' not in next(row for row in client.get('/dev/checklists').json()['lists'] if row['id'] == 'feature-tests')['items'][0]
    (tmp_path / 'dev/checklists/founder-today.md').unlink()
    assert 'founder-today' not in {row['id'] for row in client.get('/dev/checklists').json()['lists']}


def test_content_approval_encoding_and_status(tmp_path):
    from urllib.parse import parse_qs, urlsplit
    client = make_client(tmp_path)
    draft = client.post('/dev/content/from-feature', json={'feature': 'Notes & focus', 'summary': 'A & B? ' * 80}).json()
    x = next(t for t in draft['targets'] if t['platform'] == 'x')
    assert len(x['body']) <= 280
    reddit_targets = [t for t in draft['targets'] if t['platform'] == 'reddit']
    assert len(reddit_targets) == 8
    assert len({t['title'] for t in reddit_targets}) > 1
    assert len({t['body'] for t in reddit_targets}) > 1
    ident = draft['id']
    assert client.get(f'/dev/content/{ident}/share').status_code == 409
    assert client.post(f'/dev/content/{ident}/posted').status_code == 409
    approved = client.post(f'/dev/content/{ident}/approve').json()
    reddit = next(s for s in approved['shares'] if s['platform'] == 'reddit')
    assert parse_qs(urlsplit(reddit['url']).query)['title'] == ['Building Piblo: Notes & focus']
    assert client.post(f'/dev/content/{ident}/posted').json()['status'] == 'posted'
    updated = client.put(f'/dev/content/{ident}', json={'title': 'Changed', 'body': 'Text', 'targets': []}).json()
    assert updated['status'] == 'draft'
    assert client.get(f'/dev/content/{ident}/share').status_code == 409
    assert client.delete(f'/dev/content/{ident}').status_code == 200


def test_usage_redacts_and_github_unavailable(tmp_path, monkeypatch):
    import json
    from mazhost import dev_centre
    session = tmp_path / '.codex/sessions/2026/01/01/a.jsonl'
    session.parent.mkdir(parents=True)
    session.write_text(json.dumps({'payload': {'rate_limits': {'primary': {'used_percent': 81, 'resets_at': 123}, 'secondary': {'used_percent': 2, 'resets_at': 456}}}}), encoding='utf-8')
    monkeypatch.setattr(dev_centre.Path, 'home', lambda: tmp_path)
    private_email = 'secret' + chr(64) + 'example.test'
    def fake_cli(args, **kwargs):
        if args[0] == 'gh':
            raise FileNotFoundError()
        return json.dumps({'accounts': [{'number': 1, 'email': private_email, 'usage': {'fiveHour': {'pct': 90, 'resetsAt': 'tomorrow'}, 'sevenDay': {'pct': 10, 'resetsAt': 'later'}}}]})
    monkeypatch.setattr(dev_centre, 'run_cli', fake_cli)
    client = make_client(tmp_path)
    result = client.get('/dev/usage').json()
    assert result['claude']['accounts'][0]['five_hour']['used_percent'] == 90
    assert result['codex']['primary']['used_percent'] == 81
    assert private_email not in json.dumps(result)
    assert client.get('/dev/github').json() == {'available': False}
    assert client.get('/dev/overview').json()['usage_warnings'] == 2


def test_app_routes_require_token(tmp_path):
    from mazhost.app import create_app
    from mazhost.config import Settings
    app = create_app(Settings(data_dir=str(tmp_path), work_dir=str(tmp_path / 'work'), buddy_db='off', token='test-token', _env_file=None))
    client = TestClient(app)
    for index, (method, path) in enumerate([('get', '/dev/checklists'), ('post', '/dev/checklists/a/items/b'), ('get', '/dev/content'), ('post', '/dev/content'), ('post', '/dev/content/from-feature'), ('put', '/dev/content/a'), ('post', '/dev/content/a/approve'), ('get', '/dev/content/a/share'), ('post', '/dev/content/a/posted'), ('delete', '/dev/content/a'), ('get', '/dev/usage'), ('get', '/dev/github'), ('get', '/dev/overview')]):
        client = TestClient(app, client=(f'testclient{index}', 50000))
        assert getattr(client, method)(path).status_code == 401, path


def test_link_post_and_private_github(tmp_path, monkeypatch):
    from urllib.parse import parse_qs, urlsplit
    from mazhost import dev_centre, private_mode
    client = make_client(tmp_path)
    draft = client.post('/dev/content', json={'title': 'A & B', 'body': 'Text', 'link': 'https://example.org/?a=1&b=2', 'targets': [{'platform': 'reddit', 'subreddit': 'esp32', 'post_type': 'link'}]}).json()
    share = client.post(f"/dev/content/{draft['id']}/approve").json()['shares'][0]
    assert parse_qs(urlsplit(share['url']).query)['url'] == ['https://example.org/?a=1&b=2']
    calls = []
    monkeypatch.setattr(dev_centre, 'run_cli', lambda *args, **kwargs: calls.append(args) or '[]')
    private_mode.set_enabled(False)
    assert client.get('/dev/github').json()['available']
    assert client.get('/dev/github').json()['available']
    assert len(calls) == 1
    private_mode.set_enabled(True)
    try:
        assert client.get('/dev/github').json() == {'available': False}
        assert len(calls) == 1
    finally:
        private_mode.set_enabled(False)


def test_private_mode_does_not_run_cswap(tmp_path, monkeypatch):
    from mazhost import dev_centre, private_mode
    import subprocess
    monkeypatch.setattr(dev_centre.Path, 'home', lambda: tmp_path)
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('subprocess launched')))
    private_mode.set_enabled(True)
    try:
        assert dev_centre.usage()['claude'] == {'available': False}
    finally:
        private_mode.set_enabled(False)


def test_overview_counts_each_failing_check(tmp_path, monkeypatch):
    import json
    from mazhost import dev_centre, private_mode
    private_mode.set_enabled(False)
    monkeypatch.setattr(dev_centre, 'usage', lambda: {'claude': {}, 'codex': {}})
    monkeypatch.setattr(dev_centre, 'run_cli', lambda *args, **kwargs: json.dumps([{'statusCheckRollup': [{'conclusion': 'FAILURE'}, {'conclusion': 'TIMED_OUT'}, {'conclusion': 'SUCCESS'}]}]))
    assert make_client(tmp_path).get('/dev/overview').json()['failing_pr_checks'] == 2
