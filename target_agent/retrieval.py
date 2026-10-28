import re 
from pathlib import Path

CORPUS_DIR = Path(__file__).parent / "corpus"

STOPWORDS = {
    "a", "an", "the", "i", "my", "me", "you", "your", "is", "are", "do", "does", 
    "how", "what", "when", "can", "to", "of", "in", "on", "for", "and", "or", "it", 
}

def tokenize(text: str) -> list[str]:
    """Lowercase, split into words, drop stopwords"""

    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def load_corpus() -> dict[str, str]:
    """Read {filename: article text} for every .md file in the corpus"""
    return {path.name: path.read_text() for path in sorted(CORPUS_DIR.glob("*.md"))}


def retrieve(question: str, k: int = 2) -> list[str]:
    """Return the k articles where the question's words appear most often."""
    question_words = set(tokenize(question))
    scored = []
    for name, text in load_corpus().items():
        article_words = tokenize(text)
        score = 0
        for word in question_words:
            score += article_words.count(word)
        if score > 0:
            scored.append((score, name, text))
    scored.sort(reverse=True)
    return [text for score, name, text in scored[:k]]
