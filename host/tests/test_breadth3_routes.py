from fastapi.testclient import TestClient

from mazhost.app import create_app
from mazhost.config import Settings


def test_all_new_routes_require_bearer_and_work_with_it(tmp_path):
    class Model:
        def chat(self, messages, route):
            return 'A useful saved idea.', 'fake'

    cfg = Settings(token='breadth3-test-token', data_dir=str(tmp_path / 'data'),
                   dumps_dir=str(tmp_path / 'inbox'), buddy_db='off', _env_file=None)
    client = TestClient(create_app(cfg, models=Model()))
    routes = [('GET', '/catchup', None), ('GET', '/filter/rules', None),
              ('PUT', '/filter/rules', {'key_contacts': ['Alex']}),
              ('GET', '/filter/replies', None),
              ('POST', '/filter/reply', {'notification_id': 'missing', 'reply_index': 0}),
              ('POST', '/share', {'captions': 'Keep this useful idea.'}),
              ('GET', '/buddy/form', None), ('GET', '/onboarding', None),
              ('POST', '/onboarding/answer', {'text': 'Alex'}), ('POST', '/onboarding/skip', None)]
    for method, path, body in routes:
        assert client.request(method, path, json=body).status_code == 401, path
    client = TestClient(create_app(cfg, models=Model()))
    headers = {'Authorization': 'Bearer breadth3-test-token'}
    for method, path, body in routes:
        response = client.request(method, path, json=body, headers=headers)
        assert response.status_code == (404 if path == '/filter/reply' else 200), response.text
