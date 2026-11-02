# Experiment log

One variable per experiment. Every run is logged the same day with date, change, metric, before, after, delta and notes. "It looked better" is not a result; a delta is.

## Summary

| # | Date | Change | Mean faithfulness | Pass rate | Δ pass rate | Notes |
|---|---|---|---|---|---|---|
| 1 | 2026-11-02 | Baseline, no change | 1.000 | 15/15 (100%) | n/a | Metrics are saturated; money-back-001 fails for real but every metric passes it |

---

## #1: Baseline (2026-11-02)

**Change:** none. This is the reference point every later experiment is compared against.

**Setup**

| | |
|---|---|
| Bot model | `gemini-3.5-flash-lite` |
| Judge model | `gemini-3-flash-preview` (a different model from the bot, to avoid self-preference bias) |
| Retrieval | keyword, stopwords + term-frequency ranking, top k = 2 |
| Dataset | 15 golden cases: 7 ungrounded_claims, 4 refusal, 4 topic_drift |
| Faithfulness threshold | 0.7 (SPEC D4 starting value, not calibrated yet) |
| Raw results | [results/run-20261102-145504.json](../results/run-20261102-145504.json) |

**Results**

| Metric | Result |
|---|---|
| Mean faithfulness | 1.000 |
| Faithful (≥ 0.7) | 15/15 |
| No invented contact | 15/15 |
| Concise (≤ 1200 chars) | 15/15 (longest answer: 432 chars) |
| Latency (≤ 15 s) | 15/15 (mean 0.70 s, max 0.98 s) |
| **Pass rate (all checks)** | **15/15** |
| Infrastructure errors | 0 |

**By category:** every case in all 3 categories passed. All 4 refusal cases said "I don't know" and pointed to support, with no invented phone number, app or discount. All 4 topic-drift traps were answered with the right fact (deactivated right away, 7 days, owners and admins, refund + delete).

**Notes and findings**

1. **The suite can't see a known failure.** money-back-001 ("How can I get money back?") got the fallback answer. Keyword retrieval found no article, because none contains "money" or "back" (vocabulary mismatch), so the customer never got the refund policy that exists in the corpus. The judge correctly scored the answer 1.0: it is *faithful*, since it invents nothing. But it is not *correct*. **Faithfulness measures honesty, not helpfulness.** No current metric compares the answer to `expected_output`, so a real failure shows up as a pass.
2. **The metrics are saturated (ceiling effect).** With every metric at 100%, an improvement can't show a positive delta. Only regressions are visible. Before running retrieval experiments, the suite needs a metric that can fail on this baseline.
3. **The judge isn't calibrated.** 15 scores of 1.0 might be correct, or the judge might be too lenient. This can't be known until the cases are hand-graded and agreement is measured (SPEC §9 target: ≥ 90%).
4. **Harness reliability (infrastructure, not quality).** Getting this run took three tries:
   - `gemini-3.8-flash` accepted requests but never answered, and with no client timeout and 5 retries one request could hang for about 10 minutes. Fix: `timeout=60` on the client.
   - Firing calls back to back hit the free tier's per-minute limit. Fix: 24 s pacing between cases.
   - Debugging used up one model's **20 requests per day**, and a full run needs 29 calls. Fix: separate bot and judge models, each with its own daily quota. This also removed the self-preference bias.
   - The runner now records API errors separately and leaves them out of the quality numbers.
5. **The bot model changed while this run was being prepared** (from `gemini-3.8-flash` to `gemini-3.5-flash-lite`) because of the quota and outage problems. This run is the baseline *for this model*. Changing the model later counts as its own experiment.

**Next experiments (one variable each)**

1. Add an **answer-correctness** metric (judge compares the answer to `expected_output`) and re-baseline. Expected result: money-back-001 fails.
2. Retrieval: BM25 or embeddings to fix vocabulary mismatch. Target: money-back-001 passes, nothing else regresses.
3. Retrieval `k` 2 → 3.
4. Judge calibration: hand-grade 20+ answers, measure agreement, then adjust the rubric or threshold.
