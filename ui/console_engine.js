// Portfolio optimiser for the browser console. Mirrors
// src/tender_agent/decision_engine/portfolio.py line for line, over the same
// exported Monte Carlo scenarios, so default settings reproduce the Python result.
(function (root) {
  "use strict";

  function quantileLinear(values, q) {
    const a = Float64Array.from(values).sort();
    const pos = (a.length - 1) * q;
    const lo = Math.floor(pos), hi = Math.ceil(pos);
    return a[lo] + (a[hi] - a[lo]) * (pos - lo);
  }

  function round(x, digits) {
    const f = Math.pow(10, digits);
    return Math.round(x * f) / f;
  }

  function portfolioStats(records, scenarios, bidCost, capacity, alpha) {
    if (!records.length) {
      return { expected_profit_eur: 0, p05_profit_eur: 0, p95_profit_eur: 0, probability_of_loss: 0,
        cvar_05_eur: 0, overcommit_probability: 0, planned_bid_cost_eur: 0, profit: null };
    }
    const n = scenarios[records[0]].profit.length;
    const profit = new Float64Array(n), revenue = new Float64Array(n);
    for (const r of records) {
      const s = scenarios[r];
      for (let i = 0; i < n; i++) { profit[i] += s.profit[i]; revenue[i] += s.revenue[i]; }
    }
    let sum = 0, losses = 0, over = 0;
    for (let i = 0; i < n; i++) { sum += profit[i]; if (profit[i] < 0) losses++; if (revenue[i] > capacity) over++; }
    const cutoff = quantileLinear(profit, alpha);
    let tailSum = 0, tailN = 0;
    for (let i = 0; i < n; i++) if (profit[i] <= cutoff) { tailSum += profit[i]; tailN++; }
    return {
      expected_profit_eur: round(sum / n, 2),
      p05_profit_eur: round(quantileLinear(profit, 0.05), 2),
      p95_profit_eur: round(quantileLinear(profit, 0.95), 2),
      probability_of_loss: round(losses / n, 3),
      cvar_05_eur: round(tailSum / tailN, 2),
      overcommit_probability: round(over / n, 3),
      planned_bid_cost_eur: round(records.reduce((t, r) => t + bidCost[r], 0), 2),
      profit,
    };
  }

  function concurrencyOk(deadlines, windowDays, limit) {
    const ordered = deadlines.slice().sort((a, b) => a - b);
    for (let i = 0; i < ordered.length; i++) {
      let inWindow = 0;
      for (let j = i; j < ordered.length; j++) {
        if (Math.floor((ordered[j] - ordered[i]) / 86400000) <= windowDays) inWindow++;
      }
      if (inWindow > limit) return false;
    }
    return true;
  }

  function combinations(items, size) {
    const out = [];
    const pick = (start, acc) => {
      if (acc.length === size) { out.push(acc.slice()); return; }
      for (let i = start; i < items.length; i++) { acc.push(items[i]); pick(i + 1, acc); acc.pop(); }
    };
    pick(0, []);
    return out;
  }

  // Python's sorted() on str compares code points; so does this comparator.
  const byCodePoint = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

  function optimise(profile, settings) {
    const decisions = profile.decisions;
    const scenarios = profile.scenarios;
    const alpha = 0.05;
    const bidCost = {}, deadline = {};
    for (const d of decisions) {
      bidCost[d.record_id] = d.bid_cost_median_eur;
      deadline[d.record_id] = Date.parse(d.gate.deadline_utc || "1970-01-01T00:00:00Z");
    }
    const candidates = decisions
      .filter(d => d.gate.passed && d.expected_profit_eur > 0)
      .map(d => d.record_id)
      .sort(byCodePoint);
    const lam = settings.riskAversion;
    const objective = s => s.expected_profit_eur - lam * Math.max(0, -s.cvar_05_eur);
    let best = [], bestStats = portfolioStats([], scenarios, bidCost, settings.capacity, alpha), bestValue = 0;
    const rejected = { "bid budget": 0, "team concurrency": 0, "delivery capacity": 0 };
    let evaluated = 0;
    for (let size = 1; size <= candidates.length; size++) {
      for (const subset of combinations(candidates, size)) {
        evaluated++;
        const stats = portfolioStats(subset, scenarios, bidCost, settings.capacity, alpha);
        if (stats.planned_bid_cost_eur > settings.budget) { rejected["bid budget"]++; continue; }
        if (!concurrencyOk(subset.map(r => deadline[r]), settings.windowDays, settings.maxConcurrent)) {
          rejected["team concurrency"]++; continue;
        }
        if (stats.overcommit_probability > settings.overcommitLimit) { rejected["delivery capacity"]++; continue; }
        const value = objective(stats);
        if (value > bestValue + 1e-6 || (Math.abs(value - bestValue) <= 1e-6 && best.length && subset.length < best.length)) {
          best = subset; bestStats = stats; bestValue = value;
        }
      }
    }
    const eligible = decisions.filter(d => d.gate.passed).map(d => d.record_id);
    return {
      selected: best,
      objective_eur: round(bestValue, 2),
      stats: bestStats,
      evaluated,
      rejected,
      bidAll: portfolioStats(eligible, scenarios, bidCost, settings.capacity, alpha),
      eligible,
    };
  }

  const RESERVE_NOTE = "Bid only if budget, team, or delivery capacity becomes available";

  function decide(decision, selectedSet) {
    const base = decision.conditions.filter(c => c !== RESERVE_NOTE);
    if (!decision.gate.passed) return { decision: "NO_BID", status: "EXCLUDED", conditions: base, reasons: decision.gate.failures };
    if (decision.expected_profit_eur <= 0) {
      return { decision: "NO_BID", status: "EXCLUDED", conditions: base, reasons: ["Expected profit after bid cost is not positive"] };
    }
    if (selectedSet.has(decision.record_id)) {
      return { decision: base.length ? "CONDITIONAL_BID" : "BID", status: "SELECTED", conditions: base,
        reasons: ["Selected by the risk-adjusted portfolio optimiser"] };
    }
    return { decision: "CONDITIONAL_BID", status: "RESERVE", conditions: base.concat([RESERVE_NOTE]),
      reasons: ["Positive expected profit, but excluded by a portfolio constraint"] };
  }

  const api = { optimise, decide, portfolioStats, quantileLinear };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PortfolioEngine = api;
})(this);
