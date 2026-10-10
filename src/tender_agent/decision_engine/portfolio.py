"""Exact portfolio selection over simulated tender outcomes.

A firm does not decide on one tender at a time: bids compete for the same bid
budget, the same people in the same weeks, and the same delivery capacity if
several are won at once. This module chooses the subset of tenders to bid on
that maximises a risk-adjusted expected profit, subject to those constraints.

Method: exhaustive enumeration of every subset of eligible candidates, scored
on the *joint* Monte Carlo scenarios (common random numbers), so correlation
between bids and the probability of winning "too much" are both captured. It
is exact for up to ``max_exact_candidates`` tenders; above that a documented
greedy fallback is used and flagged in the output.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from itertools import combinations
from typing import Any

import numpy as np

from tender_agent.decision_engine.monte_carlo import TenderSimulation


@dataclass(frozen=True)
class PortfolioConfig:
    # Share of the annual bid budget available to the deadlines in one cycle.
    cycle_budget_fraction: float = 0.25
    # Bids whose deadlines fall within the same rolling window compete for the team.
    concurrency_window_days: int = 14
    max_concurrent_bids: int = 3
    # Spare delivery capacity, as a share of annual revenue, if bids are won.
    delivery_capacity_fraction: float = 0.30
    # Maximum acceptable probability of winning more than the team can deliver.
    overcommit_probability_limit: float = 0.10
    # Risk aversion: objective = mean - risk_aversion * max(0, -CVaR_alpha).
    risk_aversion: float = 0.5
    cvar_alpha: float = 0.05
    max_exact_candidates: int = 20

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _cvar(values: np.ndarray, alpha: float) -> float:
    cutoff = np.quantile(values, alpha)
    return float(values[values <= cutoff].mean())


def _portfolio_stats(
    sims: list[TenderSimulation], capacity_eur: float, alpha: float
) -> dict[str, float]:
    if not sims:
        return {
            "expected_profit_eur": 0.0,
            "p05_profit_eur": 0.0,
            "p95_profit_eur": 0.0,
            "probability_of_loss": 0.0,
            "cvar_05_eur": 0.0,
            "expected_wins": 0.0,
            "overcommit_probability": 0.0,
            "planned_bid_cost_eur": 0.0,
        }
    profit = np.sum([s.profit for s in sims], axis=0)
    revenue = np.sum([s.won_revenue for s in sims], axis=0)
    wins = np.sum([s.won for s in sims], axis=0)
    return {
        "expected_profit_eur": round(float(profit.mean()), 2),
        "p05_profit_eur": round(float(np.quantile(profit, 0.05)), 2),
        "p95_profit_eur": round(float(np.quantile(profit, 0.95)), 2),
        "probability_of_loss": round(float((profit < 0).mean()), 3),
        "cvar_05_eur": round(_cvar(profit, alpha), 2),
        "expected_wins": round(float(wins.mean()), 2),
        "overcommit_probability": round(float((revenue > capacity_eur).mean()), 3),
        "planned_bid_cost_eur": round(float(sum(s.bid_cost_median_eur for s in sims)), 2),
    }


def _concurrency_ok(deadlines: list[datetime], window_days: int, limit: int) -> bool:
    ordered = sorted(deadlines)
    for i, start in enumerate(ordered):
        in_window = sum(1 for d in ordered[i:] if (d - start).days <= window_days)
        if in_window > limit:
            return False
    return True


def optimise_portfolio(
    sims: dict[str, TenderSimulation],
    deadlines: dict[str, datetime],
    company: dict[str, Any],
    config: PortfolioConfig,
    candidates: list[str],
    risk_aversion: float | None = None,
) -> dict[str, Any]:
    """Return the best feasible subset of ``candidates`` and why others were left out."""
    lam = config.risk_aversion if risk_aversion is None else risk_aversion
    budget = float(company["available_bid_budget_eur"]) * config.cycle_budget_fraction
    capacity = float(company["annual_revenue_eur"]) * config.delivery_capacity_fraction
    alpha = config.cvar_alpha

    def objective(stats: dict[str, float]) -> float:
        return stats["expected_profit_eur"] - lam * max(0.0, -stats["cvar_05_eur"])

    def feasible(subset: tuple[str, ...]) -> tuple[bool, dict[str, float], str]:
        chosen = [sims[r] for r in subset]
        stats = _portfolio_stats(chosen, capacity, alpha)
        if stats["planned_bid_cost_eur"] > budget:
            return False, stats, "bid budget"
        if not _concurrency_ok(
            [deadlines[r] for r in subset], config.concurrency_window_days, config.max_concurrent_bids
        ):
            return False, stats, "team concurrency"
        if stats["overcommit_probability"] > config.overcommit_probability_limit:
            return False, stats, "delivery capacity"
        return True, stats, ""

    method = "exact enumeration"
    best: tuple[str, ...] = ()
    best_stats = _portfolio_stats([], capacity, alpha)
    best_value = 0.0
    evaluated = 0
    rejected_by: dict[str, int] = {"bid budget": 0, "team concurrency": 0, "delivery capacity": 0}

    if len(candidates) <= config.max_exact_candidates:
        for size in range(1, len(candidates) + 1):
            for subset in combinations(sorted(candidates), size):
                evaluated += 1
                ok, stats, reason = feasible(subset)
                if not ok:
                    rejected_by[reason] += 1
                    continue
                value = objective(stats)
                # Tie-break deterministically: higher value, then fewer bids, then IDs.
                if value > best_value + 1e-6 or (
                    abs(value - best_value) <= 1e-6 and best and len(subset) < len(best)
                ):
                    best, best_stats, best_value = subset, stats, value
    else:
        method = "greedy fallback (candidate count above exact limit)"
        ranked = sorted(
            candidates,
            key=lambda r: sims[r].profit.mean() / max(1.0, sims[r].bid_cost_median_eur),
            reverse=True,
        )
        chosen: list[str] = []
        for record in ranked:
            trial = tuple(chosen + [record])
            evaluated += 1
            ok, stats, reason = feasible(trial)
            if ok and objective(stats) > best_value:
                chosen.append(record)
                best, best_stats, best_value = trial, stats, objective(stats)
            elif not ok:
                rejected_by[reason] += 1

    return {
        "method": method,
        "subsets_evaluated": evaluated,
        "subsets_rejected_by_constraint": rejected_by,
        "risk_aversion": lam,
        "cycle_bid_budget_eur": round(budget, 2),
        "delivery_capacity_eur": round(capacity, 2),
        "selected": list(best),
        "objective_eur": round(best_value, 2),
        "stats": best_stats,
    }


def efficient_frontier(
    sims: dict[str, TenderSimulation],
    deadlines: dict[str, datetime],
    company: dict[str, Any],
    config: PortfolioConfig,
    candidates: list[str],
    risk_aversions: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0),
) -> list[dict[str, Any]]:
    """Re-optimise across risk-aversion levels to show the return/downside trade-off."""
    points = []
    for lam in risk_aversions:
        result = optimise_portfolio(sims, deadlines, company, config, candidates, lam)
        points.append(
            {
                "risk_aversion": lam,
                "selected": result["selected"],
                "expected_profit_eur": result["stats"]["expected_profit_eur"],
                "cvar_05_eur": result["stats"]["cvar_05_eur"],
                "probability_of_loss": result["stats"]["probability_of_loss"],
            }
        )
    return points


def portfolio_stats_for(
    sims: dict[str, TenderSimulation], records: list[str], company: dict[str, Any], config: PortfolioConfig
) -> dict[str, float]:
    capacity = float(company["annual_revenue_eur"]) * config.delivery_capacity_fraction
    return _portfolio_stats([sims[r] for r in records], capacity, config.cvar_alpha)
