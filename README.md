# llm-eval-harness

An evaluation harness for a RAG customer-support bot. It answers one question: **is the bot good, in numbers, and did my last change make it better or worse?**

Anyone can wire up an LLM call. The hard part is knowing whether a prompt, retrieval or model change helped or quietly broke something. This harness runs a golden dataset of hard questions through the bot, scores every answer with deterministic checks and an LLM judge, and saves the results so every change can be compared against a baseline.

## The bot under test

"Acme Cloud" support bot (made-up company, clean-room data):

- **Corpus:** 4 help-center articles in [target_agent/corpus/](target_agent/corpus/) (password reset, data export, billing and refunds, account deletion). Each one has planted traps, such as two different "30 days" facts.
- **Retrieval:** keyword retrieval with stopword removal and term-frequency ranking, top 2 articles ([target_agent/retrieval.py](target_agent/retrieval.py)).
- **Generation:** Gemini through the `openai` SDK and Gemini's OpenAI-compatible endpoint. The system prompt says to answer only from the articles and never invent policies or contacts.
- **Fallback:** if retrieval finds nothing, the bot returns a fixed "contact support" answer **without calling the LLM**.

The harness only talks to the bot through one adapter function (`target_agent/adapter.py`):

```python
run_agent(prompt: str) -> {"answer": str, "retrieval_context": list[str], "latency_s": float}
```

To evaluate a different bot, replace that one function. The evals don't change.

## What gets measured, and why

| Metric | Type | Catches | Pass rule |
|---|---|---|---|
| Faithfulness | LLM judge | Hallucinations: claims the retrieved articles don't support | score ≥ 0.7 (starting value, to be set by calibration) |
| No invented contact | Deterministic (regex + allow-list) | Made-up support emails | every email is in the articles or the known support address |
| Conciseness | Deterministic | Walls of text | ≤ 1200 characters |
| Latency | Deterministic | Slow answers (SLO breach) | ≤ 15 s |

**Rule:** if something can be checked objectively, it's checked in code. Only judgment calls go to the LLM judge. A regex never flakes and never costs anything.

**The judge uses a different model from the bot.** If a model grades its own answers, it tends to favor them (self-preference bias).

### Golden dataset

15 cases in [evals/datasets/golden_dataset.json](evals/datasets/golden_dataset.json), each mapped to a failure mode:

| Category | Cases | What it tests |
|---|---|---|
| `ungrounded_claims` | 7 | Exact facts and numbers, and "no" answers (PDF export? PayPal?) where people-pleasing bots say yes |
| `refusal` | 4 | Questions the articles can't answer (phone number, iPhone app, discounts). The bot must say it doesn't know, not invent an answer. |
| `topic_drift` | 4 | Articles containing a tempting wrong number, e.g. "7 days" link validity vs "15 minutes" preparation time |

Each case records the **correct** answer, never just whatever the bot currently says.

## Baseline results

Run on 2026-11-02. Bot `gemini-3.5-flash-lite`, judge `gemini-3-flash-preview`, 15 cases, 0 infrastructure errors.

| Metric | Result |
|---|---|
| Mean faithfulness | 1.00 |
| No invented contact | 15/15 |
| Concise | 15/15 |
| Latency ≤ 15 s | 15/15 (mean 0.7 s) |
| **All checks passed** | **15/15** |

**What the 100% hides.** `money-back-001` ("How can I get money back?") actually fails: keyword retrieval doesn't connect "money back" to the refund article, so the bot says it can't help. Every metric still passes it. The answer is *faithful* (it invents nothing) but not *correct*. The baseline shows the suite needs an answer-correctness metric before retrieval experiments can show a delta. It's the first planned experiment in the log.

Full experiment history: [docs/EXPERIMENT_LOG.md](docs/EXPERIMENT_LOG.md).

## Quickstart

Requires Python 3.11+ and a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/sudhakodavatikanti/llm-eval-harness.git
cd llm-eval-harness
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then put your real key in .env (never commit it)
```

Run the unit tests. They make no API calls and need no key:

```bash
python -m pytest -v
```

Ask the bot one question:

```bash
python -c "from target_agent.adapter import run_agent; print(run_agent('How long is the password reset link valid?'))"
```

Run the full evaluation (about 7 minutes, 29 API calls):

```bash
python -m evals.run_evals
```

Results are saved to `results/run-<timestamp>.json`, with every answer, score and judge reason, plus a summary.

### Free-tier limits

On Gemini's free tier, each model allows only about 5 requests per minute and **20 per day**. The harness is designed around this:

- The bot and the judge use **different models**, so each stays under 20 calls per run.
- The runner waits 24 s between cases (the per-minute limit).
- API errors (429, 503, timeouts) are recorded as `errors` and **left out of the quality numbers**. An outage is an infrastructure failure, not a quality failure.

## Project layout

```
target_agent/   the bot under test: adapter (run_agent), retrieval, corpus
evals/          metrics.py, judge.py, run_evals.py, datasets/golden_dataset.json
tests/          unit tests for retrieval, the adapter (LLM mocked) and metrics
results/        saved eval runs (JSON)
docs/           EXPERIMENT_LOG.md
```

## Known limitations and roadmap

- **Keyword retrieval misses synonyms.** "money back" never matches the refund article. Next experiment: BM25 or embeddings.
- **Faithfulness isn't correctness.** An honest "I don't know" scores 1.0 even when the answer exists in the articles. Planned: an answer-correctness metric against `expected_output`, and answer relevancy.
- **The judge isn't calibrated yet.** Planned: hand-grade 20+ cases and target ≥ 90% agreement before the 0.7 threshold is trusted.
- **Phone numbers aren't detected** by the invented-contact check yet.
- **Next:** a FastAPI `POST /ask` service with API contract tests, a CI gate that fails PRs on quality regressions, Docker, and growing the dataset to 60 cases.
