from target_agent.adapter import client, FALLBACK_ANSWER, run_agent
from types import SimpleNamespace 


def test_fallback(monkeypatch) -> None:
    def fake_create(**kwargs):
        raise AssertionError("LLM should not be called for fallback")

    monkeypatch.setattr(client.chat.completions, "create", fake_create)
    
    response = run_agent('how can I get money?')
    assert response['answer'] == FALLBACK_ANSWER
    assert response['retrieval_context'] == []



def test_run_agent_contract(monkeypatch) -> None:
    def fake_create(**kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Hello from fake Gemini"))])         

    monkeypatch.setattr(client.chat.completions, "create", fake_create)    

    response = run_agent('How do I reset my password?')

    assert set(response) == {"answer", "retrieval_context", "latency_s"}                  
    assert response['answer'] == 'Hello from fake Gemini'
