import pytest
import redis
from api.src.main import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_rate_limit():
    # Clear Redis before each test to avoid state leakage
    r = redis.Redis(host="redis", port=6379, decode_responses=True)
    r.flushdb()
