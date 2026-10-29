
MAX_ANSWER_CHARS = 1200
MAX_LATENCY_S = 15                                                

def is_concise(answer: str) -> bool:
    return len(answer) <= MAX_ANSWER_CHARS
        
def is_latency_within_limits(latency: float) -> bool:
    return latency <= MAX_LATENCY_S