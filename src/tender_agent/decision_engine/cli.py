"""Command-line entry point for the decision engine.

Usable from an n8n Execute Command node (the mechanism the brief names) as
well as from a terminal:

    python -m tender_agent.decision_engine.cli \
        --input data/live_run_2026_08_12/stage2_advanced_tenders.json \
        --as-of 2026-08-12T22:09:14Z --profile both --output engine_result.json

Input is either a JSON list of tender records or an object with a ``tenders``
key (the shape n8n produces when it aggregates Stage 9 outputs). Output is JSON
on stdout or in ``--output``; the exit code is non-zero on invalid input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tender_agent.decision_engine.engine import run_decision_engine, serialisable
from tender_agent.decision_engine.monte_carlo import CONSERVATIVE, SimulationConfig
from tender_agent.decision_engine.proposal_outline import generate_outline
from tender_agent.tools.core import load_company_profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, help="JSON file with tender records")
    parser.add_argument("--as-of", help="Assessment date (ISO 8601). Defaults to input discovered_at.")
    parser.add_argument("--company", default="i@work")
    parser.add_argument("--profile", choices=["checkpoint1", "conservative", "both"], default="both")
    parser.add_argument("--outlines", action="store_true", help="Add proposal outlines for bid decisions")
    parser.add_argument("--output", help="Write JSON here instead of stdout")
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    tenders = payload if isinstance(payload, list) else payload.get("tenders", [])
    as_of = args.as_of or (payload.get("discovered_at") if isinstance(payload, dict) else None)
    if not tenders or not as_of:
        print(json.dumps({"status": "failed", "error": "Need tenders and an as-of date"}))
        return 2

    company = load_company_profile(args.company)
    profiles = {
        "checkpoint1": [("checkpoint1", SimulationConfig())],
        "conservative": [("conservative", CONSERVATIVE)],
        "both": [("checkpoint1", SimulationConfig()), ("conservative", CONSERVATIVE)],
    }[args.profile]

    output = {"status": "completed", "runs": {}}
    by_id = {str(t["recordId"]): t for t in tenders}
    for name, config in profiles:
        result = serialisable(run_decision_engine(tenders, company, as_of, sim_config=config))
        if args.outlines:
            result["proposal_outlines"] = [
                generate_outline(by_id[d["record_id"]], d, company)
                for d in result["decisions"]
                if d["decision"] != "NO_BID"
            ]
        output["runs"][name] = result
    if len(profiles) == 2:
        c1 = {d["record_id"]: d["decision"] for d in output["runs"]["checkpoint1"]["decisions"]}
        cons = {d["record_id"]: d["decision"] for d in output["runs"]["conservative"]["decisions"]}
        sel1 = set(output["runs"]["checkpoint1"]["portfolio"]["selected"])
        sel2 = set(output["runs"]["conservative"]["portfolio"]["selected"])
        output["robustness"] = {
            "selected_under_both_profiles": sorted(sel1 & sel2),
            "selected_only_under_checkpoint1": sorted(sel1 - sel2),
            "decision_changed": sorted(r for r in c1 if c1[r] != cons[r]),
        }

    text = json.dumps(output, indent=2, ensure_ascii=False, default=str)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
