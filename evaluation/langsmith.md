# Phase 12 — LangSmith Evaluation

**Use case evaluated:** bid / no-bid decisions on EU energy tenders for i@work (final use case after the Round 1 decision gate)
**Dataset:** `eu-tender-decisions-v2`, 23 examples
**Experiments:** two, run on the same dataset with the same evaluators: `checkpoint1-` (the Checkpoint 1 pipeline as delivered) and `checkpoint2-` (the Checkpoint 2 decision engine)
**Evaluators:** 7 row-level, 1 dataset-level summary, plus an optional LLM-as-judge
**Status of the numbers below:** produced by running the identical targets and evaluators locally on 7 October 2026 (`--offline`). The LangSmith upload of the dataset, traces and experiments needs `LANGSMITH_API_KEY` and is the first item in [How to reproduce](#how-to-reproduce-in-langsmith). The LangSmith code path was checked with uploading switched off; it produced the same per-example decisions.

---

## 1. Why the dataset was rebuilt after Round 1

Round 1 pitched a different technical direction (the Grid Connection Pre-Check). The decision gate then brought the project back to the Tender Intelligence Agent as the final build. The brief says to update the evaluation dataset if direction changed, so it was rebuilt around the decision this tool exists to support: **should i@work spend bid budget on this tender?**

The Round 1 evaluation-plan document itself was not among the files supplied for this work. Its test cases are therefore not mapped one by one here; if it is added, its relevant cases can be appended as a further split without changing anything else.

## 2. Dataset

| Split | Examples | What it tests | Where the reference label comes from |
|---|---:|---|---|
| `live_run_2026_08_12` | 14 | The 14 real tenders that passed the Stage 2 relevance gate in the recorded run (25 discovered, 14 advanced) | Read from each record: is the deadline after the discovery date, and is it an open procedure rather than a prior-information notice? |
| `checkpoint1_fixtures` | 3 | Building renovation, AI data centre, laptop purchase | The published Checkpoint 1 reference reports (BID 93.2, BID 96.2, NO_BID 47.9) |
| `edge_cases` | 6 | Missing value, value above the EUR 8M ceiling, deadline "TBC", 5 days to prepare, status "Closed", and a prompt-injection twin of a real record | Constructed; each states the expected behaviour and why |

The 14 live records were copied verbatim from the n8n pinned data in `workflows/n8n/EU Tender Stage 1-9 WebHook  GTEWAY - Receiver Node Patch.json` into `data/live_run_2026_08_12/stage2_advanced_tenders.json`. No values were edited.

**What the real data showed before any system was run:** of the 14 tenders the relevance gate advanced, **7 could not be bid on** on the discovery date. Five had deadlines between November 2024 and March 2026, yet still carried the status "Open for submission" or "Forthcoming", and two were prior-information notices whose deadline field uses a different date format (`14/07/2026`). The Stage 2 LLM triage scored all seven at relevance 4 or 5 with confidence 0.75–0.95. Relevance was judged correctly. Whether a bid was still possible was never checked.

## 3. Systems under test

| Target | What runs | Controlled changes for evaluation |
|---|---|---|
| `checkpoint1_pipeline` | The unmodified Checkpoint 1 assessment (`offline_workflow.assess_tender`) | The portal fetch returns nothing because the record already holds the Stage 2 payload, and the clock is frozen at the example's `as_of` date so the deadline logic sees the same "today" as the live run |
| `checkpoint2_engine` | The Checkpoint 2 decision engine on the single tender: hard gates, seeded Monte Carlo (2,000 scenarios), and the portfolio rule | None |

Both targets are wrapped with `@traceable`, so each example produces one trace per experiment in LangSmith.

## 4. Evaluators

| Evaluator | Question it answers | Applies to |
|---|---|---|
| `completed_without_error` | Did the system return a decision at all? | All 23 |
| `non_biddable_rejected` | Does it say NO_BID when the tender cannot be bid on? | 10 non-biddable |
| `reference_decision_match` | Does the decision match the reference? Same direction but different class (BID vs CONDITIONAL_BID) scores 0.5 | 13 with a reference decision |
| `flags_required_condition` | Is the known weakness (missing value, short window) stated? Matched by meaning with a regular expression, so neither system's wording is favoured | 2 |
| `decision_consistent_with_value` | Is there no positive recommendation with a non-positive expected value? | Where a value exists |
| `reproducible` | Does re-running give the identical decision and value? | All 23 |
| `injection_invariant` | Does an injected instruction in the tender text change the decision? | The injected twin |
| Summary metrics | Share of recommendations on biddable records; share of non-biddable records rejected | Dataset |
| `llm_grounding_judge` (optional, `--judge`) | Does the output contradict the record, or recommend a dead tender? | All, when `ANTHROPIC_API_KEY` is set |

One evaluator was corrected during this work: its first version matched exact phrases taken from the Checkpoint 2 engine's own messages, which scored Checkpoint 1 at 0 for saying the same thing in different words. It now matches meaning, and Checkpoint 1 scores 1.0 on it.

## 5. Results

| Evaluator | Checkpoint 1 | Checkpoint 2 |
|---|---|---|
| completed_without_error | **0.83** (19 of 23) | 1.00 (23 of 23) |
| non_biddable_rejected | **0.20** (2 of 10) | 1.00 (10 of 10) |
| reference_decision_match | **0.39** | 0.92 |
| flags_required_condition | 1.00 | 1.00 |
| decision_consistent_with_value | 1.00 | 1.00 |
| reproducible | 1.00 | 1.00 |
| injection_invariant | 1.00 | 1.00 |

| Summary metric | Checkpoint 1 | Checkpoint 2 |
|---|---|---|
| Recommendations that were on biddable records | **0.75** (12 of 16) | 1.00 (12 of 12) |
| Non-biddable records correctly rejected | **0.20** | 1.00 |

Full per-example table: `evaluation/results/offline_experiment.md`. Raw results: `evaluation/results/offline_experiment.json`.

## 6. What failed, and why

**Checkpoint 1 recommended bids on four tenders whose deadlines had already passed** (by 135, 217, 237 and 637 days). Why: its eligibility check trusts the status *string* ("Open for submission") and never compares the deadline with the date. The deadline logic exists, but only as a risk flag, so a dead tender is downgraded to CONDITIONAL_BID instead of rejected. The same logic used `datetime.now()`, so the same tender would have produced different answers on different days. The engine now takes an explicit assessment date, and a past deadline is a hard gate.

**Checkpoint 1 crashed on 4 of 23 records.** Two prior-information notices use `dd/mm/yyyy` deadlines, which `datetime.fromisoformat` rejects. One record has the deadline "TBC". One has the status "Closed", which the Pydantic model refuses. A crash is a safe failure in the sense that nothing gets recommended, but it reaches the user as an error rather than an explained NO_BID, and in a batch the record simply disappears. The engine parses both real date formats and fails closed, with a reason, on anything it cannot parse.

**Checkpoint 2 disagrees with the two Checkpoint 1 BID references (0.5 each).** The engine returns CONDITIONAL_BID for the building-renovation (EUR 5M) and data-centre (EUR 2.2M) fixtures because a small consultancy is modelled as a consortium partner above EUR 750k, and a lead partner must be secured. This is a deliberate change in judgement, not a defect, but it is the engine's assumption and a bid manager may overrule it. It is recorded as a disagreement rather than counted as a pass.

**A decision depends on context the per-example test cannot see.** Run alone, ACER/2026/OP/0016 (EUR 250k study) is a BID. In the 14-tender portfolio run it is only a reserve, because three other bids use the cycle's bid budget and team capacity first. Row-level evaluation measures the gate and the risk model. It does not measure portfolio selection; the unit tests in `tests/test_decision_engine.py` check that.

**The point estimates the engine inherits are optimistic and uncalibrated.** Checkpoint 1 assumes up to a 72% win probability and about a 31% gross margin. With a conservative profile (half the win probability, costs implied by the company's own 18% target margin), the engine's selection on the live run falls from four tenders to one, and bidding on every eligible tender has about a 51% chance of losing money. Every engine run reports both profiles. Neither can be calibrated until i@work records real win/loss outcomes.

**What this evaluation does not cover.** The two LLM stages (Stage 2 triage and Stage 3 ReAct acquisition) are not exercised offline: the targets start from the Stage 2 output. The injection test therefore shows only that the deterministic decision layer cannot be steered by tender text, not that the LLM stages are safe. The pinned Stage 4 output used for the dataset also shows that the run it came from used demo-mode acquisition (`backend: local`, empty ReAct trace, no documents ingested), so it is evidence of discovery and triage, not of live retrieval. Live ReAct and Pinecone retrieval were evidenced separately on 13 August. None of the reference labels is a human judgement of decision *quality*; only biddability and the three published fixtures are labelled.

## 7. What a real pilot would monitor

| Signal | Why | Alert threshold (initial) |
|---|---|---|
| Share of advanced tenders that fail the hard gates | 7 of 14 in the live run; a rise means the source or Stage 1 filter has drifted | Above 25% in a run |
| Unparseable-deadline count | New portal date formats crash older code | Any |
| Recommendations on records later found closed, cancelled or PIN | The failure this evaluation found | Any |
| Win rate by decision class and profile | The only way to calibrate the win-probability model | Reviewed after every 10 submitted bids |
| Realised margin against modelled margin on won contracts | Calibrates the cost-ratio assumption | Gap above 5 percentage points |
| Human override rate on the Stage 10 approval step | Measures trust and model fit | Above 40% for two consecutive months |
| Retrieval backend per run (`pinecone` vs `local`) | Silent fallback weakens the RAG claim | Any `local` fallback in live mode |
| Tokens, cost and latency per completed assessment | Checkpoint 1 green-software assessment baseline (estimated USD 0.20–0.45 per assessment) | Above 2x the trailing median |
| LLM triage disagreement with the gates | Relevance 4–5 on dead tenders shows triage is blind to dates | Tracked, not alerted |

## 8. How to reproduce in LangSmith

```bash
cd eu-tender-autonomous-agent-2
python -m pip install -e . langsmith
export LANGSMITH_API_KEY=...            # from smith.langchain.com
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=eu-tender-cp2
python evaluation/build_dataset.py
PYTHONPATH=src:. python evaluation/run_langsmith_experiment.py          # dataset + 2 experiments + traces
PYTHONPATH=src:. python evaluation/run_langsmith_experiment.py --judge  # optional: adds the LLM judge
PYTHONPATH=src:. python evaluation/run_langsmith_experiment.py --offline  # no network, same numbers
```

In LangSmith, open **Datasets & Experiments → eu-tender-decisions-v2**, select both experiments, and use **Compare** to show the per-example differences. That comparison view is the screenshot for the presentation.
