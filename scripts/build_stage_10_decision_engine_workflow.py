"""Generate the Checkpoint 2 Stage 10 n8n workflow (portfolio decision engine).

Node IDs are deterministic UUIDv5 values derived from node names, so they are
unique by construction (the Checkpoint 1 generator's duplicate-ID defect cannot
recur) and stable across regenerations.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

NS = uuid.UUID("6f1d8c2e-9a51-4b0e-8a1e-2a6b5d7c3e10")
OUT = Path(__file__).resolve().parents[1] / "workflows" / "n8n" / "stage_10_portfolio_decision_engine.json"
CRED = {"httpHeaderAuth": {"id": "hQtmRSIS4OiJlZ75", "name": "Header Auth account 13"}}


def node(name, type_, version, position, parameters=None, **extra):
    data = {
        "parameters": parameters or {},
        "id": str(uuid.uuid5(NS, name)),
        "name": name,
        "type": type_,
        "typeVersion": version,
        "position": position,
    }
    data.update(extra)
    return data


nodes = [
    node("Stage 10 Overview", "n8n-nodes-base.stickyNote", 1, [-260, -420], {
        "content": "## STAGE 10: PORTFOLIO DECISION ENGINE (Checkpoint 2)\n"
        "Receives the Stage 9 decision packages of one run, calls the deterministic engine "
        "(hard gates -> seeded Monte Carlo -> exact portfolio optimiser), and asks the human "
        "bid authority to approve before anything is published. No bid is submitted by this workflow.",
        "width": 900, "height": 200, "color": 5}),
    node("When Stage 9 Batch Completes", "n8n-nodes-base.executeWorkflowTrigger", 1.1, [-240, 0]),
    node("Manual Demo Trigger", "n8n-nodes-base.manualTrigger", 1, [-240, -180]),
    node("Load Live-Run Sample (12 Aug 2026)", "n8n-nodes-base.code", 2, [0, -180], {
        "mode": "runOnceForAllItems",
        "jsCode": "// Paste the contents of data/live_run_2026_08_12/stage2_advanced_tenders.json\n"
        "// into the pinned data of this node for a fully offline demonstration.\n"
        "return $input.all();"}),
    node("Aggregate Stage 9 Packages", "n8n-nodes-base.code", 2, [240, 0], {
        "mode": "runOnceForAllItems",
        "jsCode": "const items = $input.all().map(i => i.json);\n"
        "const tenders = items.flatMap(j => Array.isArray(j.tenders) ? j.tenders : [j.state?.tender || j.tender || j]);\n"
        "const valid = tenders.filter(t => t && t.recordId);\n"
        "if (!valid.length) throw new Error('Stage 10 received no tender records with recordId');\n"
        "const asOf = items[0]?.discovered_at || valid[0].discoveredAt || new Date().toISOString();\n"
        "return [{ json: { tenders: valid, as_of: asOf, profile: 'both', include_outlines: true,\n"
        "  idempotency_key: 'stage10:' + asOf + ':' + valid.map(t => t.recordId).sort().join(',') } }];"}),
    node("Tender Agent Base URL", "n8n-nodes-base.set", 3.4, [480, 0], {
        "assignments": {"assignments": [{"id": str(uuid.uuid5(NS, "base-url")), "name": "tenderAgentBaseUrl",
                                         "value": "https://REPLACE-WITH-STABLE-HOST", "type": "string"}]},
        "includeOtherFields": True, "options": {}}),
    node("Run Decision Engine (FastAPI)", "n8n-nodes-base.httpRequest", 4.2, [720, 0], {
        "method": "POST",
        "url": "={{ $json.tenderAgentBaseUrl }}/decision-engine/run",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "X-Workflow-Stage", "value": "10"},
            {"name": "Idempotency-Key", "value": "={{ $json.idempotency_key }}"}]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({tenders: $json.tenders, as_of: $json.as_of, profile: $json.profile, include_outlines: $json.include_outlines}) }}",
        "options": {"timeout": 120000}},
        credentials=CRED, retryOnFail=True, maxTries=3, waitBetweenTries=3000, onError="continueErrorOutput"),
    node("Run Decision Engine (Execute Command, optional)", "n8n-nodes-base.executeCommand", 1, [720, 200], {
        "command": "cd /opt/eu-tender-agent && PYTHONPATH=src python -m tender_agent.decision_engine.cli "
        "--input /tmp/stage10_input.json --profile both --outlines"},
        disabled=True,
        notes="Literal 'Execute Command' route named in the brief. Disabled by default: n8n 2.x ships this node "
        "disabled and it needs a self-hosted worker with the repository installed. The HTTP route above is the production path."),
    node("Engine Completed?", "n8n-nodes-base.if", 2.2, [960, 0], {
        "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                       "conditions": [{"id": str(uuid.uuid5(NS, "engine-ok")), "leftValue": "={{ $json.status }}",
                                       "rightValue": "completed", "operator": {"type": "string", "operation": "equals"}}],
                       "combinator": "and"}, "options": {}}),
    node("Build Portfolio Recommendation", "n8n-nodes-base.code", 2, [1200, -100], {
        "mode": "runOnceForAllItems",
        "jsCode": "const r = $input.first().json;\n"
        "const base = r.runs.checkpoint1, cons = r.runs.conservative;\n"
        "const label = id => (base.decisions.find(d => d.record_id === id) || {}).identifier || id;\n"
        "const lines = [\n"
        "  `*Portfolio recommendation* (engine ${base.engine_version}, as of ${base.as_of})`,\n"
        "  `Gate-passing tenders: ${base.counts.gate_passed} of ${base.counts.tenders_in}`,\n"
        "  `Robust under both profiles: ${r.robustness.selected_under_both_profiles.map(label).join(', ') || 'none'}`,\n"
        "  `Only under Checkpoint 1 assumptions: ${r.robustness.selected_only_under_checkpoint1.map(label).join(', ') || 'none'}`,\n"
        "  `Expected profit (C1 / conservative): EUR ${Math.round(base.portfolio.stats.expected_profit_eur).toLocaleString()} / EUR ${Math.round(cons.portfolio.stats.expected_profit_eur).toLocaleString()}`,\n"
        "  'Approve to publish the recommendation. Nothing is submitted to the EU portal.'\n"
        "];\n"
        "return [{ json: { ...r, approvalText: lines.join('\\n'), resumeUrl: $execution.resumeUrl } }];"}),
    node("Ask Bid Authority for Approval (Slack)", "n8n-nodes-base.slack", 2.3, [1440, -100], {
        "select": "channel", "channelId": {"__rl": True, "value": "REPLACE-WITH-CHANNEL-ID", "mode": "id"},
        "text": "={{ $json.approvalText + '\\n\\nApprove: ' + $json.resumeUrl + '?approved=true\\nReject: ' + $json.resumeUrl + '?approved=false' }}",
        "otherOptions": {}}, retryOnFail=True, maxTries=3, waitBetweenTries=2000),
    node("Wait for Human Approval", "n8n-nodes-base.wait", 1.1, [1680, -100], {
        "resume": "webhook", "httpMethod": "GET", "limitWaitTime": True, "limitType": "afterTimeInterval",
        "resumeAmount": 48, "resumeUnit": "hours", "options": {}}),
    node("Approved?", "n8n-nodes-base.if", 2.2, [1920, -100], {
        "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                       "conditions": [{"id": str(uuid.uuid5(NS, "approved")), "leftValue": "={{ $json.query?.approved }}",
                                       "rightValue": "true", "operator": {"type": "string", "operation": "equals"}}],
                       "combinator": "and"}, "options": {}}),
    node("Record Approved Decision", "n8n-nodes-base.set", 3.4, [2160, -200], {
        "assignments": {"assignments": [
            {"id": str(uuid.uuid5(NS, "a1")), "name": "humanDecision", "value": "APPROVED", "type": "string"},
            {"id": str(uuid.uuid5(NS, "a2")), "name": "approvedAt", "value": "={{ $now.toISO() }}", "type": "string"}]},
        "includeOtherFields": True, "options": {}}),
    node("Record Rejected or Expired", "n8n-nodes-base.set", 3.4, [2160, 0], {
        "assignments": {"assignments": [
            {"id": str(uuid.uuid5(NS, "r1")), "name": "humanDecision", "value": "REJECTED_OR_TIMED_OUT", "type": "string"},
            {"id": str(uuid.uuid5(NS, "r2")), "name": "decidedAt", "value": "={{ $now.toISO() }}", "type": "string"}]},
        "includeOtherFields": True, "options": {}}),
    node("Decision Record Output", "n8n-nodes-base.noOp", 1, [2400, -100],
         notes="Connect to the Notion 'Tender Radar' update and Drive archive used in Stage 9. Kept as an explicit "
         "hand-off so the approval record is persisted before any downstream write."),
    node("Engine Failure Alert (Slack)", "n8n-nodes-base.slack", 2.3, [1200, 200], {
        "select": "channel", "channelId": {"__rl": True, "value": "REPLACE-WITH-CHANNEL-ID", "mode": "id"},
        "text": "={{ 'Stage 10 decision engine failed: ' + ($json.error?.message || $json.detail || JSON.stringify($json).slice(0, 300)) }}",
        "otherOptions": {}}, retryOnFail=True, maxTries=3, waitBetweenTries=2000),
    node("Stop: Engine Failed", "n8n-nodes-base.stopAndError", 1, [1440, 200], {
        "errorMessage": "Stage 10 decision engine did not complete; see the Slack alert for details."}),
]

def link(src, dst, out=0):
    return src, out, dst

edges = [
    link("Manual Demo Trigger", "Load Live-Run Sample (12 Aug 2026)"),
    link("Load Live-Run Sample (12 Aug 2026)", "Aggregate Stage 9 Packages"),
    link("When Stage 9 Batch Completes", "Aggregate Stage 9 Packages"),
    link("Aggregate Stage 9 Packages", "Tender Agent Base URL"),
    link("Tender Agent Base URL", "Run Decision Engine (FastAPI)"),
    link("Run Decision Engine (FastAPI)", "Engine Completed?", 0),
    link("Run Decision Engine (FastAPI)", "Engine Failure Alert (Slack)", 1),
    link("Engine Completed?", "Build Portfolio Recommendation", 0),
    link("Engine Completed?", "Engine Failure Alert (Slack)", 1),
    link("Build Portfolio Recommendation", "Ask Bid Authority for Approval (Slack)"),
    link("Ask Bid Authority for Approval (Slack)", "Wait for Human Approval"),
    link("Wait for Human Approval", "Approved?"),
    link("Approved?", "Record Approved Decision", 0),
    link("Approved?", "Record Rejected or Expired", 1),
    link("Record Approved Decision", "Decision Record Output"),
    link("Record Rejected or Expired", "Decision Record Output"),
    link("Engine Failure Alert (Slack)", "Stop: Engine Failed"),
]
connections: dict = {}
for src, out, dst in edges:
    main = connections.setdefault(src, {"main": []})["main"]
    while len(main) <= out:
        main.append([])
    main[out].append({"node": dst, "type": "main", "index": 0})

workflow = {
    "name": "EU Tender Stage 10 - Portfolio Decision Engine (Checkpoint 2)",
    "nodes": nodes,
    "connections": connections,
    "active": False,
    "settings": {"executionOrder": "v1", "saveExecutionProgress": True, "timezone": "Europe/Berlin"},
    "pinData": {},
    "meta": {"templateCredsSetupCompleted": False},
    "tags": [],
}

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(workflow, indent=2), encoding="utf-8")
    ids = [n["id"] for n in nodes]
    names = {n["name"] for n in nodes}
    assert len(ids) == len(set(ids)), "duplicate node IDs"
    for src, out, dst in edges:
        assert src in names and dst in names, f"dangling edge {src} -> {dst}"
    print(f"wrote {OUT} ({len(nodes)} nodes, {len(edges)} edges, unique IDs, no dangling edges)")
