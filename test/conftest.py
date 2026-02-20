import pytest
import sys, os

# Ensure /app is on sys.path so 'api' package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.src.main import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client
