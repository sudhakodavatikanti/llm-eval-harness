from target_agent.retrieval import retrieve

def test_retrieve_finds_password_article() -> None:
    articles = retrieve('how do I reset my password?')
    assert len(articles) == 1
    assert '30 minutes' in articles[0]