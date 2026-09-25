from app.services.llm import narrate


def test_narrate_returns_none_without_credentials(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    assert narrate({"recommendation": "slow"}) is None
