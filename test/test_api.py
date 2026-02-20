def test_status(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    assert resp.json == {"status": "healthy"}

def test_add_product_validation(client):
    # Missing body
    resp = client.post("/api/products",json={})
    assert resp.status_code == 400

    # Empty name
    resp = client.post("/api/products", json={"name": "", "description": "desc", "price": 10})
    assert resp.status_code == 400

    # Empty description
    resp = client.post("/api/products", json={"name": "Test", "description": "", "price": 10})
    assert resp.status_code == 400

    # Invalid price
    resp = client.post("/api/products", json={"name": "Test", "description": "desc", "price": -5})
    assert resp.status_code == 400

def test_add_product_success(client):
    resp = client.post("/api/products", json={"name": "Phone", "description": "Smartphone", "price": 800})
    assert resp.status_code == 201
    data = resp.json
    assert data["name"] == "Phone"
    assert data["price"] == 800

def test_list_products(client):
    resp = client.get("/api/products")
    assert resp.status_code == 200
    assert isinstance(resp.json, list)

def test_rate_limit(client):
    for i in range(5):
        resp = client.post("/api/protected-action", json={"action": "test"})
        assert resp.status_code == 200

    # 6th request should fail
    resp = client.post("/api/protected-action", json={"action": "test"})
    assert resp.status_code == 429
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers
    assert "X-RateLimit-Reset" in resp.headers

def test_metrics(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "api_requests_total" in resp.data.decode()
