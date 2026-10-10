"""ROI model for deploying the Tender Intelligence Agent at a client firm.

Decision-maker: a mid-size energy engineering / advisory firm that bids on EU
tenders (the company profile in data/company_profiles/i-at-work.json: EUR 12M
revenue, EUR 450k annual bid budget). i@work provides the agent as a managed
service. Every input is an explicit assumption with a low / base / high value
and a stated basis; nothing is presented as measured unless it was.

    ROI = (Benefit - Cost) / Cost x 100      (cumulative over the horizon)

Benefits are split into two tiers because their evidence differs:
  Tier A (operational): screening and qualification time saved, and bid cost
          not wasted on no-go bids. Moderately evidenced.
  Tier B (outcome): extra positive-expected-value bids found because coverage
          rises. Driven by the engine's own estimates, which are uncalibrated.
The headline ROI uses Tier A only. Tier B is reported separately.

Run:  PYTHONPATH=src python analysis/roi_model.py   (writes analysis/roi_results.json)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "roi_results.json"
HORIZON_MONTHS = 36
RAMP_MONTHS = 3          # pilot calibration period at half benefit
RAMP_FACTOR = 0.5


@dataclass(frozen=True)
class A:  # one assumption
    low: float
    base: float
    high: float
    unit: str
    basis: str


ASSUMPTIONS: dict[str, A] = {
    # ---- upfront
    "setup_days": A(8, 12, 18, "consultant days", "i@work configuration: company profile, capability corpus, n8n hosting, Notion/Slack, calibration data"),
    "consultant_day_rate_eur": A(800, 900, 1100, "EUR/day", "Independent energy/AI consulting day rates in Germany (planning range)"),
    "client_onboarding_hours": A(24, 40, 64, "hours", "Client staff time for workshops, data supply, acceptance testing"),
    "client_hourly_cost_eur": A(60, 75, 95, "EUR/hour", "Fully loaded internal cost of a bid/technical consultant"),
    # ---- ongoing
    "service_fee_month_eur": A(900, 1200, 1600, "EUR/month", "i@work managed-service fee (commercial model, Phase 17)"),
    "infra_month_eur": A(60, 120, 250, "EUR/month", "n8n hosting, Pinecone starter tier, monitoring; Notion/Slack assumed already licensed"),
    "llm_cost_per_assessment_eur": A(0.18, 0.40, 0.80, "EUR", "Checkpoint 1 green-software assessment: USD 0.20-0.45 per completed assessment; high case doubles for retries"),
    "deep_assessments_month": A(15, 25, 35, "assessments", "Live run: 14 of 25 listings advanced in one batch"),
    "listings_month": A(40, 60, 90, "listings", "Energy-keyword EU notices screened per month (25 in one batch on 12 Aug 2026)"),
    # ---- manual baseline
    "manual_screen_minutes_per_listing": A(6, 10, 15, "minutes", "Reading title, scope, deadline and value on the portal"),
    "manual_qualified_month": A(6, 10, 14, "tenders", "Tenders a firm qualifies by hand each month (fewer than the agent covers)"),
    "manual_hours_per_qualification": A(4, 6, 10, "hours", "Reading specifications, checking eligibility, rough pricing, go/no-go memo"),
    # ---- with the agent
    "review_hours_per_assessment": A(0.25, 0.40, 0.75, "hours", "Human review of each automated assessment"),
    "approval_hours_month": A(2, 3, 5, "hours", "Stage 10 portfolio approval by the bid authority"),
    "time_realisation": A(0.6, 0.8, 0.95, "share", "Share of freed time actually redeployed to billable or bid work"),
    # ---- avoided waste (Tier A)
    "no_go_bids_avoided_year": A(1, 2, 4, "bids/year", "Bids started then abandoned or lost on a hard-gate issue the agent flags early"),
    "avg_bid_cost_eur": A(10000, 15000, 25000, "EUR", "Engine bid-cost medians on the live run: EUR 8k-49.5k"),
    "wasted_fraction": A(0.3, 0.5, 0.8, "share", "Share of a bid's cost already spent when the problem is found manually"),
    # ---- outcome effect (Tier B, reported separately)
    "extra_positive_ev_bids_year": A(0, 4, 8, "bids/year", "Additional selected bids from 2-3x wider coverage"),
    "ev_per_selected_bid_eur": A(0, 13500, 40000, "EUR", "Engine: EUR 13.5k for the bid selected under the conservative profile; EUR 30k-290k under Checkpoint 1 assumptions"),
}


def _monthly(v: dict[str, float]) -> dict[str, float]:
    manual_h = v["listings_month"] * v["manual_screen_minutes_per_listing"] / 60 + \
        v["manual_qualified_month"] * v["manual_hours_per_qualification"]
    agent_h = v["deep_assessments_month"] * v["review_hours_per_assessment"] + v["approval_hours_month"]
    hours_saved = max(0.0, manual_h - agent_h)
    return {
        "manual_hours": manual_h,
        "agent_hours": agent_h,
        "hours_saved": hours_saved,
        "time_benefit_eur": hours_saved * v["client_hourly_cost_eur"] * v["time_realisation"],
        "waste_benefit_eur": v["no_go_bids_avoided_year"] * v["avg_bid_cost_eur"] * v["wasted_fraction"] / 12,
        "outcome_benefit_eur": v["extra_positive_ev_bids_year"] * v["ev_per_selected_bid_eur"] / 12,
        "running_cost_eur": v["service_fee_month_eur"] + v["infra_month_eur"]
        + v["deep_assessments_month"] * v["llm_cost_per_assessment_eur"],
    }


def evaluate(v: dict[str, float]) -> dict:
    upfront = v["setup_days"] * v["consultant_day_rate_eur"] + v["client_onboarding_hours"] * v["client_hourly_cost_eur"]
    m = _monthly(v)
    cost = [upfront] + [0.0] * HORIZON_MONTHS
    benefit_a = [0.0] * (HORIZON_MONTHS + 1)
    benefit_b = [0.0] * (HORIZON_MONTHS + 1)
    for month in range(1, HORIZON_MONTHS + 1):
        ramp = RAMP_FACTOR if month <= RAMP_MONTHS else 1.0
        cost[month] = m["running_cost_eur"]
        benefit_a[month] = ramp * (m["time_benefit_eur"] + m["waste_benefit_eur"])
        benefit_b[month] = ramp * m["outcome_benefit_eur"]
    cum_cost = np.cumsum(cost)
    cum_a = np.cumsum(benefit_a)
    cum_ab = np.cumsum(np.array(benefit_a) + np.array(benefit_b))

    def roi(cum_benefit, month):
        return (cum_benefit[month] - cum_cost[month]) / cum_cost[month] * 100

    def breakeven(cum_benefit):
        hits = np.nonzero(cum_benefit[1:] >= cum_cost[1:])[0]
        return int(hits[0]) + 1 if len(hits) else None

    return {
        "upfront_cost_eur": round(upfront, 0),
        "monthly_running_cost_eur": round(m["running_cost_eur"], 0),
        "manual_hours_month": round(m["manual_hours"], 1),
        "agent_hours_month": round(m["agent_hours"], 1),
        "hours_saved_month": round(m["hours_saved"], 1),
        "monthly_benefit_tier_a_eur": round(m["time_benefit_eur"] + m["waste_benefit_eur"], 0),
        "monthly_benefit_tier_b_eur": round(m["outcome_benefit_eur"], 0),
        "cost_12m_eur": round(float(cum_cost[12]), 0),
        "cost_36m_eur": round(float(cum_cost[36]), 0),
        "benefit_tier_a_12m_eur": round(float(cum_a[12]), 0),
        "benefit_tier_a_36m_eur": round(float(cum_a[36]), 0),
        "roi_12m_tier_a_pct": round(roi(cum_a, 12), 1),
        "roi_36m_tier_a_pct": round(roi(cum_a, 36), 1),
        "roi_12m_with_outcomes_pct": round(roi(cum_ab, 12), 1),
        "roi_36m_with_outcomes_pct": round(roi(cum_ab, 36), 1),
        "breakeven_month_tier_a": breakeven(cum_a),
        "breakeven_month_with_outcomes": breakeven(cum_ab),
        "expected_value_36m_tier_a_eur": round(float(cum_a[36] - cum_cost[36]), 0),
        "expected_value_36m_with_outcomes_eur": round(float(cum_ab[36] - cum_cost[36]), 0),
        "cumulative_net_tier_a_eur": [round(float(x), 0) for x in (cum_a - cum_cost)],
        "cumulative_net_with_outcomes_eur": [round(float(x), 0) for x in (cum_ab - cum_cost)],
    }


def scenario(name: str) -> dict[str, float]:
    """Pessimistic takes the cost-high and benefit-low end of every range."""
    cost_side = {"setup_days", "consultant_day_rate_eur", "client_onboarding_hours", "service_fee_month_eur",
                 "infra_month_eur", "llm_cost_per_assessment_eur", "review_hours_per_assessment", "approval_hours_month",
                 "deep_assessments_month"}
    out = {}
    for key, a in ASSUMPTIONS.items():
        if name == "base":
            out[key] = a.base
        elif name == "pessimistic":
            out[key] = a.high if key in cost_side else a.low
        else:
            out[key] = a.low if key in cost_side else a.high
    # The hourly cost is both a cost (onboarding) and a benefit (time saved); keep it at base in the
    # extreme scenarios so the scenarios move only one way.
    out["client_hourly_cost_eur"] = ASSUMPTIONS["client_hourly_cost_eur"].base
    return out


def monte_carlo(n: int = 20000, seed: int = 20261010) -> dict:
    rng = np.random.default_rng(seed)
    draws = {k: rng.triangular(a.low, a.base, a.high, n) if a.high > a.low else np.full(n, a.base)
             for k, a in ASSUMPTIONS.items()}
    results = [evaluate({k: float(draws[k][i]) for k in ASSUMPTIONS}) for i in range(n)]

    def stats(key):
        values = np.array([r[key] if r[key] is not None else np.nan for r in results], dtype=float)
        finite = values[np.isfinite(values)]
        return {"p10": round(float(np.percentile(finite, 10)), 1), "p50": round(float(np.percentile(finite, 50)), 1),
                "p90": round(float(np.percentile(finite, 90)), 1),
                "never_breaks_even_share": round(float(np.isnan(values).mean()), 3)}

    roi12 = np.array([r["roi_12m_tier_a_pct"] for r in results])
    roi36 = np.array([r["roi_36m_tier_a_pct"] for r in results])
    return {
        "draws": n,
        "seed": seed,
        "roi_12m_tier_a_pct": stats("roi_12m_tier_a_pct"),
        "roi_36m_tier_a_pct": stats("roi_36m_tier_a_pct"),
        "roi_36m_with_outcomes_pct": stats("roi_36m_with_outcomes_pct"),
        "breakeven_month_tier_a": stats("breakeven_month_tier_a"),
        "probability_roi_12m_negative": round(float((roi12 < 0).mean()), 3),
        "probability_roi_36m_negative": round(float((roi36 < 0).mean()), 3),
    }


def sensitivity() -> list[dict]:
    """One-at-a-time swing of the 36-month Tier A ROI, largest first (tornado data)."""
    base = scenario("base")
    ref = evaluate(base)["roi_36m_tier_a_pct"]
    rows = []
    for key, a in ASSUMPTIONS.items():
        lo = evaluate({**base, key: a.low})["roi_36m_tier_a_pct"]
        hi = evaluate({**base, key: a.high})["roi_36m_tier_a_pct"]
        rows.append({"assumption": key, "roi_at_low": lo, "roi_at_high": hi, "swing": round(abs(hi - lo), 1)})
    rows.sort(key=lambda r: r["swing"], reverse=True)
    return [r for r in rows if r["swing"] > 0][:10] + [{"base_roi_36m_tier_a_pct": ref}]


if __name__ == "__main__":
    result = {
        "assumptions": {k: a.__dict__ for k, a in ASSUMPTIONS.items()},
        "scenarios": {s: evaluate(scenario(s)) for s in ("pessimistic", "base", "optimistic")},
        "monte_carlo": monte_carlo(),
        "sensitivity": sensitivity(),
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for s, r in result["scenarios"].items():
        print(s, {k: v for k, v in r.items() if not k.startswith("cumulative")})
    print("MC", result["monte_carlo"])
    for row in result["sensitivity"]:
        print(row)
