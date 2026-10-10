# EU AI Act Compliance — Tender Intelligence Agent

**Phase 15** · Checkpoint 2 · prepared 7 October 2026 by Dr.-Ing. Walid Barakat, i@work UG
**Status:** first-pass self-assessment for the capstone. It is not a legal opinion or a conformity assessment. Qualified counsel should confirm it before the system is offered commercially.

> **Classification in one line.** An AI system that is **not prohibited and not high-risk** under the current Annex III. Its binding obligations are limited to **AI literacy (Article 4)** and, on a conservative reading, **marking AI-generated report text (Article 50(2))**. The design voluntarily applies the main high-risk controls (human oversight, logging, documented accuracy, robustness testing) because they are cheap here, and because one plausible future feature, matching named experts to proposal roles, could move the system into Annex III.

---

## 1. System description

| Element | Description |
|---|---|
| Name and version | Tender Intelligence Agent: Checkpoint 1 pipeline (Stages 1–9) plus the Checkpoint 2 decision engine `cp2-decision-engine/1.0.0` (Stage 10) |
| Intended purpose | Help a firm decide **which EU energy tenders to bid on**. It discovers tenders on the EU Funding & Tenders Portal, screens relevance, gathers evidence, assesses eligibility, technical fit, finance and risk, simulates the outcome distribution of each bid, and recommends a portfolio of bids within the firm's budget and capacity |
| Users | Bid managers and the managing director of an engineering or advisory firm (the deployer); i@work as provider and operator of the managed service |
| Subjects of the decision | **Organisations**: the firm itself (where to spend its bid budget) and the tenders. No natural person is scored, ranked or selected |
| Outputs | Per tender: BID / CONDITIONAL_BID / NO_BID with reasons, conditions, a profit distribution (P5/P50/P95, probability of loss) and a draft proposal outline. Per run: a recommended bid portfolio and its risk. Delivered as JSON, Markdown/PDF reports, Notion records and Slack messages |
| Decision authority | Recommendations only. Stage 10 waits for explicit approval from the firm's bid authority before anything is recorded as a decision. **Nothing is ever submitted to the EU portal by the system** |
| AI components | (a) LLM relevance triage (Stage 2, Anthropic Claude via n8n); (b) a ReAct evidence-acquisition agent with MCP tools (Stage 3, LangGraph); (c) OpenAI embeddings and Pinecone retrieval (Stages 4–5); (d) LLM-generated summaries in reports |
| Non-AI components | Hard eligibility gates, seeded Monte Carlo simulation, exact portfolio optimisation, report templating, n8n orchestration |
| General-purpose AI models used | Claude (Anthropic) and OpenAI embedding models, through their APIs without modification or fine-tuning |
| Deployment | Self-hosted n8n and FastAPI; third-party model and vector providers (see `gdpr_documentation.md` for regions and transfers) |

## 2. AI Act classification

| Test | Article | Result |
|---|---|---|
| Is it an AI system? | Art. 3(1) | **Yes**, because of the LLM triage, ReAct agent and generated summaries: they operate with some autonomy and infer from inputs how to generate recommendations and content. The deterministic engine on its own (gates, Monte Carlo, optimisation) would probably fall outside the definition, as classic mathematical optimisation and rule-based processing, but the system is assessed as a whole |
| Prohibited practice? | Art. 5 | **No** |
| High-risk via product safety legislation? | Art. 6(1), Annex I | **No**. It is not a safety component of a regulated product |
| High-risk via Annex III use case? | Art. 6(2), Annex III | **No** on the intended purpose (reasoning in §3) |
| Transparency obligations? | Art. 50 | **50(1): No.** It does not converse with natural persons as an interlocutor. **50(2): applies conservatively** to LLM-generated report text. **50(4): No.** Reports are not published to inform the public, and they are human-reviewed |
| General-purpose AI model obligations? | Art. 53–55 | **Not on i@work.** i@work integrates GPAI models as a downstream provider and does not place a GPAI model on the market. The model providers carry those obligations |
| AI literacy | Art. 4 | **Applies** to i@work as provider and to each client as deployer |
| Role of i@work | Art. 3(3), 3(4) | **Provider** when it offers the system to clients under its own name; **provider and deployer** when it uses the system for its own bids |
| Role of a client firm | Art. 3(4), Art. 25 | **Deployer.** It would become a provider if it changed the intended purpose to a high-risk use (Art. 25(1)(c)); the service contract must forbid that |

## 3. Reasoning

**Why it is an AI system.** The Article 3(1) definition turns on inference: generating outputs such as recommendations or content from input, with some autonomy. The Stage 2 triage infers relevance from free text; the ReAct agent decides which tool to call next; report summaries are generated text. Each of these is inference in the Act's sense.

**Why it is not Annex III high-risk.** Annex III lists eight areas. The system was checked against each. Two needed a closer look, because the client works in energy and because proposals involve people:

* **Critical infrastructure (Annex III point 2)** covers AI used as a *safety component* in the management and operation of, among others, the supply of electricity, gas and heating. The agent advises on commercial bids for consulting and engineering services. It does not operate, control or protect any part of an energy system, and its failure cannot cause a physical-safety or supply incident. **Not covered.**
* **Employment and workers' management (Annex III point 4)** covers recruitment and selection of natural persons, and allocating tasks based on individual traits or behaviour. The current system does not process, score or select people. The proposal outline lists *roles*, not named experts. **Not covered today, but this is the main classification risk** (§7).
* Biometrics, education, access to essential private or public services (credit, insurance, public benefits), law enforcement, migration and the administration of justice and democratic processes: **not applicable.**
* **Public procurement is not an Annex III area.** Even on the contracting-authority side, procurement evaluation is not listed. This system is used by bidders in any case.

**Why a human-reviewed internal report is not caught by Article 50(4).** That paragraph concerns AI-generated text *published to inform the public on matters of public interest*, and exempts text that has undergone human review or editorial control under a person's editorial responsibility. The reports are internal business documents, and Stage 10 places them under the bid authority's approval.

**Why Article 50(2) is applied anyway.** Article 50(2) requires providers of AI systems that generate synthetic text to mark outputs in a machine-readable format so they can be detected as AI-generated. Whether this is aimed at internal analytical reports produced partly by templates and partly by an LLM is not settled. Marking costs almost nothing here: a metadata field in the JSON, PDF and Notion record, and a visible label. The conservative reading is therefore adopted.

## 4. Applicable obligations

### 4.1 Binding

| Obligation | Article | Applies from | What the system does |
|---|---|---|---|
| AI literacy: providers and deployers take measures to support sufficient AI literacy of the staff who operate and use the system | Art. 4 (softened by the Digital Omnibus to supporting literacy rather than guaranteeing a level) | 2 Feb 2025 | Onboarding module for the client's bid team covering what the engine models and what it assumes, the two calibration profiles, the known failure modes from the evaluation, and when to override. Completion recorded per user |
| Marking AI-generated text in a machine-readable way (conservative reading) | Art. 50(2) | 2 Aug 2026 (with a grace period to 2 Dec 2026 for systems already on the market) | `ai_generated: true` plus generator and engine version in every JSON report; PDF document metadata; a visible footer "Prepared with an AI system; recommendations require human approval" |
| Not to drift into prohibited practices | Art. 5 | 2 Feb 2025 | No emotion recognition, social scoring or manipulative techniques: none exist in the design, and the scope lock forbids them |
| Respect the providers' usage policies and pass their information downstream | Art. 53 (on GPAI providers) | 2 Aug 2025 | Model and version recorded per run; the providers' acceptable-use terms flow into the client contract |

### 4.2 Voluntary (high-risk-style controls adopted as good practice)

Article 95 encourages voluntary codes of conduct that apply high-risk requirements to other systems. These are adopted because they also fix defects found in this project's own audits.

| Control | Modelled on | Implementation | Evidence |
|---|---|---|---|
| Human oversight before any decision is recorded | Art. 14 | Stage 10 Slack approval and n8n Wait node (48-hour timeout means rejection); nothing is submitted to the portal | `workflows/n8n/stage_10_portfolio_decision_engine.json` |
| Accuracy and robustness, measured and declared | Art. 15 | Evaluation dataset with 23 examples; 7 evaluators; non-biddable records rejected 10 of 10; reproducibility 23 of 23; prompt-injection twin unchanged | `evaluation/langsmith.md` |
| Record-keeping and traceability | Art. 12 | Engine version, assessment date, seed and all assumptions written into every result; n8n execution history; JSONL audit events | Engine output `simulation_config`, `portfolio_config` |
| Risk management | Art. 9 | Twelve-item risk register with owners and status | `roi_risk_assessment.md` §5 |
| Data governance | Art. 10 | Source restricted to official EU portal records; dataset provenance documented; no personal data in the decision engine | `evaluation/build_dataset.py`, `gdpr_documentation.md` |
| Instructions for use and limits | Art. 13 | Deployer guide states the intended purpose, the uncalibrated assumptions, and the prohibited extensions | §6 outline item 2 |
| Post-market monitoring | Art. 72 | Pilot monitoring metrics and alert thresholds | `evaluation/langsmith.md` §7 |

## 5. Conformity summary

| Requirement | Applies? | Status on 7 Oct 2026 | Evidence or gap |
|---|---|---|---|
| Art. 5 prohibited practices | Yes (do not breach) | **Compliant** | No prohibited function in the design |
| Art. 4 AI literacy | Yes | **Partial** | Content defined (§4.1); the training module and the completion record are pilot deliverables |
| Art. 50(2) machine-readable marking | Conservatively yes | **Gap** | Fields are specified here; the report generator does not yet write them. One-day change, due before the pilot |
| Art. 50(1), 50(4) | No | Not applicable | No conversational interface; no public-interest publication |
| Art. 6 / Annex III high-risk obligations | No | Not applicable | Re-classify if the scope changes (§7) |
| GPAI provider duties | No (downstream provider) | Not applicable | Model IDs recorded per run |
| Voluntary human oversight | Adopted | **Implemented** in Stage 10, not yet exercised by a real approver | Stage 10 workflow is generated and structurally verified, not executed |
| Voluntary accuracy and robustness | Adopted | **Implemented** for the decision layer | The LLM stages are not yet covered by adversarial tests (risk R4) |
| Voluntary logging | Adopted | **Partial** | Engine results are fully reproducible; n8n publication branch has a known ordering defect (risk R7) |

**Overall:** low regulatory exposure under the intended purpose. Two actions are needed before a commercial pilot: write the Article 50(2) marking fields, and deliver the Article 4 literacy module.

## 6. Technical documentation outline

Annex IV documentation is mandatory only for high-risk systems. It is kept in this shape anyway, so the system can be re-classified quickly if its scope changes.

1. **General description** — intended purpose, provider (i@work UG), version history (`cp2-decision-engine/1.0.0`, Stage 1–9 workflow export, Stage 10 workflow), hardware and hosting, user interfaces (n8n, Notion, Slack, the portfolio dashboard).
2. **Intended purpose, limits and foreseeable misuse** — organisation-level bid decisions only; no scoring of natural persons; no automatic submission; the win-probability and margin assumptions are uncalibrated; known failure modes from the evaluation.
3. **System elements and design choices** — architecture diagram; why the decision layer is deterministic (reproducibility, injection resistance); the gate list; Monte Carlo configuration and its two calibration profiles; optimiser objective and constraints; the LLM models and prompts used in Stages 2–3.
4. **Data** — source (EU Funding & Tenders Portal Search API); record fields used; evaluation dataset composition and labelling method; the knowledge corpus used for retrieval; data-protection measures (cross-reference to `gdpr_documentation.md`).
5. **Human oversight** — the Stage 10 approval flow; the information shown to the approver; override logging; time-outs.
6. **Accuracy, robustness and cybersecurity** — evaluation metrics and their limits; reproducibility; prompt-injection test; tool allow-list (official EU domains only); secret management; known open defects.
7. **Risk management** — risk register and its review cadence.
8. **Changes over the life cycle** — versioning rule: any change to gates, assumptions or optimiser constraints bumps the engine version and re-runs the evaluation.
9. **Post-market monitoring plan** — pilot metrics and thresholds; incident log; the quarterly re-classification check.
10. **Transparency artefacts** — Article 50(2) marking specification; deployer guide; AI literacy module.

## 7. Remaining uncertainty

| Question | Why it matters | Current position | What would resolve it |
|---|---|---|---|
| Will a staffing feature (matching named experts or CVs to proposal roles) be added? | Ranking people for roles could fall under Annex III point 4, high-risk from **2 Dec 2027**, as set by the Digital Omnibus | Out of scope; the proposal outline lists roles only | A re-classification gate in the product roadmap before any person-level feature |
| Does Article 50(2) cover internal analytical reports? | Determines whether marking is mandatory or voluntary | Applied conservatively | Commission guidelines and the code of practice on marking AI-generated content |
| Is the deterministic engine an AI system on its own? | Matters if it is ever sold separately from the LLM stages | Probably not (optimisation and rule-based processing) | Commission guidelines on the AI system definition |
| Will a client use the system on the contracting-authority side? | Evaluating other companies' bids for a public buyer raises fairness and procurement-law questions, although procurement is not in Annex III | Not offered | Contract clause restricting use to bidders |
| Exact Omnibus text and dates | Two sources consulted differ on adoption status (provisional agreement of 6 May 2026, versus in force from 27 July 2026) | Planning uses 2 Dec 2027 for Annex III and 2 Aug 2026 for Article 50 | Check the Official Journal text before the commercial launch |
| Will i@work fine-tune a model? | Substantial modification could make it a GPAI model provider | Not planned | Re-assess if fine-tuning is introduced |

## Sources

* Regulation (EU) 2024/1689 (AI Act), Articles 3, 4, 5, 6, 25, 50, 53, 95 and Annex III — [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
* Digital Omnibus on AI, postponed high-risk deadlines (Annex III to 2 Dec 2027; Annex I to 2 Aug 2028; Article 50 unchanged; AI literacy softened) — [Gibson Dunn, 2026](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/)
* Omnibus signed 8 July 2026 and in force 27 July 2026; Article 50(2) grace period to 2 Dec 2026 for systems already on the market — [Usercentrics, 2026](https://usercentrics.com/knowledge-hub/eu-ai-act-high-risk-delay-article-50-transparency-consent/)
* European Commission, AI Act regulatory framework overview — [digital-strategy.ec.europa.eu](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
