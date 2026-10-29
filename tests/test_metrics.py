from evals.metrics import is_concise, MAX_ANSWER_CHARS, MAX_LATENCY_S, is_latency_within_limits


def test_correct_char_limit() -> None:
    assert is_concise("a" * MAX_ANSWER_CHARS)


def test_char_limit_exceeded() -> None:
    assert not is_concise("a" * MAX_ANSWER_CHARS + 'a')

def test_valid_latency_limit() -> None:
    assert is_latency_within_limits(MAX_LATENCY_S)

def test_excess_latency() -> None:
    assert not is_latency_within_limits(MAX_LATENCY_S + 2.3)