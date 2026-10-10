"""Deterministic hard gates applied before any simulation or optimisation.

Checkpoint 1 decided deadline risk with ``datetime.now()``, which made the same
tender produce different answers on different days, and it accepted any record
whose *status string* said "Open" or "Forthcoming". The live run of 12 August
2026 showed why that is not enough: 7 of the 14 tenders that passed Stage 2 had
a deadline that had already passed or were prior-information notices rather
than open procedures. These gates take an explicit ``as_of`` date so a run can
be reproduced exactly, and they fail closed when a deadline cannot be parsed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

# Procedure-type code the EU Search API returned for the two "-PIN" records in
# the live run. A prior information notice announces a future procedure; it
# cannot be bid on.
PRIOR_INFORMATION_NOTICE_CODES = {"47396222"}

ACTIONABLE_STATUSES = {"Forthcoming", "Open for submission", "Open"}


@dataclass
class GateResult:
    passed: bool
    days_to_deadline: int | None
    deadline_utc: str | None
    required_prep_days: int
    failures: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "days_to_deadline": self.days_to_deadline,
            "deadline_utc": self.deadline_utc,
            "required_prep_days": self.required_prep_days,
            "failures": list(self.failures),
            "conditions": list(self.conditions),
        }


def parse_deadline(raw: str | None) -> datetime | None:
    """Parse the deadline formats seen in real EU Search API payloads.

    Seen in the 12 Aug 2026 run: ``2026-09-15T16:00:59.000+0000`` (ISO with a
    compact offset) and ``14/07/2026`` (day/month/year, on prior-information
    notices). Returns ``None`` when the value cannot be parsed, which callers
    must treat as a failed gate, not as "no deadline risk".
    """
    if not raw:
        return None
    text = str(raw).strip().split(" Europe/")[0]
    match = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", text)
    if match:
        day, month, year = (int(part) for part in match.groups())
        return datetime(year, month, day, 23, 59, 59, tzinfo=UTC)
    text = text.replace("Z", "+00:00")
    text = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", text)  # +0000 -> +00:00
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def required_preparation_days(contract_value_eur: float | None) -> int:
    """Calendar days a small consultancy needs to prepare a compliant offer.

    Planning assumption, not a measured value: larger procedures carry more
    annexes, partner coordination, and pricing work.
    """
    if contract_value_eur is None:
        return 30
    if contract_value_eur < 140_000:
        return 15
    if contract_value_eur < 1_000_000:
        return 25
    return 35


def evaluate_gates(
    tender: dict[str, Any],
    company: dict[str, Any],
    as_of: datetime,
) -> GateResult:
    """Apply the non-negotiable checks. Any failure means NO_BID."""
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=UTC)
    value = tender.get("estimatedAmount")
    value = float(value) if value not in (None, "") else None
    prep_days = required_preparation_days(value)
    failures: list[str] = []
    conditions: list[str] = []

    status = tender.get("status") or "Unknown"
    if status not in ACTIONABLE_STATUSES:
        failures.append(f"Status '{status}' is not an actionable submission status")

    identifier = str(tender.get("identifier") or "")
    if (
        str(tender.get("procedureTypeCode") or "") in PRIOR_INFORMATION_NOTICE_CODES
        or identifier.upper().endswith("-PIN")
    ):
        failures.append("Prior information notice: announces a future procedure, cannot be bid on")

    deadline = parse_deadline(tender.get("deadline"))
    days: int | None = None
    if deadline is None:
        failures.append(f"Deadline '{tender.get('deadline')}' is missing or unparseable")
    else:
        days = (deadline - as_of).days
        if days < 0:
            failures.append(
                f"Deadline {deadline.date().isoformat()} had passed {abs(days)} days before "
                f"the assessment date {as_of.date().isoformat()}"
            )
        elif days < prep_days:
            conditions.append(
                f"Only {days} days to deadline against {prep_days} needed for a compliant offer"
            )

    max_single = float(company.get("max_single_bid_eur") or 0)
    if value is not None and max_single and value > max_single:
        failures.append(
            f"Estimated value EUR {value:,.0f} exceeds the single-bid ceiling EUR {max_single:,.0f}"
        )
    if value is None:
        conditions.append("Contract value not published; value modelled with wide uncertainty")

    return GateResult(
        passed=not failures,
        days_to_deadline=days,
        deadline_utc=deadline.isoformat() if deadline else None,
        required_prep_days=prep_days,
        failures=failures,
        conditions=conditions,
    )
