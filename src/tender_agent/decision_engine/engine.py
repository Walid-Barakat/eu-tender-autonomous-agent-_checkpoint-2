"""Checkpoint 2 bid-decision engine: gates -> Monte Carlo -> portfolio -> decisions.

Entry point: :func:`run_decision_engine`. It is deterministic: the same tenders,
company profile, ``as_of`` date, and configuration always produce the same
output, which is what makes it testable and auditable. No LLM is called here;
the LLM stages of Checkpoint 1 supply relevance and evidence, and this engine
turns them into a portfolio decision a bid manager can defend.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from tender_agent.agents.assessment import technical_assessment
from tender_agent.decision_engine.gates import evaluate_gates, parse_deadline
from tender_agent.decision_engine.monte_carlo import (
    SimulationConfig,
    common_shock,
    simulate_tender,
)
from tender_agent.decision_engine.portfolio import (
    PortfolioConfig,
    efficient_frontier,
    optimise_portfolio,
    portfolio_stats_for,
)
from tender_agent.schemas import CompanyProfile, TenderInput

ENGINE_VERSION = "cp2-decision-engine/1.0.0"


def _capability_fit(tender: dict[str, Any], company: dict[str, Any]) -> tuple[float, list[str]]:
    """Reuse the Checkpoint 1 technical assessment so both checkpoints agree on fit."""
    record = dict(tender)
    record.setdefault(
        "stage2Assessment",
        {
            "relevanceScore": tender.get("relevanceScore"),
            "modelDecision": tender.get("modelDecision"),
        },
    )
    status = record.get("status")
    if status not in {"Forthcoming", "Open for submission", "Open", "Unknown"}:
        record["status"] = "Unknown"
    parsed = TenderInput.model_validate(record)
    technical = technical_assessment(parsed, CompanyProfile.model_validate(company))
    return technical["capability_score"] / 100.0, technical["findings"]


def run_decision_engine(
    tenders: list[dict[str, Any]],
    company: dict[str, Any],
    as_of: datetime | str,
    sim_config: SimulationConfig | None = None,
    portfolio_config: PortfolioConfig | None = None,
) -> dict[str, Any]:
    sim_config = sim_config or SimulationConfig()
    portfolio_config = portfolio_config or PortfolioConfig()
    if isinstance(as_of, str):
        parsed_as_of = parse_deadline(as_of)
        if parsed_as_of is None:
            raise ValueError(f"Unparseable as_of date: {as_of}")
        as_of = parsed_as_of
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=UTC)

    shock = common_shock(sim_config)
    sims = {}
    gates = {}
    fits = {}
    deadlines = {}
    for tender in tenders:
        record_id = str(tender["recordId"])
        gate = evaluate_gates(tender, company, as_of)
        fit, findings = _capability_fit(tender, company)
        gates[record_id] = gate
        fits[record_id] = (fit, findings)
        sims[record_id] = simulate_tender(tender, company, fit, gate, shock, sim_config)
        deadlines[record_id] = parse_deadline(tender.get("deadline")) or as_of

    candidates = [
        r for r, gate in gates.items() if gate.passed and sims[r].profit.mean() > 0
    ]
    optimum = optimise_portfolio(sims, deadlines, company, portfolio_config, candidates)
    frontier = efficient_frontier(sims, deadlines, company, portfolio_config, candidates)
    selected = set(optimum["selected"])

    decisions = []
    for tender in tenders:
        r = str(tender["recordId"])
        gate, sim = gates[r], sims[r]
        summary = sim.summary(portfolio_config.cvar_alpha)
        conditions = list(gate.conditions)
        if sim.company_share_point < 1.0:
            conditions.append(
                "Modelled as a consortium partner share; a lead partner must be secured"
            )
        if not gate.passed:
            decision, status, reasons = "NO_BID", "EXCLUDED", list(gate.failures)
        elif summary["expected_profit_eur"] <= 0:
            decision, status = "NO_BID", "EXCLUDED"
            reasons = ["Expected profit after bid cost is not positive"]
        elif r in selected:
            decision = "CONDITIONAL_BID" if conditions else "BID"
            status, reasons = "SELECTED", ["Selected by the risk-adjusted portfolio optimiser"]
        else:
            decision, status = "CONDITIONAL_BID", "RESERVE"
            reasons = ["Positive expected profit, but excluded by a portfolio constraint"]
            conditions.append("Bid only if budget, team, or delivery capacity becomes available")
        decisions.append(
            {
                **summary,
                "decision": decision,
                "portfolio_status": status,
                "reasons": reasons,
                "conditions": conditions,
                "gate": gate.as_dict(),
                "technical_findings": fits[r][1],
                "deadline": tender.get("deadline"),
                "url": tender.get("url"),
            }
        )

    gate_passing = [r for r, g in gates.items() if g.passed]
    return {
        "engine_version": ENGINE_VERSION,
        "as_of": as_of.isoformat(),
        "company_id": company.get("company_id"),
        "simulation_config": sim_config.as_dict(),
        "portfolio_config": portfolio_config.as_dict(),
        "counts": {
            "tenders_in": len(tenders),
            "gate_passed": len(gate_passing),
            "positive_expected_profit": len(candidates),
            "selected": len(selected),
        },
        "decisions": decisions,
        "portfolio": optimum,
        "frontier": frontier,
        "baselines": {
            "bid_every_gate_passing_tender": {
                "records": gate_passing,
                **portfolio_stats_for(sims, gate_passing, company, portfolio_config),
            },
            "bid_every_positive_ev_tender": {
                "records": candidates,
                **portfolio_stats_for(sims, candidates, company, portfolio_config),
            },
        },
        "_simulations": sims,  # stripped by callers that serialise the result
    }


def serialisable(result: dict[str, Any]) -> dict[str, Any]:
    """Drop the raw scenario arrays before returning JSON."""
    return {k: v for k, v in result.items() if not k.startswith("_")}


def now_utc() -> datetime:
    return datetime.now(UTC)
