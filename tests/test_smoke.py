from target_agent.retrieval import retrieve

def test_retrieve_finds_password_article() -> None:
    articles = retrieve('how do I reset my password?')
    assert len(articles) == 1
    assert '30 minutes' in articles[0]


def test_vocabulary_mismatch() -> None:
    """This tests the vocabulary mismatch."""
    articles = retrieve('can I get my money back?')
    assert len(articles) == 0


def test_refund_article() -> None:
    articles = retrieve('how do I get refund?')
    assert 'Billing' in articles[0]