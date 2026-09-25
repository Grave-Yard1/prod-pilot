from fastapi.testclient import TestClient
import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'linewalk.db'}")
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
