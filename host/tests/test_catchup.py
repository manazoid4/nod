from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mazhost.buddy import AlertIn, Buddy
from mazhost.buddy_store import BuddyStore
from mazhost.catchup import Catchup, DEFAULT_RULES, classify, build_catchup_router


@pytest.mark.parametrize('note,expected', [
    ({'sender': 'Mum'}, 'through_now'),
    ({'sender': 'Alex'}, 'through_now'),
    ({'category': 'delivery'}, 'quiet'),
    ({'source': 'Shopping'}, 'quiet'),
    ({'category': 'social'}, 'silent'),
    ({'source': 'Instagram'}, 'silent'),
    ({'sender': 'Dentist'}, 'summary'),
    ({'sender': 'Skipped'}, 'silent'),
])
def test_classification(note, expected):
    rules = {**DEFAULT_RULES, 'key_contacts': ['Alex'], 'skip_senders': ['Skipped']}
    assert classify(note, rules) == expected


def test_summary_uses_phone_calendar_and_saves_and_caps_model(tmp_path):
    from mazhost import library
    buddy = Buddy(store=BuddyStore(tmp_path / 'buddy.sqlite3'))
    buddy.post_alert(AlertIn(source='Phone', title='Mum', body='Call tonight'))
    library.save_item(tmp_path / 'library', text='Garden plans', project='home')

    class Calendar:
        def events(self, start, end):
            return [{'title': 'Dentist at noon'}]

    svc = Catchup(tmp_path, buddy, tmp_path / 'library', calendar=Calendar())
    text = svc.catch_me_up(datetime.now(timezone.utc))
    assert all(word in text for word in ['Mum', 'Dentist', 'Garden'])
    assert text.endswith('Everything else can wait.')
    assert len(text.split()) <= 300
    text = svc.catch_me_up(datetime.now(timezone.utc), llm=lambda system, user: 'word ' * 1000)
    assert len(text.split()) <= 300
    assert text.endswith('Everything else can wait.')


def test_rules_persist_and_reply_only_requests_approval(tmp_path):
    buddy = Buddy()
    note = buddy.post_alert(AlertIn(source='Phone', title='Alex', body='Coming?'))
    svc = Catchup(tmp_path, buddy, tmp_path / 'library')
    api = FastAPI()
    api.include_router(build_catchup_router(svc))
    client = TestClient(api)
    assert client.put('/filter/rules', json={'key_contacts': ['Alex']}).status_code == 200
    assert Catchup(tmp_path, buddy, tmp_path / 'library').rules()['key_contacts'] == ['Alex']
    assert client.put('/filter/rules', json={'key_contacts': 'invalid'}).status_code == 422
    assert client.get('/filter/replies').json()['replies'][0] == 'On my way'
    response = client.post('/filter/reply', json={'notification_id': note['id'], 'reply_index': 0})
    assert response.status_code == 200
    pending = buddy.pending()
    assert len(pending) == 1
    assert pending[0]['category'] == 'message'
    assert pending[0]['decision'] is None
    assert pending[0]['sensitive'] is True
    assert 'On my way' in pending[0]['summary']
    assert 'On my way' not in str(buddy.events())
    assert client.post('/filter/reply', json={'notification_id': 'missing', 'reply_index': 0}).status_code == 404
    assert client.post('/filter/reply', json={'notification_id': note['id'], 'reply_index': -1}).status_code == 422
    shown = buddy.summary()['items'][0]
    assert 'On my way' in shown['summary'] and 'NOD' not in shown['summary']
    buddy.decide(pending[0]['id'], 'deny')
    assert 'On my way' not in str(buddy.events())


def test_phone_alerts_survive_restart_and_silent_senders_stay_out(tmp_path):
    store = BuddyStore(tmp_path / 'buddy.sqlite3')
    buddy = Buddy(store=store)
    buddy.post_alert(AlertIn(source='Messages', title='Mum', body='Phone tonight'))
    buddy.post_alert(AlertIn(source='Instagram', title='New photo', body='Social noise'))
    restarted = Buddy(store=store)
    service = Catchup(tmp_path, restarted, tmp_path / 'library')
    text = service.catch_me_up(datetime.now(timezone.utc))
    assert 'Mum' in text and 'Phone tonight' in text
    assert 'Social noise' not in text and 'New photo' not in text
    service.update_rules({'skip_senders': ['Mum']})
    assert 'Mum' not in service.catch_me_up(datetime.now(timezone.utc))


def test_template_is_capped_and_model_failure_uses_template(tmp_path):
    buddy = Buddy()
    for i in range(15):
        buddy.post_alert(AlertIn(title=f'Contact {i}', body='word ' * 40))
    service = Catchup(tmp_path, buddy, tmp_path / 'library')

    def offline(system, user):
        raise RuntimeError('offline')

    for model in (None, offline, lambda system, user: 'Everything else can wait. ' * 1000):
        text = service.catch_me_up(datetime.now(timezone.utc), model)
        assert len(text.split()) <= 300
        assert text.endswith('Everything else can wait.')
        assert text.count('Everything else can wait.') == 1
