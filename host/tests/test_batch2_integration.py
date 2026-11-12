from collections import Counter

from fastapi.testclient import TestClient

from mazhost.app import create_app
from mazhost.config import Settings


def route_pairs(routes, prefix=""):
    for route in routes:
        if hasattr(route, "original_router"):
            yield from route_pairs(route.original_router.routes, prefix + route.include_context.prefix)
        else:
            for method in getattr(route, "methods", set()):
                yield method, prefix + route.path


def test_batch2_routes_are_unique_and_protected(tmp_path):
    cfg = Settings(token="integration-token", data_dir=str(tmp_path / "data"),
                   dumps_dir=str(tmp_path / "inbox"), buddy_db="off", _env_file=None)
    app = create_app(cfg)
    routes = Counter(route_pairs(app.routes))
    assert not {route: count for route, count in routes.items() if count > 1}
    expected = [("GET", "/privacy"), ("GET", "/where"), ("GET", "/memory/recall"),
                ("GET", "/catchup"), ("GET", "/buddy/form"), ("GET", "/onboarding"),
                ("GET", "/agents"), ("GET", "/rescue"), ("POST", "/share"),
                ("POST", "/buddy/request"), ("GET", "/learning"), ("POST", "/speaks-first/check")]
    assert {route: routes[route] for route in expected if routes[route] != 1} == {}
    client = TestClient(app)
    for method, path in expected:
        assert client.request(method, path).status_code in (401, 429), path  # 429 = failed-auth limiter after 10 tries


def test_speaks_first_uses_learning_notes(tmp_path):
    cfg = Settings(token="integration-token", data_dir=str(tmp_path / "data"),
                   dumps_dir=str(tmp_path / "inbox"), buddy_db="off", _env_file=None)
    client = TestClient(create_app(cfg))
    headers = {"Authorization": "Bearer integration-token"}
    (tmp_path / "data" / "learning-speaks-first.md").write_text("15 minutes", encoding="utf-8")
    result = client.post("/speaks-first/check", headers=headers,
                         json={"events": [{"title": "Call", "start": 1000}], "now": 200})
    assert result.status_code == 200
    assert result.json()["posted"] == ["Meeting in 15: Call"]
    assert client.get("/learning", headers=headers).status_code == 200
