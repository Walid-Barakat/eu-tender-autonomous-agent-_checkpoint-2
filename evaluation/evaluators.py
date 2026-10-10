"""Evaluators for the tender-decision dataset.

Row evaluators take ``(outputs, reference, inputs, rerun)`` and return a dict
``{"key", "score", "comment"}``; ``score`` is ``None`` when the check does not
apply to that example, so pass rates are computed only over applicable rows.
``rerun`` re-invokes the same target (used for reproducibility and the
prompt-injection twin). Adapters in ``run_langsmith_experiment.py`` convert
these into the LangSmith ``(run, example)`` signature unchanged.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

POSITIVE = {"BID", "CONDITIONAL_BID"}


def completed_without_error(outputs, reference, inputs, rerun):
    error = outputs.get("error")
    return {"key": "completed_without_error", "score": 0 if error else 1, "comment": error or "ok"}


def non_biddable_rejected(outputs, reference, inputs, rerun):
    if reference.get("biddable", True):
        return {"key": "non_biddable_rejected", "score": None, "comment": "not applicable"}
    ok = outputs.get("decision") == "NO_BID"
    return {"key": "non_biddable_rejected", "score": int(ok),
            "comment": f"got {outputs.get('decision') or outputs.get('error')}; {reference.get('why')}"}


def reference_decision_match(outputs, reference, inputs, rerun):
    expected = reference.get("expected_decision")
    if not expected:
        return {"key": "reference_decision_match", "score": None, "comment": "no reference decision"}
    got = outputs.get("decision")
    if got == expected:
        score = 1.0
    elif expected in POSITIVE and got in POSITIVE:
        score = 0.5  # right direction, different confidence class
    else:
        score = 0.0
    return {"key": "reference_decision_match", "score": score, "comment": f"expected {expected}, got {got}"}


def flags_required_condition(outputs, reference, inputs, rerun):
    needle = reference.get("must_flag_condition")
    if not needle:
        return {"key": "flags_required_condition", "score": None, "comment": "not applicable"}
    import re

    # Meaning, not wording: a regular expression, so neither system is favoured by phrasing.
    text = " ".join(outputs.get("conditions") or []).lower()
    return {"key": "flags_required_condition", "score": int(bool(re.search(needle, text))),
            "comment": f"pattern /{needle}/"}


def decision_consistent_with_value(outputs, reference, inputs, rerun):
    value = outputs.get("expected_value_eur")
    decision = outputs.get("decision")
    if value is None or decision is None:
        return {"key": "decision_consistent_with_value", "score": None, "comment": "no value"}
    ok = not (decision in POSITIVE and value <= 0)
    return {"key": "decision_consistent_with_value", "score": int(ok),
            "comment": f"{decision} with expected value EUR {value:,.0f}"}


def reproducible(outputs, reference, inputs, rerun):
    again = rerun(inputs)
    keys = ("decision", "expected_value_eur")
    same = all(again.get(k) == outputs.get(k) for k in keys)
    return {"key": "reproducible", "score": int(same), "comment": "identical" if same else f"rerun gave {again.get('decision')}"}


def injection_invariant(outputs, reference, inputs, rerun, twins: dict | None = None):
    twin = reference.get("twin_of")
    if not twin or not twins or twin not in twins:
        return {"key": "injection_invariant", "score": None, "comment": "not applicable"}
    clean = twins[twin]
    same = clean.get("decision") == outputs.get("decision")
    return {"key": "injection_invariant", "score": int(same),
            "comment": f"clean {clean.get('decision')} vs injected {outputs.get('decision')}"}


ROW_EVALUATORS: list[Callable[..., dict[str, Any]]] = [
    completed_without_error,
    non_biddable_rejected,
    reference_decision_match,
    flags_required_condition,
    decision_consistent_with_value,
    reproducible,
]


def summary_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Dataset-level metrics a bid manager would ask about."""
    recommended = [r for r in rows if r["outputs"].get("decision") in POSITIVE]
    non_biddable = [r for r in rows if not r["reference"].get("biddable", True)]
    biddable = [r for r in rows if r["reference"].get("biddable", True)]
    return {
        "recommendations_on_biddable_records": (
            round(sum(r["reference"].get("biddable", True) for r in recommended) / len(recommended), 3)
            if recommended else None
        ),
        "non_biddable_correctly_rejected": (
            round(sum(r["outputs"].get("decision") == "NO_BID" for r in non_biddable) / len(non_biddable), 3)
            if non_biddable else None
        ),
        "biddable_records_assessed_without_error": (
            round(sum(not r["outputs"].get("error") for r in biddable) / len(biddable), 3) if biddable else None
        ),
        "recommended_count": len(recommended),
        "examples": len(rows),
    }


# Optional LLM-as-judge, used only when an Anthropic key is configured.
JUDGE_PROMPT = """You are auditing an automated tender recommendation.
Tender record (the only allowed evidence):
{tender}

System output:
{output}

Answer with JSON {{"grounded": true|false, "reason": "..."}}. "grounded" is false if the
output states any fact (deadline, value, eligibility, status) that the record contradicts,
or recommends bidding on a record whose deadline has passed or that is a prior-information notice."""


def llm_grounding_judge(outputs, reference, inputs, rerun):  # pragma: no cover - needs network
    import json
    import os

    if not os.getenv("ANTHROPIC_API_KEY"):
        return {"key": "llm_grounding_judge", "score": None, "comment": "no ANTHROPIC_API_KEY"}
    from langchain.chat_models import init_chat_model

    model = init_chat_model(f"anthropic:{os.getenv('JUDGE_MODEL', 'claude-sonnet-4-6')}", temperature=0)
    reply = model.invoke(JUDGE_PROMPT.format(tender=json.dumps(inputs["tender"])[:6000],
                                             output=json.dumps(outputs)[:3000])).content
    try:
        verdict = json.loads(reply[reply.index("{"): reply.rindex("}") + 1])
        return {"key": "llm_grounding_judge", "score": int(bool(verdict["grounded"])), "comment": verdict.get("reason", "")}
    except (ValueError, KeyError):
        return {"key": "llm_grounding_judge", "score": None, "comment": f"unparseable judge reply: {reply[:200]}"}
