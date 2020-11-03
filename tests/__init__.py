from fastapi.testclient import TestClient
from api.app.server import app
client = TestClient(app)