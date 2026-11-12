from fastapi import FastAPI
from fastapi.testclient import TestClient


def client(tmp_path):
    from mazhost.features import build_features_router
    app = FastAPI()
    app.include_router(build_features_router(tmp_path))
    return TestClient(app)


def test_every_feature_starts_in_testing_with_steps(tmp_path):
    rows = client(tmp_path).get('/features').json()['features']
    ids = {row['id'] for row in rows}
    assert {'ask-on-piblo', 'private-mode', 'where-was-i-park-it', 'catch-me-up', 'maker'} <= ids
    assert all(row['status'] == 'testing' and row['steps'] and row['summary'] for row in rows)


def test_confirm_then_unconfirm_round_trip(tmp_path):
    api = client(tmp_path)
    row = api.post('/features/private-mode/confirm', json={'note': 'blocked cloud ok'}).json()
    assert row['status'] == 'confirmed' and row['confirmed_at'] and row['note'] == 'blocked cloud ok'
    # survives a new router instance (persisted)
    assert next(r for r in client(tmp_path).get('/features').json()['features'] if r['id'] == 'private-mode')['status'] == 'confirmed'
    assert api.post('/features/private-mode/unconfirm').json()['status'] == 'testing'


def test_unknown_feature_and_bad_body_rejected(tmp_path):
    api = client(tmp_path)
    assert api.post('/features/nope/confirm', json={}).status_code == 404
    assert api.post('/features/memory/confirm', json={'note': 'x', 'extra': 1}).status_code == 422
    assert not (tmp_path / 'dev' / 'features.json').exists()


def test_features_routes_require_token(tmp_path):
    from mazhost.app import create_app
    from mazhost.config import Settings
    app = create_app(Settings(data_dir=str(tmp_path), work_dir=str(tmp_path / 'work'), buddy_db='off', token='test-token', _env_file=None))
    api = TestClient(app)
    for method, path in [('get', '/features'), ('post', '/features/memory/confirm'), ('post', '/features/memory/unconfirm')]:
        assert getattr(api, method)(path).status_code in (401, 429), path


def test_bare_confirm_and_damaged_store_never_wipes(tmp_path):
    api = client(tmp_path)
    assert api.post('/features/memory/confirm').json()['status'] == 'confirmed'
    store = tmp_path / 'dev' / 'features.json'
    store.write_text('{not json', encoding='utf-8')
    assert api.get('/features').status_code == 500
    assert (tmp_path / 'dev' / 'features.json.corrupt').read_text(encoding='utf-8') == '{not json'
    # after setting it aside, Core starts clean rather than half-reading damaged data
    assert api.get('/features').status_code == 200
