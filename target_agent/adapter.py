import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from target_agent.retrieval import retrieve

load_dotenv()

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
    max_retries=5,
)
MODEL = os.environ["LLM_MODEL"]

SYSTEM_PROMPT = """You are Acme Cloud's customer support assistant.
Answer the customer's question using ONLY the help-center articles provided.
If the articles do not contain the answer, say you don't know and suggest contacting support@acmecloud.com.
Never invent policies, numbers, prices, or contact details.
Keep answers short: at most 5 sentences."""

FALLBACK_ANSWER = (
    "I couldn't find that in our help center. "
    "Please contact support@acmecloud.com and our team will help you."
)

def run_agent(prompt: str) -> dict:
    """Answer a customer question from the help-center corpus (SPEC §4 adapter contract)."""
    start = time.perf_counter()

    articles = retrieve(prompt)
    if not articles:
        return {
            "answer": FALLBACK_ANSWER,
            "retrieval_context": [],
            "latency_s": time.perf_counter() - start,
        }

    context = "\n\n---\n\n".join(articles)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Help-center articles:\n\n{context}\n\nCustomer question: {prompt}"},
        ],
    )

    return {
         "answer": response.choices[0].message.content,
        "retrieval_context": articles,
        "latency_s": time.perf_counter() - start,
    }