import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mazhost.buddy_forms import build_buddy_forms_router, current_form, forms
from mazhost.onboarding import Onboarding, STEPS, build_onboarding_router


@pytest.mark.parametrize('stats,expected', [
    ({}, 'seed'),
    ({'focus_sessions_completed_7d': 2}, 'seed'),
    ({'focus_sessions_completed_7d': 3}, 'monk'),
    ({'agents_built': 2}, 'tinkerer'),
    ({'goals_or_travel_events': 3}, 'explorer'),
    ({'activity_after_22_7d': 6, 'activity_total_7d': 10}, 'night_owl'),
    ({'activity_after_22_7d': 5, 'activity_total_7d': 10}, 'seed'),
    ({'activity_after_22_7d': 0, 'activity_total_7d': 0}, 'seed'),
    ({'tasks_done_before_noon': 5}, 'sunny'),
    ({'focus_sessions_completed_7d': 3, 'agents_built': 2}, 'monk'),
])
def test_form_rules(stats, expected):
    assert current_form(stats)['id'] == expected


def test_artwork_has_six_distinct_grids():
    available = forms()
    assert len(available) == 6
    assert len({str(form['pixel_art']) for form in available}) == 6
    for form in available:
        assert len(form['pixel_art']) == 16
        assert all(len(row) == 16 and all(0 <= pixel < 5 for pixel in row) for row in form['pixel_art'])


def test_onboarding_routes_walk_and_persist(tmp_path):
    onboarding = Onboarding(tmp_path)
    api = FastAPI()
    api.include_router(build_onboarding_router(onboarding))
    api.include_router(build_buddy_forms_router(onboarding=onboarding))
    client = TestClient(api)
    assert client.get('/buddy/form').json()['id'] == 'seed'
    for (step, _), answer in zip(STEPS, ['Alex', 'Busy', 'Water plants', 'Grow herbs', 'Ready', 'Yes']):
        assert client.get('/onboarding').json()['step'] == step
        state = client.post('/onboarding/answer', json={'text': answer}).json()
        if step == 'watch_this':
            assert state['play_watch_this'] is True
        if step == 'first_form':
            assert state['form_change'] == {'from': 'seed', 'to': 'explorer'}
    assert state['complete'] and not state['can_skip']
    assert Onboarding(tmp_path).state()['name'] == 'Alex'
    assert state['wish'] == {'text': 'Water plants', 'goal': 'Grow herbs'}
    assert client.get('/buddy/form').json()['id'] == 'explorer'
    assert client.post('/onboarding/skip').json()['complete']


def test_every_onboarding_step_can_be_skipped(tmp_path):
    onboarding = Onboarding(tmp_path)
    for _ in STEPS:
        state = onboarding.skip()
    assert state['complete']
    assert state['skipped'] == [step for step, _ in STEPS]
    assert 'wish' not in state and 'first_form_id' not in state and 'watch_played' not in state


def test_form_route_reads_current_stats():
    stats = {}
    api = FastAPI()
    api.include_router(build_buddy_forms_router(lambda: stats))
    client = TestClient(api)
    assert client.get('/buddy/form').json()['id'] == 'seed'
    stats['focus_sessions_completed_7d'] = 3
    assert client.get('/buddy/form').json()['id'] == 'monk'
