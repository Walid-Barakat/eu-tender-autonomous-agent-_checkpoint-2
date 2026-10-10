"""Export the engine's scenario matrices for the browser portfolio console.

The console re-runs the exact portfolio optimiser in JavaScript over these
same scenarios, so at default settings it reproduces the Python result
exactly; changing a slider re-optimises on identical data.
"""

from __future__ import annotations

import json
from pathlib import Path

from tender_agent.decision_engine.engine import run_decision_engine, serialisable
from tender_agent.decision_engine.monte_carlo import CONSERVATIVE, SimulationConfig
from tender_agent.decision_engine.proposal_outline import generate_outline
from tender_agent.tools.core import load_company_profile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ui" / "portfolio_data.json"


def main() -> None:
    run = json.loads((ROOT / "data" / "live_run_2026_08_12" / "stage2_advanced_tenders.json").read_text())
    company = load_company_profile("i@work")
    by_id = {t["recordId"]: t for t in run["tenders"]}
    payload = {"as_of": run["discovered_at"], "run_id": run["run_id"], "company": company, "profiles": {}}
    for name, config in (("checkpoint1", SimulationConfig()), ("conservative", CONSERVATIVE)):
        result = run_decision_engine(run["tenders"], company, run["discovered_at"], sim_config=config)
        sims = result["_simulations"]
        clean = serialisable(result)
        for decision in clean["decisions"]:
            decision["outline"] = generate_outline(by_id[decision["record_id"]], decision, company)
            decision["value_eur"] = by_id[decision["record_id"]].get("estimatedAmount")
        payload["profiles"][name] = {
            **clean,
            "scenarios": {
                r: {
                    "profit": [round(float(x)) for x in sims[r].profit],
                    "revenue": [round(float(x)) for x in sims[r].won_revenue],
                }
                for r in sims
                if sims[r].submission_probability > 0
            },
        }
    OUT.write_text(json.dumps(payload, separators=(",", ":"), default=str), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
