from evals.metrics import (
    MAX_ANSWER_CHARS,
    MAX_LATENCY_S,
    has_no_invented_contact,
    is_concise,
    is_latency_within_limits,
)

REFUND_CONTEXT = ["To request a refund, email billing@acmecloud.com from the account owner's email address."]


def test_correct_char_limit() -> None:
    assert is_concise("a" * MAX_ANSWER_CHARS)


def test_char_limit_exceeded() -> None:
    assert not is_concise("a" * MAX_ANSWER_CHARS + 'a')


def test_valid_latency_limit() -> None:
    assert is_latency_within_limits(MAX_LATENCY_S)


def test_excess_latency() -> None:
    assert not is_latency_within_limits(MAX_LATENCY_S + 0.01)


def test_email_is_not_invented() -> None:
    assert has_no_invented_contact('To request a refund, email billing@acmecloud.com', REFUND_CONTEXT)


def test_email_is_invented() -> None:
    assert not has_no_invented_contact('To request a refund, email refunds@acmecloud.io', REFUND_CONTEXT)


def test_email_at_end_of_sentence_is_not_invented() -> None:
    assert has_no_invented_contact('To request a refund, email billing@acmecloud.com.', REFUND_CONTEXT)


def test_support_email_is_allowed_without_context() -> None:
    assert has_no_invented_contact("I couldn't find that. Please contact support@acmecloud.com.", [])
