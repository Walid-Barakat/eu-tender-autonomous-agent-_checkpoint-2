// Checkpoint 2: eleven scenes, in the format of the Checkpoint 1 deck (presentation-data.js).
// build_checkpoint2.py adds timing, narration and subtitles. Numbers come from the repository:
// data/live_run_2026_08_12, src/tender_agent/decision_engine, evaluation/results/offline_experiment.md,
// analysis/roi_results.json, roi_risk_assessment.md, eu_ai_act_compliance.md, gdpr_documentation.md, strategic_plan.md.
(() => {
  const repo = "https://github.com/Walid-Barakat/eu-tender-autonomous-agent-2";
  const card = (title, big, text, cls = "") =>
    `<div class="cp2-card ${cls}"><h3>${title}</h3>${big ? `<b class="big">${big}</b>` : ""}<p>${text}</p></div>`;
  const chip = (text, cls) => `<span class="cp2-chip ${cls}">${text}</span>`;
  const cp2 = o => ({ type: "cp2", cue: "", script: [], sources: [["Repository", repo]], ...o });

  function rangeChart(rows) {
    const W = 600, rowH = 40, top = 18, left = 182, right = 16;
    const H = top + rows.length * rowH + 26;
    const lo = -90000, hi = 680000;
    const x = v => left + ((v - lo) / (hi - lo)) * (W - left - right);
    let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Profit ranges per tender under two assumption profiles">`;
    for (const t of [0, 200000, 400000, 600000]) {
      svg += `<line x1="${x(t)}" x2="${x(t)}" y1="${top - 6}" y2="${H - 22}" stroke="${t === 0 ? "#5d7388" : "#c9e1ec"}" stroke-width="1" ${t === 0 ? 'stroke-dasharray="3 3"' : ""}/>`;
      svg += `<text x="${x(t)}" y="${H - 6}" text-anchor="middle">${t === 0 ? "€0" : "€" + t / 1000 + "k"}</text>`;
    }
    rows.forEach((r, i) => {
      const y = top + i * rowH;
      svg += `<text class="lbl" x="${left - 10}" y="${y + 16}" text-anchor="end">${r.id}</text>`;
      [[r.c1, "#0f7fb0", 7], [r.cons, "#c2702a", 21]].forEach(([d, col, dy]) => {
        svg += `<line class="grow" x1="${x(d[0])}" x2="${x(d[2])}" y1="${y + dy}" y2="${y + dy}" stroke="${col}" stroke-width="3" stroke-linecap="round" style="animation-delay:${0.15 * i}s"/>`;
        svg += `<circle cx="${x(d[1])}" cy="${y + dy}" r="5" fill="${col}" stroke="#f8fbfd" stroke-width="2"/>`;
      });
    });
    return svg + "</svg>";
  }

  function roiChart() {
    const a36 = { 0: -13800, 3: -10785, 6: -765, 9: 9255, 12: 19275, 15: 29295, 18: 39315, 21: 49335, 24: 59355, 27: 69375, 30: 79395, 33: 89415, 36: 99435 };
    const b36 = { 0: -13800, 3: -4035, 6: 19485, 9: 43005, 12: 66525, 15: 90045, 18: 113565, 21: 137085, 24: 160605, 27: 184125, 30: 207645, 33: 231165, 36: 254685 };
    const W = 700, H = 300, L = 62, R = 76, Tp = 14, B = 30, lo = -40000, hi = 260000;
    const x = m => L + (m / 36) * (W - L - R);
    const y = v => Tp + (1 - (v - lo) / (hi - lo)) * (H - Tp - B);
    const path = obj => Object.entries(obj).map(([m, v], i) => `${i ? "L" : "M"}${x(+m)},${y(v)}`).join("");
    let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Cumulative net position over 36 months">`;
    for (const v of [0, 100000, 200000]) {
      s += `<line x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}" stroke="${v === 0 ? "#5d7388" : "#c9e1ec"}" stroke-width="1" ${v === 0 ? 'stroke-dasharray="3 3"' : ""}/>`;
      s += `<text x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${v === 0 ? "€0" : "€" + v / 1000 + "k"}</text>`;
    }
    for (const m of [0, 6, 12, 18, 24, 30, 36]) s += `<text x="${x(m)}" y="${H - 8}" text-anchor="middle">m${m}</text>`;
    s += `<path d="${path(b36)}" fill="none" stroke="#c2702a" stroke-width="2.5" stroke-dasharray="6 4" pathLength="1"/>`;
    s += `<path class="draw" d="${path(a36)}" fill="none" stroke="#0f7fb0" stroke-width="3" pathLength="1"/>`;
    s += `<circle cx="${x(7)}" cy="${y(2575)}" r="5" fill="#0f7fb0" stroke="#f8fbfd" stroke-width="2"/><text class="lbl" x="${x(7) + 8}" y="${y(2575) + 18}">break-even, month 7</text>`;
    s += `<text class="lbl" x="${x(36) + 8}" y="${y(99435) + 4}">+€99k</text>`;
    s += `<text class="lbl" x="${x(36) + 8}" y="${y(254685) + 4}" style="fill:#c2702a">+€255k</text>`;
    return s + "</svg>";
  }

  const rows = [
    { id: "EC-ENER/2026/OP/0064", c1: [-71084, 287901, 659874], cons: [-82036, 39422, 329975] },
    { id: "EC-JRC/…/3886-EXA", c1: [-14067, 80266, 270077], cons: [-16326, 13546, 105256] },
    { id: "CINEA/2026/OP/0028", c1: [-33737, 62704, 246716], cons: [-37409, 1688, 119258] },
    { id: "ACER/2026/OP/0020", c1: [-15515, 32244, 109813], cons: [-16825, 1643, 54468] },
    { id: "CINEA/2026/OP/0015", c1: [-32347, 27537, 238589], cons: [-35448, -6391, 95699] },
    { id: "EC-ENER/2026/OP/0042", c1: [-28422, 26789, 181524], cons: [-30603, -5912, 77544] },
    { id: "ACER/2026/OP/0016", c1: [-13061, 12705, 53088], cons: [-14055, -3279, 25647] },
  ];

  window.C2_SLIDES = [
    cp2({ id: "c2-00", dark: true, section: "Checkpoint 2 · Why it matters",
      title: "Finding the calls is easy. Deciding which to bid on is where firms lose money.", subtitle: "",
      html: `<div class="c2-market">
        <div class="c2-stat"><b class="count" data-to="250000" data-fmt="int" data-suffix="+">250,000+</b><span>EU public authorities buy through procurement</span></div>
        <div class="c2-stat"><b class="count" data-to="2" data-prefix="≈ €" data-suffix=" trillion">≈ €2 trillion</b><span>spent every year</span></div>
        <div class="c2-stat"><b class="count" data-to="14" data-prefix="≈ " data-suffix="%">≈ 14%</b><span>of EU GDP</span></div>
      </div>
      <p class="c2-market-src">Source: European Commission, public procurement (defence-industry-space.ec.europa.eu)</p>`,
      cue: "Open with the stakes, then turn to what the Checkpoint 1 data showed.",
      sources: [["European Commission: public procurement", "https://defence-industry-space.ec.europa.eu/funding-opportunities/public-procurement_en"]] }),

    cp2({ id: "c2-01", section: "Checkpoint 2 · What the data showed",
      title: "The system worked as designed. Its own data showed what was missing.",
      subtitle: "7 of the 14 advanced tenders could not be bid on when they were found, 12 Aug 2026",
      html: `<div class="cp2-grid cp2-cols-evid">
        <table class="cp2-table tight"><thead><tr><th>Tender</th><th>Why not biddable</th><th>Relevance</th><th>Checkpoint 1</th></tr></thead><tbody>
          <tr><td class="id">NEAR/ANK/2023/EA-RP/0104</td><td>Closed 14 Nov 2024</td><td class="n">5 · 0.90</td><td>${chip("CONDITIONAL BID", "bad")}</td></tr>
          <tr><td class="id">ACER/2025/LVP/0055-EXA</td><td>Closed 15 Oct 2025</td><td class="n">5 · 0.90</td><td>${chip("NO BID", "ok")}</td></tr>
          <tr><td class="id">EC-ENEST/ANK/2025/EA-RP/0146</td><td>Closed 19 Dec 2025</td><td class="n">4 · 0.75</td><td>${chip("CONDITIONAL BID", "bad")}</td></tr>
          <tr><td class="id">ACER/2026/LVP/0002-EXA</td><td>Closed 7 Jan 2026</td><td class="n">4 · 0.75</td><td>${chip("CONDITIONAL BID", "bad")}</td></tr>
          <tr><td class="id">ACER/2026/MVP/0009-EXA</td><td>Closed 31 Mar 2026</td><td class="n">5 · 0.90</td><td>${chip("CONDITIONAL BID", "bad")}</td></tr>
          <tr><td class="id">CINEA/2026/OP/0028-PIN</td><td>Prior notice (PIN)</td><td class="n">5 · 0.90</td><td>${chip("CRASH: date 14/07/2026", "mid")}</td></tr>
          <tr><td class="id">CINEA/2026/OP/0015-PIN</td><td>Prior notice (PIN)</td><td class="n">4 · 0.75</td><td>${chip("CRASH: date 11/06/2026", "mid")}</td></tr>
        </tbody></table>
        <div><p class="cp2-lead">Status said <b>"Open for submission"</b>. The deadlines said otherwise.</p>
        <ul class="cp2-list"><li>The relevance agent was right about relevance.</li>
        <li>Nothing checked whether a bid was still possible on the day.</li>
        <li>That gap is the job of Agent 10.</li></ul></div>
      </div>`,
      cue: "The hinge of the story: from Checkpoint 1 to Checkpoint 2.",
      sources: [["Live-run records", repo + "/blob/main/data/live_run_2026_08_12/stage2_advanced_tenders.json"]] }),

    cp2({ id: "c2-02", section: "Checkpoint 2 · Stochastic modelling",
      title: "Each bid is a distribution, not a score.",
      subtitle: "4,000 seeded scenarios per tender: win or lose, award value, consortium share, cost overrun with a shared shock, time to prepare.",
      html: `<div class="cp2-grid cp2-cols-wide">
        <div>${rangeChart(rows)}
        <div class="cp2-note"><span style="color:#0f7fb0;font-weight:800">●</span> Checkpoint 1 assumptions &nbsp; <span style="color:#c2702a;font-weight:800">●</span> Conservative: half the win chance, 18% target margin &nbsp;·&nbsp; bar P5–P95, dot expected profit</div></div>
        <div><p class="cp2-lead">All 7 eligible tenders look profitable on <b>Checkpoint 1 assumptions</b>. Only <b>4</b> do on the conservative profile.</p>
        <ul class="cp2-list"><li>Most single bids lose money more often than not: they lose the bid cost unless they win.</li>
        <li>Neither profile is calibrated yet, so every run reports both.</li>
        <li>Same inputs and seed give the same answer, so it can be tested and audited.</li></ul></div>
      </div>`,
      cue: "Show the gap between blue and orange: that gap is model uncertainty, stated openly.",
      sources: [["monte_carlo.py", repo + "/blob/main/src/tender_agent/decision_engine/monte_carlo.py"]] }),

    cp2({ id: "c2-03", section: "Checkpoint 2 · Optimisation",
      title: "Choose the portfolio, not the tender.",
      subtitle: "Exact search over all 127 portfolios of the 7 eligible tenders, scored on the same joint scenarios.",
      html: `<div class="cp2-grid cp2-cols-wide">
        <table class="cp2-table"><thead><tr><th></th><th class="n">Bids</th><th class="n">Bid spend</th><th class="n">Expected profit</th><th class="n">Chance of loss</th><th class="n">Over capacity</th></tr></thead><tbody>
          <tr><td colspan="6" style="color:#5d7388;font-size:12px">CHECKPOINT 1 ASSUMPTIONS</td></tr>
          <tr><td>Bid on every eligible tender</td><td class="n">7</td><td class="n">€145.5k ✗</td><td class="n">€530k</td><td class="n">6%</td><td class="n">21.5% ✗</td></tr>
          <tr class="hl"><td>Optimised portfolio</td><td class="n">4</td><td class="n">€107.5k</td><td class="n">€458k</td><td class="n">10%</td><td class="n">9.2%</td></tr>
          <tr><td colspan="6" style="color:#5d7388;font-size:12px">CONSERVATIVE PROFILE</td></tr>
          <tr><td>Bid on every eligible tender</td><td class="n">7</td><td class="n">€145.5k ✗</td><td class="n">€41k</td><td class="n">51%</td><td class="n">3.4%</td></tr>
          <tr class="hl"><td>Optimised portfolio</td><td class="n">1</td><td class="n">€10k</td><td class="n">€13.5k</td><td class="n">67%</td><td class="n">0%</td></tr>
        </tbody></table>
        <div><p class="cp2-lead">Robust under both: <b>EC-JRC/SVQ/2026/MVP/3886</b>, Clean Energy in the EU Enlargement Region.</p>
        <ul class="cp2-list"><li>Constraints: €112.5k bid budget this cycle; at most 3 bids due within 14 days; at most 10% chance of winning more than €3.6M of delivery capacity.</li>
        <li>Objective: expected profit − 0.5 × average of the worst 5% of outcomes.</li></ul></div>
      </div>`,
      cue: "Land on the robust tender.",
      sources: [["portfolio.py", repo + "/blob/main/src/tender_agent/decision_engine/portfolio.py"]] }),

    { id: "c2-04", type: "console", section: "Checkpoint 2 · Working MVP",
      title: "The portfolio console, live.", subtitle: "",
      cue: "Narrated mode runs the walkthrough by itself. Live: click Run demo, or drive the console yourself; Next moves on.",
      script: [], sources: [["Tender Portfolio Console", repo + "/blob/main/ui/tender_portfolio_console.html"],
        ["Stage 10 workflow", repo + "/blob/main/workflows/n8n/stage_10_portfolio_decision_engine.json"]] },

    cp2({ id: "c2-05", section: "Checkpoint 2 · Evaluation",
      title: "What improved, what failed, and what is still open.",
      subtitle: "LangSmith dataset eu-tender-decisions-v2: 23 examples, 14 of them real live-run tenders. Same evaluators for both systems; offline experiment of 7 Oct 2026.",
      html: `<div class="cp2-grid cp2-cols-even">
        <table class="cp2-table"><thead><tr><th>Evaluator</th><th class="n">Checkpoint 1</th><th class="n">Checkpoint 2</th></tr></thead><tbody>
          <tr class="hl"><td>Non-biddable records rejected</td><td class="n">0.20</td><td class="n">1.00</td></tr>
          <tr><td>Recommendations on biddable records</td><td class="n">0.75</td><td class="n">1.00</td></tr>
          <tr><td>Completed without error</td><td class="n">0.83</td><td class="n">1.00</td></tr>
          <tr><td>Matches reference decision</td><td class="n">0.39</td><td class="n">0.92</td></tr>
          <tr><td>Reproducible; unchanged by injected text</td><td class="n">1.00</td><td class="n">1.00</td></tr>
        </tbody></table>
        <div class="cp2-flow">
          <div class="cp2-step" style="grid-template-columns:120px 1fr"><b>Fixed</b><span>Bids on closed tenders; crashes on real date formats.</span></div>
          <div class="cp2-step yes" style="grid-template-columns:120px 1fr"><b>Confirmed</b><span>Stage 9 publication order; fix is on the pre-pilot list.</span></div>
          <div class="cp2-step yes" style="grid-template-columns:120px 1fr"><b>Open</b><span>Uncalibrated assumptions; LLM stages not adversarially tested; no human-labelled decision quality.</span></div>
          <div class="cp2-step" style="grid-template-columns:120px 1fr"><b>Disagrees</b><span>0.5 on two reference BIDs: above €750k it asks for a consortium lead.</span></div>
        </div>
      </div>`,
      cue: "Lead with the key test: 0.2 to 1.0.",
      sources: [["evaluation/results/offline_experiment.md", repo + "/blob/main/evaluation/results/offline_experiment.md"], ["evaluation/langsmith.md", repo + "/blob/main/evaluation/langsmith.md"]] }),

    cp2({ id: "c2-06", section: "Checkpoint 2 · ROI and cost",
      title: "Base case: break-even in month 7, +65% at 12 months.",
      subtitle: "ROI = (benefit − cost) / cost × 100. Headline uses operational benefits only: time saved and wasted bid cost avoided.",
      html: `<div class="cp2-grid cp2-cols-wide">
        <div>${roiChart()}<div class="cp2-note"><span style="color:#0f7fb0;font-weight:800">━</span> operational benefits only &nbsp; <span style="color:#c2702a;font-weight:800">┅</span> including extra bids found (uncalibrated)</div></div>
        <table class="cp2-table"><tbody>
          <tr><td>Upfront: setup + onboarding</td><td class="n">€13,800</td></tr>
          <tr><td>Running cost per month</td><td class="n">€1,330</td></tr>
          <tr><td>Hours saved per month</td><td class="n">57 of 70</td></tr>
          <tr class="hl"><td>ROI at 12 / 36 months</td><td class="n">+65% / +161%</td></tr>
          <tr><td>Monte Carlo 12-month ROI, P10–P90</td><td class="n">+27% to +145%</td></tr>
          <tr><td>Chance 12-month ROI is negative</td><td class="n">1.6%</td></tr>
          <tr><td>Every assumption at its worst</td><td class="n">−94%, never</td></tr>
        </tbody></table>
      </div>`,
      cue: "Say the worst case out loud.",
      sources: [["analysis/roi_model.py", repo + "/blob/main/analysis/roi_model.py"], ["analysis/roi_results.json", repo + "/blob/main/analysis/roi_results.json"]] }),

    cp2({ id: "c2-07", section: "Checkpoint 2 · Major risks",
      title: "Twelve risks registered. Two have already happened.",
      subtitle: "Top six by score (likelihood × impact, 1–5 each), covering technical, regulatory, ethical and operational risk",
      html: `<table class="cp2-table"><thead><tr><th>Risk</th><th>Category</th><th class="n">L × I</th><th>Mitigation</th><th>Status</th></tr></thead><tbody>
        <tr><td>Non-biddable tenders recommended</td><td>Technical</td><td class="n">5 × 4</td><td>Hard gates; monitor gate-failure share</td><td>${chip("observed · fixed", "ok")}</td></tr>
        <tr><td>Uncalibrated win and margin assumptions</td><td>Technical</td><td class="n">4 × 4</td><td>Both profiles; record outcomes; recalibrate</td><td>${chip("open", "bad")}</td></tr>
        <tr><td>Personal data to non-EU providers without DPAs</td><td>Regulatory (GDPR)</td><td class="n">3 × 4</td><td>DPAs, EU regions, PII filter before LLM calls</td><td>${chip("pre-pilot", "mid")}</td></tr>
        <tr><td>Approver rubber-stamps false precision</td><td>Ethical</td><td class="n">3 × 4</td><td>Rationale required; ranges shown; overrides logged</td><td>${chip("partly built", "mid")}</td></tr>
        <tr><td>Credentials shipped in an archive</td><td>Operational</td><td class="n">3 × 4</td><td>Rotate keys; release with git archive; secret scan</td><td>${chip("observed · rotate", "mid")}</td></tr>
        <tr><td>Person-level feature drifts into AI Act Annex III</td><td>Regulatory (AI Act)</td><td class="n">2 × 5</td><td>Scope lock; re-classify before any such feature</td><td>${chip("controlled", "ok")}</td></tr>
      </tbody></table>`,
      cue: "Name the two that already happened.",
      sources: [["roi_risk_assessment.md", repo + "/blob/main/roi_risk_assessment.md"]] }),

    cp2({ id: "c2-08", section: "Checkpoint 2 · EU AI Act",
      title: "An AI system, not prohibited, not high-risk. Two binding duties.",
      subtitle: "Annex III high-risk obligations now apply from 2 Dec 2027 (Digital Omnibus); Article 50 transparency applies from 2 Aug 2026.",
      html: `<div class="cp2-grid cp2-cols-2">
        <div class="cp2-flow">
          <div class="cp2-step yes"><b>AI system? (Art. 3)</b><span>Yes: LLM triage, ReAct agent, generated summaries.</span></div>
          <div class="cp2-step"><b>Prohibited? (Art. 5)</b><span>No.</span></div>
          <div class="cp2-step"><b>Annex III high-risk?</b><span>No. Not a safety component of energy supply; scores no person; procurement not listed.</span></div>
          <div class="cp2-step yes"><b>Binding duties</b><span>Art. 4 AI literacy · Art. 50(2) machine-readable marking of AI text (conservative reading).</span></div>
          <div class="cp2-step"><b>Role</b><span>i@work: provider. Client firm: deployer.</span></div>
        </div>
        <div><p class="cp2-lead">Applied voluntarily: <b>human oversight</b> (Stage 10 approval), <b>logging</b>, <b>measured accuracy</b> and <b>robustness tests</b>.</p>
        <ul class="cp2-list"><li>The AI voices in this presentation are labelled as AI-generated: transparency in practice.</li>
        <li>Gaps before the pilot: write the marking fields; deliver the literacy module.</li>
        <li>Main uncertainty: matching named experts to proposal roles could fall under Annex III point 4. Out of scope, with a re-classification gate.</li></ul></div>
      </div>`,
      cue: "Walk the ladder top to bottom, then the one uncertainty.",
      sources: [["eu_ai_act_compliance.md", repo + "/blob/main/eu_ai_act_compliance.md"], ["Gibson Dunn: Omnibus agreement", "https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/"]] }),

    cp2({ id: "c2-09", section: "Checkpoint 2 · GDPR",
      title: "GDPR: proceed with conditions.",
      subtitle: "The decision is about organisations, but tender notices and annexes still carry personal data.",
      html: `<div class="cp2-grid cp2-cols-3 auto">
        ${card("Personal data", "", "Officer contacts in notices; people named in annexes and CVs; client users; the Stage 10 approver record; logs. The decision engine itself uses no personal data.")}
        ${card("Basis and DPIA", "", "Art. 6(1)(f) with an LIA; Art. 14 position open. 2 of 9 EDPB criteria met, so a DPIA before the pilot.", "warn")}
        ${card("Highest risk", "", "Annex text sent to non-EU LLM and embedding providers and kept in a vector store. Transfers need DPF certification or SCCs.", "warn")}
      </div><div class="cp2-band light">Before the pilot: PII filter before every LLM and embedding call · executed DPAs · per-tender vector deletion.</div>`,
      cue: "Three cards, then the band.",
      sources: [["gdpr_documentation.md", repo + "/blob/main/gdpr_documentation.md"]] }),

    cp2({ id: "c2-10", section: "Checkpoint 2 · Go to market",
      title: "POC → Pilot → Full deployment, each gated on evidence.", subtitle: "",
      html: `<div class="cp2-grid auto" style="grid-template-columns:repeat(4,1fr)">
        ${card("POC · done", "Jul–Oct 2026", "Checkpoint 1 live run; Checkpoint 2 engine, evaluation, compliance pack.", "good")}
        ${card("Harden · ~10 days", "13 Oct–6 Nov", "Rotate keys, EU hosting, PII filter, DPAs, AI marking, Stage 9 fixes, LangSmith upload.")}
        ${card("Pilot · 3 months", "9 Nov–5 Feb", "One energy engineering firm, ≤25 assessments a month, weekly portfolio run with human approval.", "warn")}
        ${card("Full deployment", "Mar 2027 →", "Multi-client, calibrated model, TED and CORDIS sources; re-classify before 2 Dec 2027.")}
      </div><div class="cp2-band light">Pilot succeeds if: ≥22 h/month saved · 0 bids on non-biddable tenders · ≥95% runs complete · 100% approvals with rationale.<br>Managed service: €10.8k setup + €1,200/month · target contribution ≈ €9k per client per year.</div>`,
      cue: "Read the success criteria and the price. This is the investor slide.",
      sources: [["strategic_plan.md", repo + "/blob/main/strategic_plan.md"]] }),

    cp2({ id: "c2-11", section: "Checkpoint 2 · Built to grow",
      title: "Built to grow: new agents plug into the same pipeline.",
      subtitle: "One job and a typed contract per agent; logged, evaluated, and a human keeps the final decision. Roadmap, not yet built.",
      html: `<div class="c2-grow">
        <div class="c2-now"><span class="c2-now-k">Today</span>${["A01","A02","A03","A04","A05","A06","A07","A08","A09","A10"].map(a => `<span class="c2-dot"><img src="__FACE__" alt="">${a}</span>`).join("")}<span class="c2-dot human">HUMAN</span></div>
        <div class="c2-next">${[
          ["Legal &amp; Compliance", "Contract terms, liability, IPR, exclusion criteria, GDPR and AI Act duties; flags clauses for counsel.", "joins A06 Eligibility"],
          ["Feasibility &amp; Project Evaluation", "Techno-economic case for energy projects: CAPEX, OPEX, LCOE, NPV and risk-adjusted returns.", "joins A07 specialists"],
          ["PMO &amp; Project Delivery", "Turns a won bid into work packages, schedule, milestones and reporting.", "after the award"],
          ["Recruiting &amp; Outsourcing", "Required expertise matched to partners and subcontractors; a consortium proposal.", "AI Act: ranking people is high-risk; re-classify first", "warn"],
          ["Finance &amp; Controlling", "Bid budgets, cash flow and recorded outcomes that calibrate the win and margin model.", "feeds A10"],
          ["Corporate Strategy &amp; Innovation / R&amp;D", "Aligns the tender pipeline with company strategy and technology roadmaps; spots R&amp;D calls early.", "steers A02 Relevance"],
          ["Governance &amp; Public Affairs", "Follows EU energy policy, consultations and work programmes before calls open.", "feeds A01 Sources"],
        ].map(([n, f, link, cls]) => `<div class="c2-new ${cls || ""}"><span class="c2-dot dashed"><img src="__FACE__" alt=""></span><div><b>${n}</b><p>${f}</p><em>${link}</em></div></div>`).join("")}<div class="c2-new plus"><span class="c2-plus">+</span><div><b>Your next agent</b><p>Any role with a clear input and output plugs in the same way: contract, logging, evaluation, human approval.</p><em>open by design</em></div></div></div>
      </div>`,
      cue: "Point at the dashed agents: same contract, same evaluation, same human approval.",
      sources: [["Architecture", repo + "/blob/main/docs/ARCHITECTURE.md"], ["Future development stages", repo + "/blob/main/docs/FUTURE_DEVELOPMENT_STAGES.md"]] }),

    { id: "c2-12", type: "closing2", section: "Recommendation",
      title: "Proceed to a three-month pilot, under four conditions.", subtitle: "",
      conditions: [["Measure", "the manual workload before the pilot starts"], ["Record", "every bid outcome, to calibrate the model"],
        ["Protect", "close the data-protection pre-conditions"], ["Decide", "a human approves every portfolio"]],
      cue: "Stop at the end card. Invite questions.", script: [], sources: [["Repository", repo]] },
  ];
})();
