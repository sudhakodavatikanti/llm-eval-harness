
MAX_ANSWER_CHARS = 1200

def is_concise(answer: str) -> bool:
    return len(answer) <= MAX_ANSWER_CHARS
        
