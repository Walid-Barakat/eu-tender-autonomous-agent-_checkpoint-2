"""FastAPI boundary called by n8n HTTP Request nodes."""

from __future__ import annotations

import hmac
import uuid
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from tender_agent.config import settings
from tender_agent.offline_workflow import assess_tender
from tender_agent.pdf_endpoint import router as pdf_router
from tender_agent.schemas import AssessmentRequest, AssessmentResponse

app = FastAPI(
    title="EU Tender Autonomous Agent",
    version="0.1.0",
)
app.include_router(pdf_router)


class StageExecutionRequest(BaseModel):
    state: dict[str, Any] = Field(default_factory=dict)


class DecisionEngineRequest(BaseModel):
    """Checkpoint 2: a batch of Stage 9 tender records for portfolio selection."""

    tenders: list[dict[str, Any]] = Field(min_length=1)
    as_of: str = Field(description="Assessment date, ISO 8601; makes the run reproducible")
    company_id: str = "i@work"
    profile: str = Field(default="both", pattern="^(checkpoint1|conservative|both)$")
    include_outlines: bool = False


def _authenticate(value: str | None) -> None:
    expected = settings.shared_secret
    if expected and not hmac.compare_digest(value or "", expected):
        raise HTTPException(status_code=401, detail="Invalid shared secret")


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "EU Tender Autonomous Agent",
        "status": "ok",
        "docs": "/docs",
        "pdf_endpoint": "/reports/pdf",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": settings.mode,
        "pinecone": settings.pinecone_enabled,
        "pdf_endpoint": True,
    }


@app.post("/assess", response_model=AssessmentResponse)
async def assess(
    request: AssessmentRequest,
    x_n8n_secret: str | None = Header(default=None),
) -> AssessmentResponse:
    _authenticate(x_n8n_secret)
    run_id = str(uuid.uuid4())

    try:
        if request.mode == "live":
            from tender_agent.graph import build_assessment_graph
            from tender_agent.schemas import DecisionReport

            state = await build_assessment_graph().ainvoke(
                {
                    "run_id": run_id,
                    "company_id": request.company_id,
                    "tender": request.tender.model_dump(by_alias=True),
                }
            )
            if state.get("status") != "completed" or not state.get("report"):
                raise RuntimeError(
                    "LangGraph assessment did not produce a validated report"
                )
            report = DecisionReport.model_validate(state["report"])
        else:
            report = assess_tender(
                request.tender.model_dump(by_alias=True),
                request.company_id,
            )

        settings.report_dir.mkdir(parents=True, exist_ok=True)
        output = settings.report_dir / f"{report.report_id}.md"
        output.write_text(report.report_markdown, encoding="utf-8")
        return AssessmentResponse(run_id=run_id, status="completed", report=report)
    except Exception as exc:  # noqa: BLE001
        return AssessmentResponse(
            run_id=run_id,
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
        )


@app.post("/stages/{stage_number}")
async def execute_visible_stage(
    stage_number: int,
    request: StageExecutionRequest,
    x_n8n_secret: str | None = Header(default=None),
) -> dict[str, Any]:
    """Execute one n8n-visible Stage 3 to 9 LangGraph subgraph."""
    _authenticate(x_n8n_secret)
    if stage_number < 3 or stage_number > 9:
        raise HTTPException(status_code=404, detail="Stage must be between 3 and 9")

    try:
        from tender_agent.graph import run_visible_stage

        result = await run_visible_stage(stage_number, request.state)
        if stage_number == 9 and result.get("report"):
            settings.report_dir.mkdir(parents=True, exist_ok=True)
            report = result["report"]
            report_id = report.get("report_id", request.state.get("run_id", "report"))
            output = settings.report_dir / f"{report_id}.md"
            output.write_text(report.get("report_markdown", ""), encoding="utf-8")

        return {"stage": stage_number, "status": "completed", "state": result}
    except Exception as exc:  # noqa: BLE001
        return {
            "stage": stage_number,
            "status": "failed",
            "state": request.state,
            "error": f"{type(exc).__name__}: {exc}",
        }


@app.post("/decision-engine/run")
def run_decision_engine_endpoint(
    request: DecisionEngineRequest,
    x_n8n_secret: str | None = Header(default=None),
) -> dict[str, Any]:
    """Checkpoint 2: hard gates, Monte Carlo risk, and portfolio optimisation.

    Unlike the Checkpoint 1 endpoints, invalid input returns HTTP 422 and an
    engine failure returns HTTP 500, so n8n retry and error routing can react.
    """
    _authenticate(x_n8n_secret)
    import json
    import tempfile
    from pathlib import Path

    from tender_agent.decision_engine.cli import main as engine_cli

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "input.json"
        target = Path(tmp) / "output.json"
        source.write_text(json.dumps({"tenders": request.tenders}), encoding="utf-8")
        argv = [
            "--input", str(source), "--as-of", request.as_of, "--company", request.company_id,
            "--profile", request.profile, "--output", str(target),
        ]
        if request.include_outlines:
            argv.append("--outlines")
        try:
            code = engine_cli(argv)
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=f"{type(exc).__name__}: {exc}") from exc
        if code != 0:
            raise HTTPException(status_code=422, detail="Invalid decision-engine input")
        return json.loads(target.read_text(encoding="utf-8"))

