"""Deterministic proposal-outline generator (Checkpoint 2 second output mode).

Produces the skeleton described in the Checkpoint 2 scope: problem statement,
objectives, work packages, partner roles, milestones, risk structure, budget
categories, and the evidence that still needs human confirmation. It is built
only from fields the pipeline has actually observed, and it marks every
inferred element as such. The LLM proposal architect (Agent 11 in the Stages
10-15 n8n workflow) can enrich this skeleton; this module guarantees that a
valid outline exists even when no model is available.
"""

from __future__ import annotations

from typing import Any

# Work-package templates keyed by CPV division (first two digits of mainCpv).
_WP_TEMPLATES: dict[str, list[tuple[str, str]]] = {
    "71": [  # Architectural, engineering, construction
        ("Baseline and energy-performance assessment", "Audit current performance and data"),
        ("Technical options and design", "Develop and appraise measures"),
        ("Implementation support", "Specify, procure, and supervise"),
    ],
    "73": [  # Research and development services
        ("State of the art and data collection", "Map players, studies, and datasets"),
        ("Analysis and modelling", "Build the analytical model and scenarios"),
        ("Findings and policy recommendations", "Synthesise and validate results"),
    ],
    "79": [  # Business services: consulting, studies
        ("Methodology and data requirements", "Agree scope, method, and data"),
        ("Benchmarking and analysis", "Run comparisons and quantitative analysis"),
        ("Reporting and stakeholder validation", "Draft, consult, and finalise"),
    ],
    "80": [  # Education and training
        ("Needs assessment", "Identify capacity gaps of target agencies"),
        ("Programme delivery", "Deliver training, peer exchange, and helpdesk"),
        ("Impact monitoring", "Track outcomes and replication"),
    ],
}
_DEFAULT_WPS = [
    ("Inception and requirements", "Confirm scope, deliverables, and acceptance criteria"),
    ("Core delivery", "Execute the technical work programme"),
    ("Reporting and close-out", "Deliver final outputs and knowledge transfer"),
]


def generate_outline(tender: dict[str, Any], decision: dict[str, Any], company: dict[str, Any]) -> dict[str, Any]:
    """Return a structured outline, or a refusal record for NO_BID decisions."""
    if decision.get("decision") == "NO_BID":
        return {
            "record_id": tender.get("recordId"),
            "generated": False,
            "reason": "No outline for NO_BID decisions: " + "; ".join(decision.get("reasons", [])),
        }

    cpv_division = str(tender.get("mainCpv") or "")[:2]
    templates = _WP_TEMPLATES.get(cpv_division, _DEFAULT_WPS)
    work_packages = [
        {"id": "WP0", "title": "Project management and quality assurance", "objective": "Govern delivery, risk, and reporting", "lead": company.get("company_name")},
        *[
            {"id": f"WP{i}", "title": title, "objective": objective, "lead": "To be assigned"}
            for i, (title, objective) in enumerate(templates, start=1)
        ],
    ]
    consortium = decision.get("company_share_point", 1.0) < 1.0
    partner_roles = (
        [
            "Lead partner with prior contracts for this contracting authority (to be secured)",
            f"{company.get('company_name')} as technical partner for energy analytics and assessment",
            "Partner covering any capability gaps listed in the technical findings",
        ]
        if consortium
        else [f"{company.get('company_name')} as sole tenderer"]
    )
    gate = decision.get("gate", {})
    return {
        "record_id": tender.get("recordId"),
        "generated": True,
        "status": "DRAFT - requires human review before any use",
        "decision_context": {
            "decision": decision.get("decision"),
            "expected_profit_eur": decision.get("expected_profit_eur"),
            "probability_of_loss": decision.get("probability_of_loss"),
            "conditions": decision.get("conditions", []),
        },
        "title": f"Proposal outline: {tender.get('title')}",
        "problem_statement": (
            f"{tender.get('description') or tender.get('title')} "
            "[Taken from the published notice; to be checked against the tender specifications.]"
        ),
        "objectives": [
            "Deliver the services specified by the contracting authority on time and to quality",
            "Apply evidence-led energy assessment methods from the company capability profile",
            "[Inferred] Provide measurable outputs aligned with the contracting authority's programme goals",
        ],
        "work_packages": work_packages,
        "partner_roles": partner_roles,
        "milestones": [
            "M1 Inception report accepted",
            "M2 Interim results delivered",
            "M3 Final report and handover accepted",
        ],
        "risk_structure": [
            *decision.get("conditions", []),
            "Specifications not yet ingested: confirm scope, award criteria, and exclusion grounds",
        ],
        "budget_categories": ["Personnel", "Subcontracting", "Travel and meetings", "Other direct costs"],
        "indicative_value_eur": tender.get("estimatedAmount"),
        "submission_deadline": gate.get("deadline_utc") or tender.get("deadline"),
        "evidence_requiring_human_confirmation": [
            "Tender specifications and annexes (not in the pipeline payload for this record)",
            "Exclusion and selection criteria, including turnover and reference requirements",
            "Partner availability and consortium agreement",
            "Price schedule and the company's day rates",
        ],
        "source_url": tender.get("url"),
    }
