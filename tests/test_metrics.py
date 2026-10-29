from evals.metrics import is_concise
from evals.metrics import MAX_ANSWER_CHARS

def test_correct_char_limit() -> None:
    assert is_concise("a" * MAX_ANSWER_CHARS)


def test_char_limit_exceeded() -> None:
    assert not is_concise("a" * MAX_ANSWER_CHARS + 'a')