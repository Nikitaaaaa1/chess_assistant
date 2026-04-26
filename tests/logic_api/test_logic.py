import sys
import os
import importlib.util
from fastapi.testclient import TestClient

# Define the path to main.py
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chess-logic-api'))
main_path = os.path.join(service_dir, 'main.py')

# Import main.py as a module named 'logic_main'
spec = importlib.util.spec_from_file_location("logic_main", main_path)
logic_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logic_main)

client = TestClient(logic_main.app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Chess Logic API is running", "status": "ok"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_cors_headers():
    # Test that CORS headers are present when an Origin is provided
    origin = "http://localhost:3000"
    headers = {"Origin": origin}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
