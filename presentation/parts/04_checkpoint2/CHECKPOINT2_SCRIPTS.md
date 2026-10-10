# Checkpoint 2: scripts

13 scenes. Target time when you present live: **6:25**.

To record your own voice: one file per scene, named as below (`c2-00.m4a` … `c2-12.m4a`; mp3 or wav also work). On the start card of `Checkpoint2.html`, click **Load my recordings** and select them; they replace the narration and the slides follow your timing. Speak calmly and leave half a second of silence at each end.

## c2-00 · Finding the calls is easy. Deciding which to bid on is where firms lose money.

*0:00–0:15 · 15 s · file `c2-00.m4a`*

Every year over 250,000 EU public authorities spend about €2 trillion through procurement. Finding the calls is easy. Deciding which to bid on is where firms lose money.

## c2-01 · The system worked as designed. Its own data showed what was missing.

*0:15–0:45 · 30 s · file `c2-01.m4a`*

The system worked as designed, and its own data showed what was missing. The relevance agent scored these seven tenders four or five out of five, and it was right about relevance. But five deadlines had already passed and two were prior-information notices. Checkpoint 1 recommended conditional bids on four of them and crashed on two. That is why I built Agent 10.

## c2-02 · Each bid is a distribution, not a score.

*0:45–1:15 · 30 s · file `c2-02.m4a`*

Agent 10 simulates four thousand outcomes for every bid. Blue uses the Checkpoint 1 assumptions; orange is a conservative profile with half the win chance and an eighteen percent margin target. On blue, every eligible tender looks profitable. On orange, only four do. There is no win-loss history yet, so the engine always shows both.

## c2-03 · Choose the portfolio, not the tender.

*1:15–1:45 · 30 s · file `c2-03.m4a`*

Bids compete for the same budget, the same people in the same weeks, and the same delivery capacity. The optimiser checks all 127 possible portfolios exactly. Bidding on everything breaks the budget. One tender is selected under both profiles: that is the bid I would defend today.

## c2-04 · The portfolio console, live.

*1:45–2:55 · 70 s · file `c2-04.m4a`*

This is the lightweight interface on the same four thousand scenarios as the Python engine. Seven of the fourteen tenders fail a hard gate, each with its reason. The optimiser selects four bids. Switch to the conservative profile, and four bids become one. Back on the first profile, raise risk aversion to four: the selection changes, because the bad tail now weighs more. Open a tender to see its reasons, conditions and a draft proposal outline. Finally, the bid authority approves with a written rationale. In n8n, that approval resumes the Stage 10 workflow. Nothing is ever submitted automatically.

Walkthrough on screen while you speak: 0 s all 14 tenders · 3.5 s the 7 gate failures · 10.5 s 4 bids, €458k · 17.5 s Conservative: 1 bid · 26 s back, risk aversion to 4 · 31.5 s ACER/2026/OP/0020 replaces the two CINEA bids · 39.5 s EC-JRC opens · 50.5 s rationale typed · 58 s approved.

## c2-05 · What improved, what failed, and what is still open.

*2:55–3:30 · 35 s · file `c2-05.m4a`*

Both systems ran on the same twenty-three examples with the same evaluators. On the key test, rejecting tenders that cannot be bid on, Checkpoint 1 scores 0.2 and Checkpoint 2 scores 1.0. Two failures are fixed, one is confirmed and scheduled, and three questions remain open. Each has a place in the pilot.

## c2-06 · Base case: break-even in month 7, +65% at 12 months.

*3:30–4:05 · 35 s · file `c2-06.m4a`*

For a client firm, the base case breaks even in month seven: plus sixty-five percent in year one and plus one hundred sixty-one over three years, on operational benefits alone. Across twenty thousand simulated assumption sets, first-year ROI sits between plus twenty-seven and plus one hundred forty-five percent. If every assumption lands at its worst, it never pays back, so the pilot measures hours first.

## c2-07 · Twelve risks registered. Two have already happened.

*4:05–4:25 · 20 s · file `c2-07.m4a`*

Twelve risks are registered. Two already happened in this project: closed tenders were recommended, and credentials ended up in a shared archive. The top open risk is uncalibrated assumptions.

## c2-08 · An AI system, not prohibited, not high-risk. Two binding duties.

*4:25–5:00 · 35 s · file `c2-08.m4a`*

Under the AI Act this is an AI system, not prohibited and not high-risk: it is not a safety component of energy infrastructure, it scores no person, and procurement is not an Annex III area. Two duties bind: AI literacy, and machine-readable marking of AI-generated content. Matching named experts to roles would change the classification, so it is out of scope.

## c2-09 · GDPR: proceed with conditions.

*5:00–5:20 · 20 s · file `c2-09.m4a`*

GDPR applies because notices and annexes name real people. The basis is legitimate interests, with a DPIA before the pilot. The fix is mostly engineering: strip personal data before model calls, sign processor agreements, and delete each tender's vectors when it closes.

## c2-10 · POC → Pilot → Full deployment, each gated on evidence.

*5:20–5:45 · 25 s · file `c2-10.m4a`*

Ten days of hardening, then a three-month paid pilot with one energy engineering firm. It succeeds if it saves at least twenty-two hours a month and recommends no closed tenders. Commercially it is a managed service: about eleven thousand euros to set up and twelve hundred a month.

## c2-11 · Built to grow: new agents plug into the same pipeline.

*5:45–6:10 · 25 s · file `c2-11.m4a`*

The system is built to grow. Every agent has one job and a typed contract, so new agents plug into the same pipeline: legal and compliance, feasibility and project evaluation, PMO and project delivery, recruiting and outsourcing, finance and controlling, corporate strategy and R&D, and public affairs. The final decision stays with a human.

## c2-12 · Proceed to a three-month pilot, under four conditions.

*6:10–6:25 · 15 s · file `c2-12.m4a`*

So, should we proceed? Yes, to a three-month pilot, under four conditions: measure the manual workload first, record every bid outcome, close the data-protection pre-conditions, and keep a human approving every portfolio. Thank you.
