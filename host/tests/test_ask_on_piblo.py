from fastapi.testclient import TestClient
from mazhost.app import create_app
from mazhost.config import Settings


def test_bearer_token_alone_cannot_allow_consequential_action():
    client = TestClient(create_app(Settings(token='test-secret', _env_file=None)))
    headers = {'Authorization': 'Bearer test-secret'}
    item = client.post('/buddy/request', headers=headers, json={
        'tool': 'Send email', 'summary': 'Send the draft', 'category': 'email'
    }).json()
    response = client.post('/buddy/decide', headers=headers, json={
        'id': item['id'], 'decision': 'allow'
    })
    assert response.status_code == 403
    assert client.get('/buddy/state', headers=headers, params={'id': item['id']}).json()['decision'] is None

import hashlib
import hmac
import pytest

KEY = 'test-device-key-that-is-independent'

@pytest.fixture
def ask(monkeypatch, tmp_path):
    monkeypatch.setenv('MAZ_ASK_DEVICE_KEY', KEY)
    monkeypatch.delenv('MAZ_ASK_LEGACY_DEVICE_DECIDE', raising=False)
    monkeypatch.setenv('MAZ_FOCUS_LOG', str(tmp_path / 'focus.jsonl'))
    client = TestClient(create_app(Settings(token='test-secret', buddy_db='off', _env_file=None)))
    client.headers.update({'Authorization': 'Bearer test-secret'})
    return client


def sign(item, decision='allow'):
    message = f"{item['id']}:{item['digest']}:{decision}:{item['nonce']}".encode()
    return hmac.new(KEY.encode(), message, hashlib.sha256).hexdigest()


def request(client, **fields):
    return client.post('/buddy/request', json={'tool': 'Send email', 'summary': 'Send draft', **fields}).json()


def test_signed_decision_is_bound_to_request_and_cannot_replay(ask):
    a, b = request(ask), request(ask)
    assert ask.post('/buddy/decide', json={'id': b['id'], 'decision': 'allow', 'proof': sign(a)}).status_code == 403
    assert ask.post('/buddy/decide', json={'id': a['id'], 'decision': 'allow', 'proof': sign(a)}).json()['decision'] == 'allow'
    assert ask.get('/buddy/state', params={'id': a['id']}).json()['digest'] == a['digest']
    assert ask.post('/buddy/decide', json={'id': a['id'], 'decision': 'allow', 'proof': sign(a)}).status_code == 409


@pytest.mark.parametrize('category', ['purchase', 'delete'])
def test_risky_categories_are_locked_until_owner_enables_them(ask, monkeypatch, category):
    item = request(ask, category=category)
    assert item['decision'] == 'deny'
    monkeypatch.setenv('MAZ_ASK_UNLOCK_' + category.upper(), '1')
    item = request(ask, category=category)
    assert item['decision'] is None
    assert ask.post('/buddy/decide', json={'id': item['id'], 'decision': 'allow', 'proof': sign(item)}).json()['decision'] == 'allow'


def test_edit_is_a_terminal_non_approval(ask):
    item = request(ask)
    result = ask.post('/buddy/decide', json={'id': item['id'], 'decision': 'edit', 'instruction': 'Use the revised draft'})
    assert result.json()['decision'] == 'edit'
    assert ask.get('/buddy/state', params={'id': item['id']}).json()['instruction'] == 'Use the revised draft'
    assert ask.post('/buddy/decide', json={'id': item['id'], 'decision': 'allow', 'proof': sign(item)}).status_code == 409


def test_focus_holds_nonurgent_without_expiring(ask):
    ask.post('/focus/start', json={'minutes': 5, 'task': 'Focus'})
    held = request(ask)
    urgent = request(ask, urgent=True)
    pending = ask.get('/buddy/pending').json()['pending']
    assert [item['id'] for item in pending] == [urgent['id']]
    assert ask.get('/buddy/state', params={'id': held['id']}).json()['decision'] is None
    ask.post('/focus/end', json={'done': False})
    assert {item['id'] for item in ask.get('/buddy/pending').json()['pending']} == {held['id'], urgent['id']}


def test_mutated_request_cannot_be_approved(monkeypatch):
    from mazhost.buddy import Buddy
    monkeypatch.setenv('MAZ_ASK_DEVICE_KEY', KEY)
    buddy = Buddy()
    item = buddy.request('Send email', 'Original')
    buddy._items[item['id']]['summary'] = 'Changed'
    with pytest.raises(PermissionError):
        buddy.decide(item['id'], 'allow', proof=sign(item))


def test_undo_records_reversal_only_within_window(ask, monkeypatch):
    from mazhost import buddy as buddy_module
    item = request(ask, undo='Recall message')
    allowed = ask.post('/buddy/decide', json={'id': item['id'], 'decision': 'allow', 'proof': sign(item)}).json()
    undone = ask.post('/buddy/decide', json={'id': item['id'], 'decision': 'undo', 'proof': sign(allowed, 'undo')})
    assert undone.json()['decision'] == 'undone'
    assert ask.get('/buddy/state', params={'id': item['id']}).json()['decision'] == 'undone'
    other = request(ask, undo='Recall message')
    allowed = ask.post('/buddy/decide', json={'id': other['id'], 'decision': 'allow', 'proof': sign(other)}).json()
    real = buddy_module.time.time
    monkeypatch.setattr(buddy_module.time, 'time', lambda: real() + 31)
    assert ask.post('/buddy/decide', json={'id': other['id'], 'decision': 'undo', 'proof': sign(allowed, 'undo')}).status_code == 409


def test_undo_window_extends_past_request_deadline(ask, monkeypatch):
    from mazhost import buddy as buddy_module
    real = buddy_module.time.monotonic
    clock = [0]
    monkeypatch.setattr(buddy_module.time, 'monotonic', lambda: real() + clock[0])
    item = request(ask, undo='Recall message')
    clock[0] = 59
    allowed = ask.post('/buddy/decide', json={'id': item['id'], 'decision': 'allow', 'proof': sign(item)}).json()
    clock[0] = 61
    assert ask.post('/buddy/decide', json={'id': item['id'], 'decision': 'undo', 'proof': sign(allowed, 'undo')}).json()['decision'] == 'undone'
    assert ask.get('/buddy/state', params={'id': item['id']}).json()['decision'] == 'undone'


def test_pause_all_denies_future_requests(ask):
    ask.post('/ask/pause', json={'on': True})
    assert request(ask)['decision'] == 'deny'


@pytest.mark.parametrize('category', ['email', 'calendar', 'purchase', 'delete', 'deploy', 'other'])
def test_card_contains_the_action_details(ask, category):
    item = request(ask, agent='Helper', category=category, amount='10 credits', recipient='Team')
    assert item['card'] == ['Who: Helper', 'What: Send email', 'Details: Send draft', 'Amount: 10 credits', 'Where: Team', 'Category: ' + category]


def test_pairing_key_proves_decisions_after_restart(tmp_path):
    settings = Settings(token='test-secret', data_dir=str(tmp_path), buddy_db='off', _env_file=None)
    client = TestClient(create_app(settings))
    client.headers.update({'Authorization': 'Bearer test-secret'})
    pair = client.post('/pair/device/request', json={'device_id': 'device-123', 'name': 'Piblo', 'approval_proof': True}).json()
    assert 'approval_key' not in pair
    assert client.post(f"/pair/device/{pair['request_id']}/approve").status_code == 200
    credentials = client.get(f"/pair/device/request/{pair['request_id']}").json()
    assert credentials['device_id'] == 'device-123'
    client = TestClient(create_app(settings))
    client.headers.update({'Authorization': 'Bearer test-secret', 'X-Piblo-Device-Id': 'device-123'})
    item = request(client)
    message = f"{item['id']}:{item['digest']}:allow:{item['nonce']}".encode()
    proof = hmac.new(credentials['approval_key'].encode(), message, hashlib.sha256).hexdigest()
    assert client.post('/buddy/decide', json={'id': item['id'], 'decision': 'allow', 'proof': proof}).json()['decision'] == 'allow'


def test_focus_start_and_end_extend_an_existing_deadline_without_polling(ask, monkeypatch):
    from mazhost import buddy as buddy_module
    real = buddy_module.time.monotonic
    clock = [0]
    monkeypatch.setattr(buddy_module.time, 'monotonic', lambda: real() + clock[0])
    item = request(ask)
    clock[0] += 10
    ask.post('/focus/start', json={'minutes': 5, 'task': 'Focus'})
    clock[0] += 90
    assert ask.get('/buddy/pending').json()['pending'] == []
    assert ask.get('/buddy/state', params={'id': item['id']}).json()['decision'] is None
    ask.post('/focus/end', json={'done': False})
    assert ask.get('/buddy/state', params={'id': item['id']}).json()['decision'] is None
    assert [x['id'] for x in ask.get('/buddy/pending').json()['pending']] == [item['id']]


def test_undo_and_digest_survive_restart(tmp_path, monkeypatch):
    monkeypatch.setenv('MAZ_ASK_DEVICE_KEY', KEY)
    monkeypatch.delenv('MAZ_ASK_LEGACY_DEVICE_DECIDE', raising=False)
    cfg = Settings(token='test-secret', data_dir=str(tmp_path), buddy_db=str(tmp_path / 'buddy.db'), _env_file=None)
    client = TestClient(create_app(cfg), headers={'Authorization': 'Bearer test-secret'})
    item = request(client, undo='Recall message')
    allowed = client.post('/buddy/decide', json={'id': item['id'], 'decision': 'allow', 'proof': sign(item)}).json()
    assert client.post('/buddy/decide', json={'id': item['id'], 'decision': 'undo', 'proof': sign(allowed, 'undo')}).json()['decision'] == 'undone'
    client = TestClient(create_app(cfg), headers={'Authorization': 'Bearer test-secret'})
    state = client.get('/buddy/state', params={'id': item['id']}).json()
    assert state['decision'] == 'undone'
    assert state['digest'] == item['digest']


def test_card_wraps_long_fields_into_short_lines(ask):
    item = request(ask, agent='A very long agent name', recipient='A particularly long recipient address', category='email')
    assert all(len(line) <= 24 for line in item['card'])
    assert 'recipient address' in ' '.join(item['card'])
