import pytest

def test_status(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"

def test_protected_action_success(client):
    resp = client.post("/api/protected-action", json={"action": "test"})
    assert resp.status_code == 200
    assert "message" in resp.get_json()

def test_rate_limit(client):
    # First 5 requests succeed
    for i in range(5):
        resp = client.post("/api/protected-action", json={"action": "test"})
        assert resp.status_code == 200

    # 6th request blocked
    resp = client.post("/api/protected-action", json={"action": "test"})
    assert resp.status_code == 429
    assert resp.get_json()["error"] == "Too Many Requests"
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers
    assert "X-RateLimit-Reset" in resp.headers

@pytest.mark.skip(reason="slow test, requires wait for reset window")
def test_rate_limit_reset(client):
    for i in range(5):
        client.post("/api/protected-action", json={"action": "test"})
    resp = client.post("/api/protected-action", json={"action": "test"})
    assert resp.status_code == 429

    import time
    time.sleep(60)
    resp = client.post("/api/protected-action", json={"action": "test"})
    assert resp.status_code == 200
