import re

MAX_ANSWER_CHARS = 1200
MAX_LATENCY_S = 15
# Ends on a letter/digit, so a sentence-ending period isn't captured as part of the email.
EMAIL_PATTERN = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
# Contacts the system prompt tells the bot to use, so they're allowed even when no article mentions them.
KNOWN_CONTACTS = {"support@acmecloud.com"}


def is_concise(answer: str) -> bool:
    return len(answer) <= MAX_ANSWER_CHARS


def is_latency_within_limits(latency: float) -> bool:
    return latency <= MAX_LATENCY_S


def has_no_invented_contact(answer: str, retrieval_context: list[str]) -> bool:
    context = " ".join(retrieval_context)
    for email in re.findall(EMAIL_PATTERN, answer):
        if email not in context and email not in KNOWN_CONTACTS:
            return False
    return True
