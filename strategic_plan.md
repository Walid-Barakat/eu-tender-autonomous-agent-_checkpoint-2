# Strategic Deployment Plan — Tender Intelligence Agent

**Phase 17** · Checkpoint 2 · prepared 7 October 2026 by Dr.-Ing. Walid Barakat, i@work UG
**Path:** POC → Pilot → Full deployment. Each stage ends in a go/no-go decision that is made against stated criteria, not by default.

```text
POC  (done, Jul–Oct 2026)
  Checkpoint 1: 9-stage n8n + LangGraph pipeline, live run 25 → 14 tenders
  Checkpoint 2: deterministic decision engine, evaluation, compliance pack
        │  Gate 0, 10 Oct 2026: final presentation; pre-pilot hardening list agreed
        ▼
PILOT  (one client firm, 3 months, 9 Nov 2026 – 5 Feb 2027)
        │  Gate 1, mid-Feb 2027: success criteria met? → continue / fix / stop
        ▼
FULL DEPLOYMENT  (Mar 2027 onward: productise, then 3–5 clients by end 2027)
        │  Gate 2, before 2 Dec 2027: re-classify under the AI Act if the scope changed
```

---

## 1. Where the POC stands (evidence, not intention)

| Capability | Evidence | Gap carried into the pilot |
|---|---|---|
| Discovery and triage on the official EU API | Recorded live run: 25 discovered, 14 advanced, 11 archived (12 Aug 2026) | 7 of the 14 advanced were not biddable; Stage 2 triage cannot see dates |
| Evidence acquisition (ReAct, MCP, Pinecone) | Live-mode screenshots and recordings, 13 Aug 2026 | 5 of 7 MCP tools bound to the agent; the retrieval backend is not labelled in outputs |
| Bid decision | Checkpoint 2 engine: gates, Monte Carlo, exact portfolio optimiser; 22 tests passing | Win and margin assumptions uncalibrated |
| Evaluation | 23-example dataset, 7 evaluators; Checkpoint 2 rejects 10 of 10 non-biddable records (Checkpoint 1: 2 of 10) | Not yet uploaded to LangSmith; LLM stages not adversarially tested |
| Publication | PDF, Drive, Notion, Slack receipts in the recorded run | Completion marker runs in parallel with Notion and Slack; terminal writes not retried |
| Compliance | AI Act: not high-risk, two small binding actions; GDPR: proceed with conditions | Marking fields, PII filter, DPAs, retention |

## 2. Pre-pilot hardening (13 Oct – 6 Nov 2026)

Pilot entry criteria. Every item is a must, and each one comes from a finding in this project's own evidence.

| # | Item | Source of the requirement | Effort |
|---:|---|---|---:|
| 1 | Rotate all credentials that were ever in a shared archive; release only with `git archive`; secret scan in CI | Repository audit (.env in a ZIP) | 0.5 d |
| 2 | Stable EU hosting for n8n and FastAPI, replacing temporary tunnels; activate the workflows | Execution record, tunnel expiry | 2 d |
| 3 | PII filter before every LLM and embedding call; per-tender Pinecone namespaces | `gdpr_documentation.md` §4 | 3 d |
| 4 | Executed DPAs and transfer tools: Anthropic, OpenAI, Pinecone, hosting provider | GDPR audit: 7 of 10 accountability items missing | external |
| 5 | Article 50(2) marking fields in every report; AI literacy module | `eu_ai_act_compliance.md` §5 | 1.5 d |
| 6 | Stage 9: merge before "Publication Complete"; retries on Notion, Drive and the EU search; persistent quarantine | Workflow JSON parse (risk R7) | 1 d |
| 7 | Wire the hard gates into Stage 2's output path, so dead tenders never reach Stages 3–9 | Evaluation: 7 of 14 advanced were not biddable | 0.5 d |
| 8 | Run the LangSmith experiments with an API key; add adversarial cases for the LLM stages | `evaluation/langsmith.md` | 1 d |
| 9 | Label the retrieval backend (`pinecone` or `local`) in every Stage 5 output | Live-run sample showed `backend: local` | 0.5 d |

**About 10 working days plus the DPA lead time.** Gate 0 passes when items 1–3 and 5–9 are done and the DPAs are at least signed for the providers used in the pilot.

## 3. Pilot

### 3.1 Scope

| Dimension | In scope | Out of scope |
|---|---|---|
| Client | One mid-size energy engineering or advisory firm that already bids on EU service tenders (the Round 1 scenario) | More than one client; any public buyer |
| Duration | 3 months: month 1 baseline and calibration, months 2–3 normal operation | — |
| Volume | Up to 25 deep assessments a month; one Stage 10 portfolio run a week | Unlimited batch runs |
| Sources | EU Funding & Tenders Portal (tenders and calls) | TED and national portals (full-deployment backlog) |
| Outputs | Decisions, portfolio, reports, draft proposal outlines | Proposal drafting beyond outlines; any submission to a portal |
| People | Client bid manager (user), managing director (approver), i@work (operator) | Scoring or selecting any named person |
| Data | Public tender data; client company profile; bid outcomes the client chooses to share | Client HR data; CVs of client staff |

### 3.2 Success criteria (decided at Gate 1)

| # | Criterion | Target | How it is measured |
|---:|---|---|---|
| S1 | Hours saved on screening and qualification, measured against the month-1 baseline | **≥ 22 h/month** in months 2–3 (the level at which time savings alone cover the running cost) | Time log kept by the bid manager in month 1, compared with months 2–3 |
| S2 | Recommendations on non-biddable records (deadline passed, prior-information notice, closed) | **0** | Weekly audit of every BID / CONDITIONAL_BID |
| S3 | Runs that complete without a pipeline error | **≥ 95%** | n8n execution history |
| S4 | Approvals with a recorded rationale | **100%** | Stage 10 approval records |
| S5 | Bid outcomes recorded (win, loss, withdrawn) for calibration | **≥ 5** (outcomes may arrive after the pilot ends) | Outcome log |
| S6 | Bid manager's rating of usefulness | **≥ 4 / 5** | Survey at the end of month 3 |
| S7 | GDPR and AI Act pre-conditions in place | All pre-pilot items closed | Compliance checklist |

**Decision rule.** Continue to full deployment if S1–S4 and S7 are met. Extend the pilot by one month if S1 is between 15 and 22 hours. Stop if S1 is below 15 hours, or if S2 is not met after one fix cycle.

### 3.3 Pilot KPIs (tracked monthly)

| KPI | Definition | Initial target |
|---|---|---|
| Coverage | Listings screened per month | 2–3× the client's manual baseline |
| Gate-failure share | Advanced tenders rejected by hard gates / advanced | Falls below 25% once the gates sit in Stage 2 |
| Decision mix | Share of BID / CONDITIONAL_BID / NO_BID | Monitored, no target |
| Override rate | Approver decisions that differ from the recommendation | Below 40%; above that, review the assumptions |
| Profile divergence | Tenders selected under Checkpoint 1 assumptions but not under the conservative profile | Reported every run |
| Unit cost | LLM + infrastructure cost per completed assessment | ≤ EUR 0.80 LLM; recorded per run |
| Latency | Discovery to approved recommendation | ≤ 2 working days |
| Reliability | Successful runs / scheduled runs | ≥ 95% |

## 4. Full deployment

| Phase | Window | Milestones |
|---|---|---|
| Productise | Mar – Jun 2027 | Multi-client configuration (one company profile and namespace per client); lightweight UI (portfolio dashboard, approval inbox); calibrated win-probability model from pilot outcomes; TED source connector |
| Scale | Jul – Dec 2027 | 3–5 paying clients; CORDIS cross-referencing for competitor and consortium intelligence; LLM proposal-outline enrichment (Agent 11) behind the deterministic skeleton |
| Re-classification check | Before 2 Dec 2027 | AI Act Annex III obligations apply from this date (Digital Omnibus). Confirm that no person-level feature has entered the scope |

**Deployment requirements.**

* **Infrastructure:** EU-hosted n8n (queue mode), FastAPI behind HTTPS with an authenticated webhook, Pinecone index in an EU region where offered, daily backups, uptime monitoring.
* **Security:** secrets in a manager, never in the repository; least-privilege API keys per client; secret scanning and dependency audit in CI; credential rotation every 90 days.
* **Quality:** CI running lint, tests and the offline evaluation on every change; LangSmith experiment re-run on every engine version; release tags with a changelog.
* **Compliance:** DPAs per provider; Article 30 record; privacy notice; breach procedure; Article 50(2) marking; AI literacy records per user.
* **Operations:** runbook (restart, re-run a stage, quarantine handling, data-subject requests); second maintainer trained; incident log.

## 5. Stakeholder communications

| Stakeholder | Interest | What they get | Channel and cadence |
|---|---|---|---|
| Client managing director (sponsor and approver) | Return on bid spend; no embarrassing bids | Monthly one-page pilot report: hours saved, decisions, KPIs, risks | Meeting, monthly |
| Client bid manager (user) | Less screening; better shortlists | Weekly portfolio recommendation; Slack alerts; training session | Slack, weekly; training in week 1 |
| Client DPO or legal counsel | Lawful processing; AI Act position | `gdpr_documentation.md`, `eu_ai_act_compliance.md`, DPIA, DPAs | Review before the pilot; again at Gate 1 |
| Client IT | Access, security, integration | Deployment requirements; credential and access list | Kick-off; on change |
| i@work (operator) | Reliability; commercial case | KPI dashboard; incident log | Weekly review |
| Course instructor and evaluators | Requirements met, honestly evidenced | Final presentation, repository, evaluation | 10 Oct 2026 |

**Key messages, used consistently:** the system recommends, a person decides; it never submits a bid; every number shows its range and its assumptions; it has known limits, and the pilot is designed to measure them.

## 6. Go-to-market

| Element | Choice | Reason |
|---|---|---|
| Target segment | Energy engineering and advisory firms with roughly 20–250 staff that bid on EU service tenders, starting in Germany, Belgium and the Netherlands | Large enough to bid regularly, too small for a dedicated bid-intelligence team; matches i@work's network and the company-profile countries |
| Problem statement | "We cannot read every EU energy notice, and we lose money on bids we should never have started." | Both halves are evidenced: coverage (25 listings in one batch), and the 7 of 14 non-biddable records |
| Positioning | A decision engine with an audit trail, not a chatbot: ranges instead of single scores, a human approval step, and a compliance pack | Differentiates from generic tender-alert services, which notify but do not decide |
| Channels | Founder-led sales through i@work's network; energy associations and agency networks (for example, ManagEnergy participants); a demo at the graduation showcase; LinkedIn case study after the pilot | Low cost; trust-based purchase |
| Proof | The pilot report, with measured hours and decision accuracy | Replaces the assumptions in `roi_risk_assessment.md` with measurements |

## 7. Commercialisation model

| Item | Price | Basis |
|---|---|---|
| Setup and calibration | EUR 10,800 one-off (12 days × EUR 900) | Same as the ROI model's base case |
| Managed service | EUR 1,200 per month: hosting operations, updates, monthly calibration review, support | ROI model base case |
| Pass-through | Infrastructure and LLM usage at cost (about EUR 130 a month at pilot volume) | Transparent; the LLM share is about EUR 10 a month |
| Pilot | Setup fee discounted 50%, three-month term, exit allowed at Gate 1 | Lowers the barrier; aligns price with proven value |

**i@work unit economics (per client, planning assumptions):** EUR 14,400 a year in service revenue against about half a consultant day a month in support (EUR 5,400 a year at EUR 900 a day), a contribution of roughly **EUR 9,000 a year per client**, plus the setup margin. Three clients cover a meaningful share of i@work's consulting capacity; five justify a second maintainer. These figures are targets for the pilot to test, not forecasts.

**Client side:** see `roi_risk_assessment.md`. Base-case break-even in month 7 on operational benefits alone; P10–P90 12-month ROI +27% to +145%; −94% if every assumption is at its worst.

## 8. Decision requested on 10 October 2026

Approve moving from POC to the pre-pilot hardening list (§2), then to a three-month paid pilot with one client firm, under the success criteria in §3.2. Full deployment is decided at Gate 1, on measured results.
