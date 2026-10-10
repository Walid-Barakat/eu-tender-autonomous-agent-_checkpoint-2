"""The two systems under test, wrapped with the same input/output contract.

``checkpoint1_pipeline`` runs the unmodified Checkpoint 1 assessment code
(``offline_workflow.assess_tender``) with two controlled changes that make it
evaluable offline: the portal fetch returns nothing (the record already holds
the n8n Stage 2 payload), and the clock is frozen at the example's ``as_of``
date so deadline logic sees the same "today" the live run saw.

``checkpoint2_engine`` runs the Checkpoint 2 decision engine on the single
tender. Both return a flat dict so the same evaluators apply to both.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any
from unittest import mock

from tender_agent.decision_engine.engine import run_decision_engine
from tender_agent.decision_engine.gates import parse_deadline
from tender_agent.decision_engine.monte_carlo import CONSERVATIVE, SimulationConfig
from tender_agent.tools.core import load_company_profile

try:  # LangSmith tracing when the SDK and an API key are available; a no-op otherwise.
    from langsmith import traceable
except ImportError:  # pragma: no cover
    def traceable(*_args, **_kwargs):
        def wrap(fn):
            return fn
        return wrap


class _FrozenDatetime(_dt.datetime):
    frozen: _dt.datetime = _dt.datetime(2026, 8, 12, tzinfo=_dt.UTC)

    @classmethod
    def now(cls, tz=None):
        return cls.frozen if tz is None else cls.frozen.astimezone(tz)


@traceable(name="checkpoint1_pipeline", run_type="chain")
def checkpoint1_pipeline(inputs: dict[str, Any]) -> dict[str, Any]:
    from tender_agent import offline_workflow

    tender = dict(inputs["tender"])
    tender.setdefault(
        "stage2Assessment",
        {"relevanceScore": tender.get("relevanceScore"), "modelDecision": tender.get("modelDecision")},
    )
    as_of = parse_deadline(inputs["as_of"]) or _FrozenDatetime.frozen
    _FrozenDatetime.frozen = as_of
    try:
        with mock.patch.object(offline_workflow, "get_eu_tender_details", return_value={}), \
             mock.patch("datetime.datetime", _FrozenDatetime):
            report = offline_workflow.assess_tender(tender, inputs.get("company_id", "i@work"))
    except Exception as exc:  # noqa: BLE001 - a crash is an evaluated outcome, not a test error
        return {"system": "checkpoint1", "error": f"{type(exc).__name__}: {exc}", "decision": None}
    return {
        "system": "checkpoint1",
        "decision": report.decision,
        "overall_score": report.overall_score,
        "expected_value_eur": report.financial.expected_value_eur,
        "conditions": report.eligibility_gaps + report.risks,
        "summary": report.executive_summary,
        "error": None,
    }


@traceable(name="checkpoint2_engine", run_type="chain")
def checkpoint2_engine(inputs: dict[str, Any], config: SimulationConfig | None = None) -> dict[str, Any]:
    company = load_company_profile(inputs.get("company_id", "i@work"))
    try:
        result = run_decision_engine(
            [inputs["tender"]], company, inputs["as_of"], sim_config=config or SimulationConfig(n_scenarios=2000)
        )
        cautious = run_decision_engine(
            [inputs["tender"]], company, inputs["as_of"],
            sim_config=SimulationConfig(**{**CONSERVATIVE.as_dict(), "n_scenarios": 2000}),
        )
    except Exception as exc:  # noqa: BLE001
        return {"system": "checkpoint2", "error": f"{type(exc).__name__}: {exc}", "decision": None}
    decision = result["decisions"][0]
    return {
        "system": "checkpoint2",
        "decision": decision["decision"],
        "decision_conservative": cautious["decisions"][0]["decision"],
        "expected_value_eur": decision["expected_profit_eur"],
        "probability_of_loss": decision["probability_of_loss"],
        "conditions": decision["conditions"] + decision["gate"]["failures"],
        "summary": "; ".join(decision["reasons"]),
        "error": None,
    }


TARGETS = {"checkpoint1": checkpoint1_pipeline, "checkpoint2": checkpoint2_engine}
