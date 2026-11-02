import os

# Dummy config so target_agent.adapter can be imported without a real .env (e.g. in CI).
# setdefault keeps any value that's already set. load_dotenv() never overrides these,
# so unit tests can never reach the real API with a real key.
os.environ.setdefault("GEMINI_API_KEY", "test-key-not-real")
os.environ.setdefault("LLM_BASE_URL", "http://localhost/not-a-real-llm")
os.environ.setdefault("LLM_MODEL", "fake-model")
os.environ.setdefault("JUDGE_MODEL", "fake-judge-model")
