import json
import time
from datetime import datetime
from pathlib import Path

from openai import APIError

from evals.judge import JUDGE_MODEL, judge_faithfulness
from evals.metrics import has_no_invented_contact, is_concise, is_latency_within_limits
from target_agent.adapter import MODEL, run_agent

DATASET_FILE = Path(__file__).parent / "datasets" / "golden_dataset.json"
RESULTS_DIR = Path(__file__).parent.parent / "results"
# Free tier allows ~5 requests per minute per model; this keeps each model under that.
SECONDS_BETWEEN_CASES = 24
# SPEC D4: start at 0.7, then set for real via judge calibration.
FAITHFULNESS_THRESHOLD = 0.7
CHECKS = ["concise", "latency_ok", "no_invented_contact", "faithful"]


def load_dataset() -> list[dict]:
    with open(DATASET_FILE, "r", encoding="utf-8") as infile:
        data = json.load(infile)
    return data


def evaluate_case(case: dict) -> dict:
    """Run one golden case through the bot, then score the answer."""
    result = run_agent(case["input"])
    judge = judge_faithfulness(result["answer"], result["retrieval_context"])
    checks = {
        "concise": is_concise(result["answer"]),
        "latency_ok": is_latency_within_limits(result["latency_s"]),
        "no_invented_contact": has_no_invented_contact(result["answer"], result["retrieval_context"]),
        "faithful": judge["score"] >= FAITHFULNESS_THRESHOLD,
    }
    return {
        "id": case["id"],
        "category": case["category"],
        "answer": result["answer"],
        "latency_s": round(result["latency_s"], 2),
        "faithfulness": judge["score"],
        "judge_reason": judge["reason"],
        "checks": checks,
        "passed": all(checks.values()),
    }


def summarize(results: list[dict]) -> dict:
    """Quality numbers come only from scored cases; infrastructure errors are counted separately."""
    scored = [r for r in results if "error" not in r]
    errors = [r for r in results if "error" in r]
    if not scored:
        return {"scored": 0, "errors": len(errors)}
    summary = {
        "scored": len(scored),
        "errors": len(errors),
        "mean_faithfulness": round(sum(r["faithfulness"] for r in scored) / len(scored), 3),
        "pass_rate": round(sum(r["passed"] for r in scored) / len(scored), 3),
    }
    for check in CHECKS:
        summary[f"{check}_rate"] = round(sum(r["checks"][check] for r in scored) / len(scored), 3)
    return summary


def main() -> None:
    cases = load_dataset()
    results = []
    for number, case in enumerate(cases, start=1):
        try:
            outcome = evaluate_case(case)
            status = "PASS" if outcome["passed"] else "FAIL"
            print(f"[{number}/{len(cases)}] {status}  {case['id']}  faithfulness={outcome['faithfulness']}")
        except (APIError, json.JSONDecodeError, KeyError) as error:
            # An API outage or a malformed judge reply says nothing about the bot's quality.
            outcome = {"id": case["id"], "category": case["category"], "error": f"{type(error).__name__}: {error}"[:300]}
            print(f"[{number}/{len(cases)}] ERROR {case['id']}  {outcome['error'][:120]}")
        results.append(outcome)
        if number < len(cases):
            time.sleep(SECONDS_BETWEEN_CASES)

    summary = summarize(results)
    run = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "bot_model": MODEL,
        "judge_model": JUDGE_MODEL,
        "faithfulness_threshold": FAITHFULNESS_THRESHOLD,
        "summary": summary,
        "results": results,
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    out_file = RESULTS_DIR / f"run-{datetime.now():%Y%m%d-%H%M%S}.json"
    out_file.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nSummary:", json.dumps(summary, indent=2))
    print("Saved:", out_file)


if __name__ == "__main__":
    main()
