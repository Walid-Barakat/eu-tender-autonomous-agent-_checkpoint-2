# ROI and Risk Assessment — Tender Intelligence Agent

**Phases 13 and 14** · Checkpoint 2 · prepared 7 October 2026
**Decision this document supports:** should a mid-size energy engineering firm that bids on EU tenders adopt the Tender Intelligence Agent as a managed service from i@work, and under what conditions?
**Model:** `analysis/roi_model.py` (run it to regenerate every number here; results in `analysis/roi_results.json`)

> **Bottom line.** On operational benefits alone (time saved and wasted bid costs avoided), the base case pays back in **month 7**, with a **12-month ROI of +65%** and a **36-month ROI of +161%**. A Monte Carlo over every assumption gives a 12-month ROI between **+27% and +145%** (10th–90th percentile), and a **1.6%** chance that the 12-month ROI is negative. If every assumption lands at its worst end at the same time, the tool **never pays back (−94% at 12 months)**. That case occurs when the firm qualifies few tenders by hand today, so there is little manual work to replace. The pilot must therefore measure the firm's current manual hours before anything else.

---

## 1. Who pays, who benefits

| Party | Role in this ROI |
|---|---|
| Client firm | Pays the setup and monthly service fee; receives the time savings and better bid selection. Modelled on the project's company profile: EUR 12M revenue, EUR 450k annual bid budget, EUR 8M single-bid ceiling |
| i@work | Provides configuration, hosting, calibration and support as a managed service. Its own business case is in `strategic_plan.md` |

## 2. Formula and method

```text
ROI = (Benefit − Cost) / Cost × 100          cumulative, from month 0 to the horizon
Break-even = first month in which cumulative benefit ≥ cumulative cost
```

* Month 0 carries the upfront cost. Months 1–3 are the pilot calibration period, during which benefits are counted at **50%**.
* Benefits are split by strength of evidence:
  * **Tier A, operational** — screening and qualification time saved, and bid cost not wasted on no-go bids. This is the headline ROI.
  * **Tier B, outcome** — additional positive-expected-value bids found because the agent covers two to three times more tenders. Reported separately, because it rests on the engine's win-probability model, which is not yet calibrated.
* Three deterministic scenarios (pessimistic, base, optimistic) plus a 20,000-draw Monte Carlo with triangular distributions over each assumption range (seed 20261010).

## 3. Assumptions

Every number below is an assumption with a stated basis, not a measurement, unless the basis says otherwise.

| Assumption | Low | Base | High | Basis |
|---|---:|---:|---:|---|
| i@work setup effort (days) | 8 | 12 | 18 | Configuration: company profile, capability corpus, n8n hosting, Notion/Slack, calibration data |
| Consultant day rate (EUR) | 800 | 900 | 1,100 | Planning range for independent energy/AI consulting in Germany |
| Client onboarding (hours) | 24 | 40 | 64 | Workshops, data supply, acceptance testing |
| Client internal cost (EUR/hour) | 60 | 75 | 95 | Fully loaded bid/technical consultant |
| Service fee (EUR/month) | 900 | 1,200 | 1,600 | i@work managed-service price (see strategic plan) |
| Hosting and tooling (EUR/month) | 60 | 120 | 250 | n8n hosting, Pinecone starter, monitoring |
| LLM cost per assessment (EUR) | 0.18 | 0.40 | 0.80 | Checkpoint 1 green-software assessment: USD 0.20–0.45; the high case doubles it for retries |
| Deep assessments per month | 15 | 25 | 35 | Live run: 14 of 25 listings advanced in a single batch |
| Listings screened per month | 40 | 60 | 90 | 25 energy listings in one batch on 12 Aug 2026 |
| Manual screening (minutes/listing) | 6 | 10 | 15 | Title, scope, deadline and value on the portal |
| Tenders qualified by hand per month | 6 | 10 | 14 | Fewer than the agent covers |
| Manual qualification (hours/tender) | 4 | 6 | 10 | Specifications, eligibility, rough price, go/no-go memo |
| Review per automated assessment (hours) | 0.25 | 0.40 | 0.75 | Human review of the agent's output |
| Portfolio approval (hours/month) | 2 | 3 | 5 | Stage 10 approval step |
| Freed time actually redeployed | 60% | 80% | 95% | Time saved is a benefit only if it is used |
| No-go bids avoided per year | 1 | 2 | 4 | Bids started, then abandoned or lost on an issue the agent flags at the gate |
| Average bid cost (EUR) | 10,000 | 15,000 | 25,000 | Engine bid-cost medians on the live run: EUR 8k–49.5k |
| Share of bid cost already spent when the problem is found by hand | 30% | 50% | 80% | — |
| *Tier B:* extra selected bids per year | 0 | 4 | 8 | Wider coverage |
| *Tier B:* expected profit per selected bid (EUR) | 0 | 13,500 | 40,000 | Engine output: EUR 13.5k for the one bid selected under the conservative profile |

**Measured inputs, for contrast:** the development spend of USD 125.07 (25.76M tokens, mid-July to mid-August 2026) is a sunk cost of building Checkpoint 1, not a client cost, and is excluded. Per-assessment token use has not been measured on clean production runs. Telemetry is a pilot deliverable.

## 4. Results

### 4.1 Costs

| | Pessimistic | **Base** | Optimistic |
|---|---:|---:|---:|
| Upfront (setup + onboarding) | EUR 24,600 | **EUR 13,800** | EUR 8,200 |
| Running cost per month | EUR 1,878 | **EUR 1,330** | EUR 963 |
| Cost over 12 months | EUR 47,136 | **EUR 29,760** | EUR 19,752 |
| Cost over 36 months | EUR 92,208 | **EUR 61,680** | EUR 42,857 |

The LLM bill is the smallest line: 25 assessments × EUR 0.40 = **EUR 10 a month**. Almost all of the running cost is the service fee, which is a commercial choice, not a technical cost.

### 4.2 Benefits, ROI and break-even

| | Pessimistic | **Base** | Optimistic |
|---|---:|---:|---:|
| Manual hours per month today | 28.0 | **70.0** | 162.5 |
| Hours per month with the agent | 31.2 | **13.0** | 5.8 |
| Hours saved per month | 0 | **57.0** | 156.8 |
| Tier A benefit per month | EUR 250 | **EUR 4,670** | EUR 17,835 |
| **12-month ROI (Tier A)** | −94.4% | **+64.8%** | +848.1% |
| **36-month ROI (Tier A)** | −90.6% | **+161.2%** | +1,335.7% |
| **Break-even month (Tier A)** | never | **month 7** | month 2 |
| Expected value over 36 months (Tier A, net) | −EUR 83,583 | **+EUR 99,435** | +EUR 572,454 |
| 12-month ROI including Tier B | −94.4% | +223.5% | +2,265.6% |
| 36-month ROI including Tier B | −90.6% | +412.9% | +3,482.4% |
| Break-even including Tier B | never | month 4 | month 1 |

**Base case, cumulative net position (Tier A):** −EUR 13,800 at month 0 · −EUR 10,785 at month 3 · −EUR 765 at month 6 · +EUR 9,255 at month 9 · +EUR 19,275 at month 12 · +EUR 59,355 at month 24 · +EUR 99,435 at month 36.

### 4.3 Uncertainty: Monte Carlo over all assumptions

| Metric (Tier A unless stated) | P10 | P50 | P90 |
|---|---:|---:|---:|
| 12-month ROI | +26.7% | +78.1% | +145.2% |
| 36-month ROI | +102.8% | +185.4% | +292.8% |
| 36-month ROI including Tier B | +254.0% | +473.1% | +820.1% |
| Break-even month | 5 | 6 | 9 |
| **Probability that the 12-month ROI is negative** | | **1.6%** | |
| Probability that the 36-month ROI is negative | | 0.0% | |

The Monte Carlo median (+78%) is above the base case (+65%) because several ranges are skewed upward; for example, manual qualification runs from 4 to 10 hours around a base of 6. The draws are independent. If the pessimistic assumptions tend to occur together (a firm that bids rarely also qualifies few tenders by hand), the real tail is fatter than 1.6%, and the pessimistic corner above shows how far it can go.

### 4.4 What drives the result (36-month ROI, one assumption at a time)

| Assumption | ROI at low | ROI at high | Swing |
|---|---:|---:|---:|
| Manual hours per qualification | +94% | +296% | 201 pts |
| Tenders qualified by hand per month | +81% | +242% | 161 pts |
| Service fee | +217% | +112% | 105 pts |
| No-go bids avoided per year | +126% | +231% | 105 pts |
| Share of freed time redeployed | +113% | +197% | 84 pts |
| Client internal hourly cost | +125% | +208% | 83 pts |

The two largest drivers describe the **client's current manual workload**, not the agent. That is why the pilot's first success criterion is a measured baseline of hours spent today (see `strategic_plan.md`).

### 4.5 What the evidence does and does not support

* **Supported:** the agent covers more tenders per month than manual screening (14 of 25 advanced in one live batch); the LLM cost per assessment is small; the Checkpoint 2 gates reject non-biddable records that Checkpoint 1 would have recommended (`evaluation/langsmith.md`: 10 of 10 against 2 of 10).
* **Not yet supported:** any measured time saving at a real client; the win probabilities behind Tier B. Under the conservative profile the engine selects 1 of 7 eligible live tenders, and bidding on all seven carries about a 51% chance of a net loss. Tier B should not be used to justify the purchase until win/loss data exists.

---

## 5. Risk assessment

Likelihood and impact are scored 1 (low) to 5 (high). "Observed" means the risk has already occurred in this project's own evidence.

| # | Risk | Category | Likelihood | Impact | Score | Mitigation | Status |
|---:|---|---|:---:|:---:|:---:|---|---|
| R1 | Non-biddable records (deadline passed, prior-information notices) reach analysis and are recommended | Technical | 5 *(observed: 7 of 14 in the live run; Checkpoint 1 recommended 4)* | 4 | **20** | Hard gates with an explicit assessment date; fail closed on unparseable dates; monitor the gate-failure share | Mitigated in Checkpoint 2 (10/10 rejected in evaluation); monitoring is a pilot item |
| R2 | Uncalibrated win-probability and margin assumptions drive the wrong portfolio | Technical / financial | 4 | 4 | **16** | Run both profiles on every decision; show ranges, not a single number; record every bid outcome; recalibrate after 10 bids | Open: no outcome data exists |
| R3 | Personal data in tender files, CVs and contact details flows to non-EU LLM and vector providers without executed processor agreements | Regulatory (GDPR) | 3 | 4 | **12** | Article 28 DPAs; EU regions where available; strip names and emails before LLM and Pinecone calls; retention schedule (`gdpr_documentation.md`) | Open: 7 of 10 accountability items missing or untested |
| R4 | Instructions hidden in tender documents steer the LLM stages (prompt injection) | Technical / security | 3 | 4 | **12** | The decision layer is deterministic and was shown to be unaffected by injected text; tools only fetch from ec.europa.eu; add adversarial cases for the LLM stages in LangSmith | Partly mitigated: the LLM stages are not yet tested |
| R5 | The bid authority approves the engine's output without scrutiny; Monte Carlo figures read as more precise than they are | Ethical | 3 | 4 | **12** | Approval requires a recorded rationale; overrides are logged and reviewed; both profiles and a "what would change this" note shown on every recommendation | Approval gate built in Stage 10; rationale field is a pilot item |
| R6 | Feature drift into person-level scoring (ranking experts or staff for proposals) moves the system into an EU AI Act Annex III high-risk category | Regulatory (AI Act) | 2 | 5 | **10** | Scope lock: no scoring of natural persons; any such feature triggers a new classification before release (`eu_ai_act_compliance.md`) | Controlled by scope |
| R7 | Publication silently fails: the completion marker fires in parallel with Notion and Slack, and terminal writes have no retry | Operational | 3 *(verified in workflow JSON)* | 3 | **9** | Merge node before "Publication Complete"; bounded retries on Notion, Drive and the EU search; persistent quarantine instead of no-op sinks | Open in the Stage 9 workflow; the Stage 10 workflow has retries and an explicit failure route |
| R8 | Credentials exposed through a shipped archive | Operational / security | 3 *(observed: .env in a submitted ZIP)* | 4 | **12** | Rotate keys; release with `git archive`; secret scanning in CI | Rotation to be confirmed by the owner |
| R9 | Key-person and hosting fragility: one developer, temporary tunnels, one inactive workflow | Operational | 4 | 3 | **12** | Stable HTTPS hosting; runbook; CI; second maintainer during the pilot | Open |
| R10 | The firm wins more than it can deliver, harming the contracting authority and its own reputation | Ethical / operational | 2 | 4 | **8** | Chance constraint in the optimiser: probability of exceeding delivery capacity ≤ 10% (bid-everything gives 21.5% under Checkpoint 1 assumptions) | Mitigated in the engine |
| R11 | The EU Search API changes its undocumented multipart contract | Technical | 3 | 4 | **12** | Contract tests on a recorded response; alert when result counts drop to zero; keep the portal fallback documented | Open |
| R12 | Freed time is not redeployed, so the operational benefit is not realised | Commercial | 3 | 3 | **9** | Pilot success criteria measure hours before and after; contract includes an exit after the pilot | Pilot item |

### Risk heat map

| Likelihood ↓ / Impact → | 3 | 4 | 5 |
|---|---|---|---|
| **5** | | R1 | |
| **4** | R9 | R2 | |
| **3** | R7, R12 | R3, R4, R5, R8, R11 | |
| **2** | | R10 | R6 |

No risk is hidden because it is unflattering: R1 and R8 have already happened in this project, and R2 is open by construction until real bids are recorded.

## 6. Recommendation for the decision-maker

**Proceed to a paid three-month pilot, not to full deployment.** The pilot is worth running because the base case pays back in month 7 and the probability of a negative first-year return is low. It is conditional on four things:

1. **Measure the current manual workload in month 1.** The ROI turns on it more than on anything the agent does.
2. **Record every bid outcome**, so the win-probability model can be calibrated. Until it is, decide on the conservative profile.
3. **Close R3 (GDPR) before live documents containing personal data are processed**: processor agreements and PII stripping.
4. **Keep the human approval step** in Stage 10, with a recorded rationale.

The continue threshold is **22 hours saved a month**, measured in months 2–3. That is the point at which time savings alone (22 h × EUR 75 × 80% ≈ EUR 1,320) cover the base-case running cost of EUR 1,330, before counting the less certain avoided-waste benefit. Between 15 and 22 hours, extend the pilot by one month; below 15, stop (decision rule in `strategic_plan.md` §3.2).
