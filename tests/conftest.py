import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from app import config
    from app.seed import seed

    db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", db)
    seed(db)
    from app.main import app

    return TestClient(app)
