"""Run the Checkpoint 2 evaluation in LangSmith (or locally with --offline).

LangSmith mode (needs LANGSMITH_API_KEY, and LANGSMITH_TRACING=true for traces):

    PYTHONPATH=src:. python evaluation/run_langsmith_experiment.py

creates or updates the dataset ``eu-tender-decisions-v2``, then runs two
experiments over it, one per system under test, each with the same row and
summary evaluators. Every target call is a traced run, so the per-example
traces appear under each experiment.

Offline mode runs the identical targets and evaluators without a network and
writes ``evaluation/results/offline_experiment.json`` plus a Markdown table:

    PYTHONPATH=src:. python evaluation/run_langsmith_experiment.py --offline
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from evaluation.evaluators import (
    ROW_EVALUATORS,
    injection_invariant,
    llm_grounding_judge,
    summary_metrics,
)
from evaluation.targets import TARGETS

ROOT = Path(__file__).resolve().parents[1]
DATASET_FILE = ROOT / "evaluation" / "dataset" / "eu_tender_decisions_v2.jsonl"
DATASET_NAME = "eu-tender-decisions-v2"
RESULTS = ROOT / "evaluation" / "results"


def load_examples() -> list[dict]:
    return [json.loads(line) for line in DATASET_FILE.read_text(encoding="utf-8").splitlines() if line]


# ------------------------------------------------------------------ offline


def run_offline() -> dict:
    examples = load_examples()
    report: dict = {"dataset": DATASET_NAME, "examples": len(examples),
                    "executed_at": datetime.now(UTC).isoformat(), "experiments": {}}
    for name, target in TARGETS.items():
        outputs = {e["id"]: target(e["inputs"]) for e in examples}
        rows = []
        for example in examples:
            out = outputs[example["id"]]
            scores = [ev(out, example["reference"], example["inputs"], target) for ev in ROW_EVALUATORS]
            scores.append(injection_invariant(out, example["reference"], example["inputs"], target, outputs))
            rows.append({"id": example["id"], "split": example["split"], "outputs": out,
                         "reference": example["reference"], "scores": scores})
        keys = sorted({s["key"] for r in rows for s in r["scores"]})
        aggregate = {}
        for key in keys:
            applicable = [s["score"] for r in rows for s in r["scores"] if s["key"] == key and s["score"] is not None]
            aggregate[key] = {"mean": round(sum(applicable) / len(applicable), 3) if applicable else None,
                              "n": len(applicable)}
        report["experiments"][name] = {"row_metrics": aggregate, "summary": summary_metrics(rows), "rows": rows}
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "offline_experiment.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    (RESULTS / "offline_experiment.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _markdown(report: dict) -> str:
    names = list(report["experiments"])
    keys = sorted({k for n in names for k in report["experiments"][n]["row_metrics"]})
    lines = [f"# Offline experiment, {report['executed_at'][:19]}Z, {report['examples']} examples", "",
             "| Evaluator | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for key in keys:
        cells = []
        for n in names:
            m = report["experiments"][n]["row_metrics"].get(key, {})
            cells.append("n/a" if m.get("mean") is None else f"{m['mean']:.2f} (n={m['n']})")
        lines.append(f"| {key} | " + " | ".join(cells) + " |")
    lines += ["", "| Summary metric | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for key in report["experiments"][names[0]]["summary"]:
        lines.append(f"| {key} | " + " | ".join(str(report["experiments"][n]["summary"][key]) for n in names) + " |")
    lines += ["", "## Per-example decisions", "", "| Example | Reference | " + " | ".join(names) + " |",
              "|---|---|" + "---|" * len(names)]
    rows = {n: {r["id"]: r for r in report["experiments"][n]["rows"]} for n in names}
    for rid in rows[names[0]]:
        ref = rows[names[0]][rid]["reference"]
        label = ref.get("expected_decision") or ("biddable" if ref.get("biddable") else "not biddable")
        cells = []
        for n in names:
            out = rows[n][rid]["outputs"]
            cells.append(out.get("decision") or f"ERROR: {str(out.get('error'))[:40]}")
        lines.append(f"| {rid} | {label} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- langsmith


def run_langsmith(include_judge: bool) -> None:
    from langsmith import Client, evaluate

    client = Client()
    examples = load_examples()
    if client.has_dataset(dataset_name=DATASET_NAME):
        dataset = client.read_dataset(dataset_name=DATASET_NAME)
    else:
        dataset = client.create_dataset(
            DATASET_NAME,
            description="Final use case: bid/no-bid decisions on EU energy tenders "
            "(14 real records from the 12 Aug 2026 run, 3 Checkpoint 1 fixtures, 6 edge cases).",
        )
        client.create_examples(
            dataset_id=dataset.id,
            examples=[{"inputs": e["inputs"], "outputs": e["reference"],
                       "metadata": {"id": e["id"], "split": e["split"]}} for e in examples],
        )

    def adapt(fn):
        def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
            result = fn(outputs, reference_outputs, inputs, TARGETS[outputs.get("system", "checkpoint2")])
            return {"key": result["key"], "score": result["score"], "comment": result["comment"]}
        evaluator.__name__ = fn.__name__
        return evaluator

    evaluators = [adapt(fn) for fn in ROW_EVALUATORS]
    if include_judge:
        evaluators.append(adapt(llm_grounding_judge))

    def summary(inputs: list, outputs: list, reference_outputs: list) -> list[dict]:
        rows = [{"outputs": o, "reference": r} for o, r in zip(outputs, reference_outputs)]
        return [{"key": k, "score": v} for k, v in summary_metrics(rows).items() if isinstance(v, (int, float))]

    for name, target in TARGETS.items():
        evaluate(
            target,
            data=DATASET_NAME,
            evaluators=evaluators,
            summary_evaluators=[summary],
            experiment_prefix=f"{name}-",
            metadata={"system": name, "engine": "cp2-decision-engine/1.0.0" if name == "checkpoint2" else "cp1"},
            max_concurrency=4,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--judge", action="store_true", help="Add the LLM grounding judge (needs ANTHROPIC_API_KEY)")
    args = parser.parse_args()
    if args.offline or not os.getenv("LANGSMITH_API_KEY"):
        if not args.offline:
            print("LANGSMITH_API_KEY not set: running offline instead.")
        result = run_offline()
        for name, exp in result["experiments"].items():
            print(name, json.dumps(exp["row_metrics"]), json.dumps(exp["summary"]))
    else:
        run_langsmith(args.judge)
