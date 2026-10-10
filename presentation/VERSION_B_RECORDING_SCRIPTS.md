# Version B: recording scripts

Version B: film → Checkpoint 1 (all 19 slides, re-recorded short) → the agents' scene → Checkpoint 2 (live or recorded) → end card.
Target 14:02 for a 15-minute slot.

## How to record

1. Use QuickTime Player (File → New Audio Recording) or Voice Memos. One file per block below, named exactly as listed, saved as `.m4a`.
2. Speak at a calm pace and leave half a second of silence at the start and end. A take may run a few seconds over or under: the deck moves on when each recording ends, so nothing needs re-timing.
3. Put the files in the deck's `media-final/voice/` folder (the installer creates it). Slides without a recording show the script as captions and advance on the target time, so you can rehearse before recording.
4. Checkpoint 2 can be recorded the same way (`c2-…` files), or you present it live: choose with `--c2 live` or `--c2 recorded` when installing, or `?c2=live` in the address bar.

## Checkpoint 1: 19 slides, all kept

The slide visuals and evidence clips stay exactly as they are on eu-tender-presentation.firebaseapp.com; only the narration is shorter. It was 20:39 at normal speed and 14:44 at the deck's 15-minute pace.

| File | Slide or scene | Target | Words | At a calm pace |
|---|---|---:|---:|---:|
| `c1-01.m4a` | EU Tender Autonomous AI Agent | 22 s | 59 | 24 s |
| `c1-02.m4a` | Five development phases | 16 s | 31 | 12 s |
| `c1-03.m4a` | The decision problem | 20 s | 48 | 19 s |
| `c1-04.m4a` | Hybrid architecture | 26 s | 59 | 24 s |
| `c1-05.m4a` | LangGraph state machine | 18 s | 46 | 18 s |
| `c1-06.m4a` | Implementation evidence | 16 s | 31 | 12 s |
| `c1-07.m4a` | Nine stages, nine agents | 14 s | 30 | 12 s |
| `c1-08.m4a` | Intake and early research | 20 s | 42 | 17 s |
| `c1-09.m4a` | Reasoning progression | 20 s | 43 | 17 s |
| `c1-10.m4a` | Full autonomous run | 36 s | 82 | 33 s |
| `c1-11.m4a` | Orchestration evidence | 16 s | 39 | 16 s |
| `c1-12.m4a` | Trigger and knowledge layer | 14 s | 26 | 10 s |
| `c1-13.m4a` | Report publication | 12 s | 25 | 10 s |
| `c1-14.m4a` | Operational visibility | 12 s | 21 | 8 s |
| `c1-15.m4a` | Delivery receipts | 10 s | 22 | 9 s |
| `c1-16.m4a` | Hurdles and problem solving | 26 s | 60 | 24 s |
| `c1-17.m4a` | Cost and token assessment | 22 s | 48 | 19 s |
| `c1-18.m4a` | Achievements and requirements | 20 s | 42 | 17 s |
| `c1-19.m4a` | Checkpoint 1 complete | 12 s | 27 | 11 s |
| | **Total** | **5:52** | | |

**c1-01 · EU Tender Autonomous AI Agent** (22 s)
Hello everyone. I am Dr.-Ing. Walid Barakat from Bonn, and my company, i@work, builds AI energy systems for the EU market. This is the EU Tender Autonomous AI Agent. Finding a tender is easy. Deciding whether to invest in a bid is hard: it combines eligibility, capability, finance, risk and strategic fit. That decision is what this system automates.

**c1-02 · Five development phases** (16 s)
The project ran in five phases: research and scope, RAG, LangGraph agent design, n8n integration, and final polish. Trello tracked it as a delivery plan tied to requirements, tests and corrections.

**c1-03 · The decision problem** (20 s)
The system solves one decision in four steps. Discover finds current opportunities from the official EU source. Understand acquires details, documents and comparable evidence. Assess tests eligibility, capability, cost, margin and risk. Decide publishes an auditable recommendation. One human stays above the graph: I approve any real submission.

**c1-04 · Hybrid architecture** (26 s)
The architecture is hybrid. n8n runs the operation: a schedule or webhook triggers the EU search, and early validation and triage reject weak records before any paid reasoning. FastAPI is the typed boundary to Python. LangGraph owns state and routing, ReAct chooses evidence tools, and Pinecone grounds the assessment. Reports and receipts return to Notion, Slack and Google Drive.

**c1-05 · LangGraph state machine** (18 s)
The state machine starts with validation, so bad input fails early. Evidence is gathered before scoring, so decisions rest on tender content, not model memory. Each specialist writes structured results into shared state, and the last stages turn that state into a decision and a report.

**c1-06 · Implementation evidence** (16 s)
This is the working code: a Python package with an API boundary, state models, agent functions, tools, reports and tests. The GitHub repository adds setup, notebooks, workflow exports, diagrams and documentation.

**c1-07 · Nine stages, nine agents** (14 s)
Nine stages, nine bounded agent functions, not nine chatbots. Each has an explicit input and output contract, so failures stay isolated and evidence carries forward. You will meet them shortly.

**c1-08 · Intake and early research** (20 s)
Agent one validates source records before anything else runs. Then the ReAct researcher chooses the next evidence tool, document intelligence structures the attachments, and retrieval returns relevant passages from Pinecone. Evidence is added step by step, not pushed into one expensive prompt.

**c1-09 · Reasoning progression** (20 s)
Each stage receives structured state and returns evidence or a labelled fallback. Eligibility is a hard gate. Feasibility, finance and risk add scored analysis, and strategy produces BID, CONDITIONAL BID or NO BID, with conditions. A weak-evidence warning stays attached to its stage.

**c1-10 · Full autonomous run** (36 s)
This is one complete autonomous run, recorded end to end. It starts with the trigger and intake, passes validation and relevance, enters the Python reasoning workflow, and finishes with the decision and its delivery. Twenty-five official opportunities were found. Fourteen passed the relevance gate and completed the full path; eleven were archived before any expensive evidence work. The recording shows the contracts holding: n8n passes structured data to the API, LangGraph advances state, evidence is retrieved, and the report returns for publication.

**c1-11 · Orchestration evidence** (16 s)
Here n8n shows an executed workflow, not a diagram: green nodes and item counts show where records advanced or were archived. Live mode confirms the FastAPI boundary, so any failure can be traced to a run and a stage.

**c1-12 · Trigger and knowledge layer** (14 s)
The webhook is a second entry point into the same controlled pipeline. Pinecone stores and retrieves document vectors, so the analysis stays grounded in controlled evidence.

**c1-13 · Report publication** (12 s)
A decision is not complete until it is delivered. The report carries the recommendation, evidence, scores, risks and next action, and lands in Google Drive.

**c1-14 · Operational visibility** (12 s)
Notion is the decision radar: opportunities, decisions, confidence and status in one place. Slack sends the time-sensitive alerts to the team.

**c1-15 · Delivery receipts** (10 s)
These are the receipts: the tender in the radar, the report in Drive, the alert in Slack. Analysis alone is not delivery.

**c1-16 · Hurdles and problem solving** (26 s)
Getting here took repeated problem solving. Source access moved from the human portal to the official EU Search API. Credentials moved to the HTTP boundary. n8n exposed practical errors: Notion properties that did not match, changing node references, and conditions arriving as strings instead of booleans. The answer was layered: validation, typed conversion, bounded retries, labelled fallbacks and publication receipts.

**c1-17 · Cost and token assessment** (22 s)
Development cost was measured, not estimated: 125 dollars and 7 cents of language-model spend across 25.76 million tokens, from mid-July to mid-August 2026. Pinecone, Slack and Notion stayed on free tiers. That is the cost of building; the cost per report must be measured on clean production runs.

**c1-18 · Achievements and requirements** (20 s)
The submission links every required capability to evidence: a repository with setup, source, tests, notebook, diagrams and example reports; a Python layer with ReAct, LangGraph, Pinecone RAG, MCP tools and error handling; and an n8n layer with triggers, orchestration, retries and monitoring.

**c1-19 · Checkpoint 1 complete** (12 s)
Checkpoint 1 is a working autonomous prototype that turns official EU tender data into evidence-led decisions and delivers them. Now meet the agents that do the work.

## Checkpoint 2: 11 scenes, live or recorded

| File | Slide or scene | Target | Words | At a calm pace |
|---|---|---:|---:|---:|
| `c2-01.m4a` | What the data showed | 30 s | 63 | 25 s |
| `c2-02.m4a` | Each bid is a distribution | 30 s | 55 | 22 s |
| `c2-03.m4a` | Choose the portfolio | 30 s | 47 | 19 s |
| `c2-04.m4a` | The portfolio console | 70 s | 99 | 40 s |
| `c2-05.m4a` | Evaluation in LangSmith | 35 s | 53 | 21 s |
| `c2-06.m4a` | ROI and cost | 35 s | 65 | 26 s |
| `c2-07.m4a` | Major risks | 20 s | 29 | 12 s |
| `c2-08.m4a` | EU AI Act | 35 s | 61 | 24 s |
| `c2-09.m4a` | GDPR | 20 s | 42 | 17 s |
| `c2-10.m4a` | Go to market | 25 s | 48 | 19 s |
| `c2-11.m4a` | Recommendation | 15 s | 34 | 14 s |
| | **Total** | **5:45** | | |

**c2-01 · What the data showed** (30 s)
The system worked as designed, and its own data showed what was missing. The relevance agent scored these seven tenders four or five out of five, and it was right about relevance. But five deadlines had already passed and two were prior-information notices. Checkpoint 1 recommended conditional bids on four of them and crashed on two. That is why I built Agent 10.

**c2-02 · Each bid is a distribution** (30 s)
Agent 10 simulates four thousand outcomes for every bid. Blue uses the Checkpoint 1 assumptions; orange is a conservative profile with half the win chance and an eighteen percent margin target. On blue, every eligible tender looks profitable. On orange, only four do. There is no win-loss history yet, so the engine always shows both.

**c2-03 · Choose the portfolio** (30 s)
Bids compete for the same budget, the same people in the same weeks, and the same delivery capacity. The optimiser checks all 127 possible portfolios exactly. Bidding on everything breaks the budget. One tender is selected under both profiles: that is the bid I would defend today.

**c2-04 · The portfolio console** (70 s)
This is the lightweight interface on the same four thousand scenarios as the Python engine. Seven of the fourteen tenders fail a hard gate, each with its reason. The optimiser selects four bids. Switch to the conservative profile, and four bids become one. Back on the first profile, raise risk aversion to four: the selection changes, because the bad tail now weighs more. Open a tender to see its reasons, conditions and a draft proposal outline. Finally, the bid authority approves with a written rationale. In n8n, that approval resumes the Stage 10 workflow. Nothing is ever submitted automatically.

**c2-05 · Evaluation in LangSmith** (35 s)
Both systems ran on the same twenty-three examples with the same evaluators. On the key test, rejecting tenders that cannot be bid on, Checkpoint 1 scores 0.2 and Checkpoint 2 scores 1.0. Two failures are fixed, one is confirmed and scheduled, and three questions remain open. Each has a place in the pilot.

**c2-06 · ROI and cost** (35 s)
For a client firm, the base case breaks even in month seven: plus sixty-five percent in year one and plus one hundred sixty-one over three years, on operational benefits alone. Across twenty thousand simulated assumption sets, first-year ROI sits between plus twenty-seven and plus one hundred forty-five percent. If every assumption lands at its worst, it never pays back, so the pilot measures hours first.

**c2-07 · Major risks** (20 s)
Twelve risks are registered. Two already happened in this project: closed tenders were recommended, and credentials ended up in a shared archive. The top open risk is uncalibrated assumptions.

**c2-08 · EU AI Act** (35 s)
Under the AI Act this is an AI system, not prohibited and not high-risk: it is not a safety component of energy infrastructure, it scores no person, and procurement is not an Annex III area. Two duties bind: AI literacy, and machine-readable marking of AI-generated content. Matching named experts to roles would change the classification, so it is out of scope.

**c2-09 · GDPR** (20 s)
GDPR applies because notices and annexes name real people. The basis is legitimate interests, with a DPIA before the pilot. The fix is mostly engineering: strip personal data before model calls, sign processor agreements, and delete each tender's vectors when it closes.

**c2-10 · Go to market** (25 s)
Ten days of hardening, then a three-month paid pilot with one energy engineering firm. It succeeds if it saves at least twenty-two hours a month and recommends no closed tenders. Commercially it is a managed service: about eleven thousand euros to set up and twelve hundred a month.

**c2-11 · Recommendation** (15 s)
So, should we proceed? Yes, to a three-month pilot, under four conditions: measure the manual workload first, record every bid outcome, close the data-protection pre-conditions, and keep a human approving every portfolio. Thank you.
