"""Seeded Monte Carlo model of the profit or loss from bidding on one tender.

Checkpoint 1 produced one expected value per tender from point estimates
(``win_probability x gross_profit - bid_cost``). That number hides the shape of
the bet: a bid usually loses its preparation cost and occasionally wins a
contract whose margin is itself uncertain. This module keeps the Checkpoint 1
point estimates as the *centre* of each distribution and simulates the spread
around them, so the decision engine can reason about downside as well as the
average.

Everything is deterministic for a given seed: each tender draws from its own
random stream derived from ``seed`` and the tender's record ID, so results do
not change when tenders are added, removed, or reordered.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from tender_agent.decision_engine.gates import GateResult


@dataclass(frozen=True)
class SimulationConfig:
    """Every modelling assumption in one place, so it can be reviewed and versioned."""

    n_scenarios: int = 4000
    seed: int = 20261010
    # Win probability: Beta distribution centred on the Checkpoint 1 point estimate.
    win_prob_concentration: float = 12.0
    # Award value relative to the published estimate (estimates are ceilings).
    award_fraction_low: float = 0.80
    award_fraction_high: float = 1.00
    # Above this value a small consultancy is assumed to bid as a consortium partner.
    solo_bid_threshold_eur: float = 750_000.0
    consortium_share_low: float = 0.25
    consortium_share_mode: float = 0.40
    consortium_share_high: float = 0.60
    # Delivery cost ratio: triangular, right-skewed because overruns exceed savings.
    cost_ratio_down: float = 0.05
    cost_ratio_up: float = 0.15
    # Share of cost-overrun risk that is common to all bids (same team, same rates).
    cost_common_factor_rho: float = 0.30
    # Bid preparation cost: lognormal around the Checkpoint 1 rule.
    bid_cost_sigma: float = 0.35
    # Missing contract value: lognormal around the Checkpoint 1 default.
    missing_value_sigma: float = 0.60
    # Share of the bid cost already spent if the team cannot finish in time.
    abandoned_bid_cost_fraction: float = 0.50
    # Day rate used to convert bid cost into bid-team effort (person-days).
    bid_team_day_rate_eur: float = 800.0
    # Calibration. 1.0 / None reproduce the Checkpoint 1 point-estimate rules exactly.
    # They are uncalibrated: i@work has no recorded win/loss history yet, so a
    # conservative profile (see CONSERVATIVE) is run alongside for every decision.
    win_probability_multiplier: float = 1.0
    cost_ratio_mode_override: float | None = None
    profile_name: str = "checkpoint-1-assumptions"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TenderSimulation:
    record_id: str
    identifier: str
    title: str
    capability_fit: float
    win_probability_point: float
    company_share_point: float
    contract_value_basis_eur: float
    value_published: bool
    bid_cost_median_eur: float
    bid_effort_person_days: float
    submission_probability: float
    profit: np.ndarray          # EUR per scenario: margin if won, minus bid cost
    won: np.ndarray             # bool per scenario
    won_revenue: np.ndarray     # i@work revenue per scenario (0 when not won)

    def summary(self, alpha: float = 0.05) -> dict[str, Any]:
        p = self.profit
        cutoff = np.quantile(p, alpha)
        tail = p[p <= cutoff]
        return {
            "record_id": self.record_id,
            "identifier": self.identifier,
            "title": self.title,
            "capability_fit": round(self.capability_fit, 3),
            "win_probability_point": round(self.win_probability_point, 3),
            "win_rate_simulated": round(float(self.won.mean()), 3),
            "submission_probability": round(self.submission_probability, 3),
            "company_share_point": round(self.company_share_point, 3),
            "contract_value_basis_eur": round(self.contract_value_basis_eur, 2),
            "value_published": self.value_published,
            "bid_cost_median_eur": round(self.bid_cost_median_eur, 2),
            "bid_effort_person_days": round(self.bid_effort_person_days, 1),
            "expected_profit_eur": round(float(p.mean()), 2),
            "std_profit_eur": round(float(p.std()), 2),
            "p05_profit_eur": round(float(np.quantile(p, 0.05)), 2),
            "p50_profit_eur": round(float(np.quantile(p, 0.50)), 2),
            "p95_profit_eur": round(float(np.quantile(p, 0.95)), 2),
            "probability_of_loss": round(float((p < 0).mean()), 3),
            "cvar_05_eur": round(float(tail.mean()), 2),
            "expected_won_revenue_eur": round(float(self.won_revenue.mean()), 2),
            "roi_on_bid_cost": round(float(p.mean()) / max(1.0, self.bid_cost_median_eur), 3),
        }


def _stream_seed(seed: int, record_id: str) -> int:
    digest = hashlib.sha256(f"{seed}:{record_id}".encode()).hexdigest()
    return int(digest[:16], 16)


def _triangular_from_uniform(u: np.ndarray, low: float, mode: float, high: float) -> np.ndarray:
    """Inverse CDF of the triangular distribution, so correlated uniforms can be used."""
    if high <= low:
        return np.full_like(u, low)
    c = (mode - low) / (high - low)
    left = low + np.sqrt(u * (high - low) * (mode - low))
    right = high - np.sqrt((1 - u) * (high - low) * (high - mode))
    return np.where(u < c, left, right)


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    from math import erf, sqrt

    return 0.5 * (1.0 + np.vectorize(erf)(x / sqrt(2.0)))


def point_estimates(capability_fit: float, value_eur: float) -> dict[str, float]:
    """The Checkpoint 1 point-estimate rules (offline_workflow.py), kept unchanged."""
    win_probability = min(0.72, max(0.12, 0.18 + capability_fit * 0.48))
    cost_ratio = 0.69 + (1 - capability_fit) * 0.12
    bid_cost = max(8_000.0, min(75_000.0, value_eur * 0.025))
    return {"win_probability": win_probability, "cost_ratio": cost_ratio, "bid_cost": bid_cost}


def simulate_tender(
    tender: dict[str, Any],
    company: dict[str, Any],
    capability_fit: float,
    gate: GateResult,
    common_cost_shock: np.ndarray,
    config: SimulationConfig,
) -> TenderSimulation:
    """Simulate profit for one tender across ``config.n_scenarios`` scenarios."""
    n = config.n_scenarios
    rng = np.random.default_rng(_stream_seed(config.seed, str(tender["recordId"])))

    raw_value = tender.get("estimatedAmount")
    published = raw_value not in (None, "")
    if published:
        basis = float(raw_value)
        value = basis * rng.uniform(config.award_fraction_low, config.award_fraction_high, n)
    else:
        basis = min(1_000_000.0, float(company["max_single_bid_eur"]) * 0.25)
        value = basis * rng.lognormal(0.0, config.missing_value_sigma, n)

    if basis > config.solo_bid_threshold_eur:
        share = rng.triangular(
            config.consortium_share_low,
            config.consortium_share_mode,
            config.consortium_share_high,
            n,
        )
        share_point = config.consortium_share_mode
    else:
        share = np.ones(n)
        share_point = 1.0
    company_value = value * share

    base = point_estimates(capability_fit, basis * share_point)
    p0 = min(0.95, max(0.01, base["win_probability"] * config.win_probability_multiplier))
    if config.cost_ratio_mode_override is not None:
        base["cost_ratio"] = config.cost_ratio_mode_override + (1 - capability_fit) * 0.06
    k = config.win_prob_concentration
    p = rng.beta(p0 * k, (1 - p0) * k, n)

    # Probability the team can finish a compliant offer before the deadline.
    days = gate.days_to_deadline
    if not gate.passed or days is None or days < 0:
        p_submit = 0.0
    else:
        p_submit = min(1.0, days / max(1, gate.required_prep_days))
    submitted = rng.uniform(0, 1, n) < p_submit
    won = submitted & (rng.uniform(0, 1, n) < p)

    # Cost ratio: Gaussian copula mixes a common shock with a tender-specific one.
    rho = config.cost_common_factor_rho
    z = np.sqrt(rho) * common_cost_shock + np.sqrt(1 - rho) * rng.standard_normal(n)
    u = np.clip(_normal_cdf(z), 1e-9, 1 - 1e-9)
    mode = base["cost_ratio"]
    cost_ratio = _triangular_from_uniform(
        u, mode - config.cost_ratio_down, mode, mode + config.cost_ratio_up
    )

    bid_cost_median = base["bid_cost"]
    bid_cost = bid_cost_median * rng.lognormal(0.0, config.bid_cost_sigma, n)
    spent = np.where(submitted, bid_cost, bid_cost * config.abandoned_bid_cost_fraction)
    if p_submit == 0.0:
        spent = np.zeros(n)  # a failed gate means the bid is never started

    margin = company_value * (1 - cost_ratio)
    profit = np.where(won, margin, 0.0) - spent
    won_revenue = np.where(won, company_value, 0.0)

    return TenderSimulation(
        record_id=str(tender["recordId"]),
        identifier=str(tender.get("identifier") or ""),
        title=str(tender.get("title") or ""),
        capability_fit=capability_fit,
        win_probability_point=p0,
        company_share_point=share_point,
        contract_value_basis_eur=basis,
        value_published=published,
        bid_cost_median_eur=bid_cost_median if p_submit > 0 else 0.0,
        bid_effort_person_days=(bid_cost_median / config.bid_team_day_rate_eur)
        if p_submit > 0
        else 0.0,
        submission_probability=p_submit,
        profit=profit,
        won=won,
        won_revenue=won_revenue,
    )


# Planning profile for a firm without win/loss history: half the Checkpoint 1
# win probability (EU service tenders often see single-digit to ~30% win rates)
# and a delivery-cost ratio implied by the company's own 18% target margin.
CONSERVATIVE = SimulationConfig(
    win_probability_multiplier=0.5,
    cost_ratio_mode_override=0.82,
    profile_name="conservative-uncalibrated",
)


def common_shock(config: SimulationConfig) -> np.ndarray:
    """Shared cost-overrun factor, identical for every tender in a run."""
    return np.random.default_rng(config.seed).standard_normal(config.n_scenarios)
