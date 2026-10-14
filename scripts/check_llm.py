import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # read .env and put its lines into environment variables

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],   # your secret key, read from the environment
    base_url=os.environ["LLM_BASE_URL"],    # Google's OpenAI-compatible "door"
)

start = time.perf_counter()
response = client.chat.completions.create(
    model=os.environ["LLM_MODEL"],
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Answer in one sentence."},
        {"role": "user", "content": "What is retrieval-augmented generation?"},
    ],
)
latency_s = time.perf_counter() - start

print("Answer :", response.choices[0].message.content)
print("Latency:", round(latency_s, 2), "s")
print("Tokens :", response.usage.total_tokens)
