"""Checkpoint 2 decision-engine tests, run against the 14 real tenders of 12 Aug 2026."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from tender_agent.config import PROJECT_ROOT
from tender_agent.decision_engine.engine import run_decision_engine, serialisable
from tender_agent.decision_engine.gates import evaluate_gates, parse_deadline
from tender_agent.decision_engine.monte_carlo import CONSERVATIVE, SimulationConfig
from tender_agent.decision_engine.portfolio import PortfolioConfig
from tender_agent.decision_engine.proposal_outline import generate_outline
from tender_agent.tools.core import load_company_profile

LIVE_RUN = PROJECT_ROOT / "data" / "live_run_2026_08_12" / "stage2_advanced_tenders.json"
SMALL = SimulationConfig(n_scenarios=1500)


@pytest.fixture(scope="module")
def live_run() -> dict:
    return json.loads(LIVE_RUN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def company() -> dict:
    return load_company_profile("i@work")


@pytest.fixture(scope="module")
def result(live_run, company) -> dict:
    return run_decision_engine(live_run["tenders"], company, live_run["discovered_at"], SMALL)


# ---------------------------------------------------------------- gates


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-09-15T16:00:59.000+0000", datetime(2026, 9, 15, 16, 0, 59, tzinfo=UTC)),
        ("14/07/2026", datetime(2026, 7, 14, 23, 59, 59, tzinfo=UTC)),
        ("2026-11-20T17:00:00+01:00", datetime(2026, 11, 20, 16, 0, tzinfo=UTC)),
    ],
)
def test_parse_deadline_handles_real_payload_formats(raw, expected):
    assert parse_deadline(raw) == expected


def test_unparseable_deadline_fails_closed(company):
    gate = evaluate_gates(
        {"recordId": "x", "status": "Open", "deadline": "next Tuesday"},
        company,
        datetime(2026, 8, 12, tzinfo=UTC),
    )
    assert not gate.passed
    assert any("unparseable" in failure for failure in gate.failures)


def test_gates_reject_exactly_the_non_biddable_live_records(result):
    rejected = {d["identifier"] for d in result["decisions"] if not d["gate"]["passed"]}
    assert rejected == {
        "CINEA/2026/OP/0028-PIN",
        "CINEA/2026/OP/0015-PIN",
        "ACER/2026/MVP/0009-EXA",
        "ACER/2026/LVP/0002-EXA",
        "EC-ENEST/ANK/2025/EA-RP/0146",
        "ACER/2025/LVP/0055-EXA",
        "NEAR/ANK/2023/EA-RP/0104",
    }


def test_failed_gate_means_no_bid_and_no_spend(result):
    for decision in result["decisions"]:
        if not decision["gate"]["passed"]:
            assert decision["decision"] == "NO_BID"
            assert decision["expected_profit_eur"] == 0
            assert decision["bid_cost_median_eur"] == 0


# ---------------------------------------------------------- determinism


def test_engine_is_deterministic(live_run, company, result):
    again = run_decision_engine(live_run["tenders"], company, live_run["discovered_at"], SMALL)
    assert serialisable(again) == serialisable(result)


def test_per_tender_results_do_not_depend_on_order(live_run, company, result):
    reordered = list(reversed(live_run["tenders"]))
    other = run_decision_engine(reordered, company, live_run["discovered_at"], SMALL)
    first = {d["record_id"]: d["expected_profit_eur"] for d in result["decisions"]}
    second = {d["record_id"]: d["expected_profit_eur"] for d in other["decisions"]}
    assert first == second


def test_assessment_date_changes_gate_outcome(live_run, company):
    later = run_decision_engine(live_run["tenders"], company, "2026-10-01T00:00:00Z", SMALL)
    assert later["counts"]["gate_passed"] == 0  # every live deadline had passed by October


# ------------------------------------------------------------ portfolio


def test_portfolio_respects_every_constraint(result, company):
    portfolio = result["portfolio"]
    config = PortfolioConfig()
    assert portfolio["stats"]["planned_bid_cost_eur"] <= company["available_bid_budget_eur"] * config.cycle_budget_fraction
    assert portfolio["stats"]["overcommit_probability"] <= config.overcommit_probability_limit
    assert portfolio["method"] == "exact enumeration"
    selected = {d["record_id"] for d in result["decisions"] if d["portfolio_status"] == "SELECTED"}
    assert selected == set(portfolio["selected"])


def test_selected_portfolio_beats_every_single_bid(result):
    lam = result["portfolio"]["risk_aversion"]
    for decision in result["decisions"]:
        if decision["portfolio_status"] == "EXCLUDED":
            continue
        single = decision["expected_profit_eur"] - lam * max(0.0, -decision["cvar_05_eur"])
        assert result["portfolio"]["objective_eur"] >= single - 1e-6


def test_conservative_profile_is_never_more_optimistic(live_run, company, result):
    cautious = run_decision_engine(live_run["tenders"], company, live_run["discovered_at"], SimulationConfig(n_scenarios=1500, win_probability_multiplier=0.5, cost_ratio_mode_override=0.82))
    base = {d["record_id"]: d["expected_profit_eur"] for d in result["decisions"]}
    for decision in cautious["decisions"]:
        assert decision["expected_profit_eur"] <= base[decision["record_id"]] + 1e-6
    assert CONSERVATIVE.profile_name == "conservative-uncalibrated"


# ------------------------------------------------------ proposal outline


def test_outline_refuses_no_bid_and_builds_bid_outline(live_run, company, result):
    by_id = {t["recordId"]: t for t in live_run["tenders"]}
    for decision in result["decisions"]:
        outline = generate_outline(by_id[decision["record_id"]], decision, company)
        if decision["decision"] == "NO_BID":
            assert outline["generated"] is False
        else:
            assert outline["generated"] is True
            assert outline["work_packages"][0]["id"] == "WP0"
            assert outline["evidence_requiring_human_confirmation"]
            assert outline["status"].startswith("DRAFT")


# ------------------------------------------------------------------ API


def test_api_rejects_invalid_assessment_date(live_run):
    from fastapi.testclient import TestClient

    from tender_agent.api import app

    client = TestClient(app)
    response = client.post(
        "/decision-engine/run",
        json={"tenders": live_run["tenders"][:2], "as_of": "not-a-date", "profile": "checkpoint1"},
    )
    assert response.status_code == 422


def test_api_runs_both_profiles(live_run):
    from fastapi.testclient import TestClient

    from tender_agent.api import app

    client = TestClient(app)
    response = client.post(
        "/decision-engine/run",
        json={"tenders": live_run["tenders"], "as_of": live_run["discovered_at"], "profile": "both"},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body["runs"]) == {"checkpoint1", "conservative"}
    assert "robustness" in body
