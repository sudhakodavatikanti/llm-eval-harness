from target_agent.adapter import client, FALLBACK_ANSWER, run_agent


def test_fallback(monkeypatch) -> None:
    def fake_create(**kwargs):
        raise AssertionError("LLM should not be called for fallback")

    monkeypatch.setattr(client.chat.completions, "create", fake_create)
    
    response = run_agent('how can I get money?')
    assert response['answer'] == FALLBACK_ANSWER
    assert response['retrieval_context'] == []