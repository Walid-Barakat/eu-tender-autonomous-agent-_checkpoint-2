/*
 * actsEU final presentation: "The Search" (10 October 2026, 15:55-16:05).
 *
 * INSTALL: paste this whole file into a new script element immediately before
 * the closing body tag of the presentation HTML, after the existing renderer
 * script. It replaces checkpoint2_merge.js: install only one of the two.
 *
 * STRUCTURE: 21 scenes, 9:20 in total.
 *   Act I    The film (scenes 1-6, plays by itself)
 *   Act II   Meet the system: Checkpoint 1 presented as new, agents introduce themselves
 *   Act III  The decision engine (Checkpoint 2)
 *   Act IV   The business case and the ask
 * The 19 original narrated Checkpoint 1 slides follow as Appendix A.
 *
 * SETTINGS: change CONFIG below, or define window.ACTSEU_CONFIG before this
 * script, or add URL parameters for rehearsal, for example
 *   ?film=silent|anime|hybrid  &voices=browser|files|live  &music=synth|file|off
 *
 * IMAGES: put them next to the HTML in media-final/ as
 *   img-01.jpg ... img-07.jpg (1920x1080) and ag-01.png ... ag-10.png (1024x1024).
 * A missing image shows a labelled placeholder, so the deck always runs.
 * Agent audio for voices=files: media-final/ag-01.mp3 ... ag-10.mp3.
 */
(function () {
  "use strict";
  if (!window.presentationSlides || typeof renderSlide !== "function") return;
  if (window.__actseuFinal) return;
  window.__actseuFinal = true;

  // ------------------------------------------------------------ settings
  const CONFIG = Object.assign({
    filmStyle: "hybrid",          // "silent" | "anime" | "hybrid"
    voiceMode: "browser",         // "browser" (built-in voices) | "files" (your MP3s) | "live" (you read)
    music: "synth",               // "synth" (original piano loop) | "file" | "off"
    musicFile: "media-final/film-score.mp3",
    mediaDir: "media-final/",
    imageExt: "jpg",
    keepEvidenceClip: true,       // scene 10 plays the recorded full autonomous run
    presenterClips: { 7: false, 8: false, 10: false }, // version A: Checkpoint 1 avatar clips, per scene
    version: "B",                 // "A": 21 scenes in 9:20, you present Checkpoint 1 live.
                                  // "B": Checkpoint 1 plays as recorded (compressed), then Checkpoint 2 live, about 14 min.
    teamScene: true,              // the ten agents introduce themselves (A: scene 9; B: just before Checkpoint 2)
    animeRamp: true,              // anime style: picture resolution and colours grow from the Stone Age to HD
    c1Slides: [1, 3, 4, 7, 10, 16], // version B: Checkpoint 1 slides that play, in order
    c1Seconds: { 1: 49, 3: 54, 4: 49, 7: 41, 10: 91, 16: 48 }, // version B, c1Mode "original": seconds per slide
    intro: true,                  // version B: open with the film
    c1Mode: "voice",              // version B: "voice" = all 19 Checkpoint 1 slides with your short recordings
                                  // (media-final/voice/c1-01.m4a …); "original" = six slides with the original narration
    c2Mode: "live",               // version B: "live" = you present Checkpoint 2; "recorded" = c2-01 … c2-11 recordings play
    demo: "",                     // portfolio console walkthrough: "auto" or "manual"; empty = auto when recorded, manual when live
    voiceDir: "media-final/voice/",
    consoleSrc: "console.html",
  }, window.ACTSEU_CONFIG || {});
  try {
    const q = new URLSearchParams(location.search);
    if (q.get("film")) CONFIG.filmStyle = q.get("film");
    if (q.get("voices")) CONFIG.voiceMode = q.get("voices");
    if (q.get("music")) CONFIG.music = q.get("music");
    if (q.get("version")) CONFIG.version = q.get("version").toUpperCase();
    if (q.get("team")) CONFIG.teamScene = q.get("team") !== "off";
    if (q.get("ramp")) CONFIG.animeRamp = q.get("ramp") !== "off";
    if (q.get("intro")) CONFIG.intro = q.get("intro") !== "off";
    if (q.get("c1")) CONFIG.c1Mode = q.get("c1");
    if (q.get("c2")) CONFIG.c2Mode = q.get("c2");
    if (q.get("demo")) CONFIG.demo = q.get("demo");
  } catch (e) { /* keep defaults */ }

  const original = window.presentationSlides.slice();
  const repo = "https://github.com/Walid-Barakat/eu-tender-autonomous-agent-2";
  // Version B narration scripts, inserted at build time from version_b_scripts.json.
  const SCRIPTS_B = {"c1":[{"id":"c1-01","slide":1,"seconds":22,"title":"EU Tender Autonomous AI Agent","text":"Hello everyone. I am Dr.-Ing. Walid Barakat from Bonn, and my company, i@work, builds AI energy systems for the EU market. This is the EU Tender Autonomous AI Agent. Finding a tender is easy. Deciding whether to invest in a bid is hard: it combines eligibility, capability, finance, risk and strategic fit. That decision is what this system automates."},{"id":"c1-02","slide":2,"seconds":16,"title":"Five development phases","text":"The project ran in five phases: research and scope, RAG, LangGraph agent design, n8n integration, and final polish. Trello tracked it as a delivery plan tied to requirements, tests and corrections."},{"id":"c1-03","slide":3,"seconds":20,"title":"The decision problem","text":"The system solves one decision in four steps. Discover finds current opportunities from the official EU source. Understand acquires details, documents and comparable evidence. Assess tests eligibility, capability, cost, margin and risk. Decide publishes an auditable recommendation. One human stays above the graph: I approve any real submission."},{"id":"c1-04","slide":4,"seconds":26,"title":"Hybrid architecture","text":"The architecture is hybrid. n8n runs the operation: a schedule or webhook triggers the EU search, and early validation and triage reject weak records before any paid reasoning. FastAPI is the typed boundary to Python. LangGraph owns state and routing, ReAct chooses evidence tools, and Pinecone grounds the assessment. Reports and receipts return to Notion, Slack and Google Drive."},{"id":"c1-05","slide":5,"seconds":18,"title":"LangGraph state machine","text":"The state machine starts with validation, so bad input fails early. Evidence is gathered before scoring, so decisions rest on tender content, not model memory. Each specialist writes structured results into shared state, and the last stages turn that state into a decision and a report."},{"id":"c1-06","slide":6,"seconds":16,"title":"Implementation evidence","text":"This is the working code: a Python package with an API boundary, state models, agent functions, tools, reports and tests. The GitHub repository adds setup, notebooks, workflow exports, diagrams and documentation."},{"id":"c1-07","slide":7,"seconds":14,"title":"Nine stages, nine agents","text":"Nine stages, nine bounded agent functions, not nine chatbots. Each has an explicit input and output contract, so failures stay isolated and evidence carries forward. You will meet them shortly."},{"id":"c1-08","slide":8,"seconds":20,"title":"Intake and early research","text":"Agent one validates source records before anything else runs. Then the ReAct researcher chooses the next evidence tool, document intelligence structures the attachments, and retrieval returns relevant passages from Pinecone. Evidence is added step by step, not pushed into one expensive prompt."},{"id":"c1-09","slide":9,"seconds":20,"title":"Reasoning progression","text":"Each stage receives structured state and returns evidence or a labelled fallback. Eligibility is a hard gate. Feasibility, finance and risk add scored analysis, and strategy produces BID, CONDITIONAL BID or NO BID, with conditions. A weak-evidence warning stays attached to its stage."},{"id":"c1-10","slide":10,"seconds":36,"title":"Full autonomous run","text":"This is one complete autonomous run, recorded end to end. It starts with the trigger and intake, passes validation and relevance, enters the Python reasoning workflow, and finishes with the decision and its delivery. Twenty-five official opportunities were found. Fourteen passed the relevance gate and completed the full path; eleven were archived before any expensive evidence work. The recording shows the contracts holding: n8n passes structured data to the API, LangGraph advances state, evidence is retrieved, and the report returns for publication."},{"id":"c1-11","slide":11,"seconds":16,"title":"Orchestration evidence","text":"Here n8n shows an executed workflow, not a diagram: green nodes and item counts show where records advanced or were archived. Live mode confirms the FastAPI boundary, so any failure can be traced to a run and a stage."},{"id":"c1-12","slide":12,"seconds":14,"title":"Trigger and knowledge layer","text":"The webhook is a second entry point into the same controlled pipeline. Pinecone stores and retrieves document vectors, so the analysis stays grounded in controlled evidence."},{"id":"c1-13","slide":13,"seconds":12,"title":"Report publication","text":"A decision is not complete until it is delivered. The report carries the recommendation, evidence, scores, risks and next action, and lands in Google Drive."},{"id":"c1-14","slide":14,"seconds":12,"title":"Operational visibility","text":"Notion is the decision radar: opportunities, decisions, confidence and status in one place. Slack sends the time-sensitive alerts to the team."},{"id":"c1-15","slide":15,"seconds":10,"title":"Delivery receipts","text":"These are the receipts: the tender in the radar, the report in Drive, the alert in Slack. Analysis alone is not delivery."},{"id":"c1-16","slide":16,"seconds":26,"title":"Hurdles and problem solving","text":"Getting here took repeated problem solving. Source access moved from the human portal to the official EU Search API. Credentials moved to the HTTP boundary. n8n exposed practical errors: Notion properties that did not match, changing node references, and conditions arriving as strings instead of booleans. The answer was layered: validation, typed conversion, bounded retries, labelled fallbacks and publication receipts."},{"id":"c1-17","slide":17,"seconds":22,"title":"Cost and token assessment","text":"Development cost was measured, not estimated: 125 dollars and 7 cents of language-model spend across 25.76 million tokens, from mid-July to mid-August 2026. Pinecone, Slack and Notion stayed on free tiers. That is the cost of building; the cost per report must be measured on clean production runs."},{"id":"c1-18","slide":18,"seconds":20,"title":"Achievements and requirements","text":"The submission links every required capability to evidence: a repository with setup, source, tests, notebook, diagrams and example reports; a Python layer with ReAct, LangGraph, Pinecone RAG, MCP tools and error handling; and an n8n layer with triggers, orchestration, retries and monitoring."},{"id":"c1-19","slide":19,"seconds":12,"title":"Checkpoint 1 complete","text":"Checkpoint 1 is a working autonomous prototype that turns official EU tender data into evidence-led decisions and delivers them. Now meet the agents that do the work."}],"c2":[{"id":"c2-01","scene":"hinge","seconds":30,"title":"What the data showed","text":"The system worked as designed, and its own data showed what was missing. The relevance agent scored these seven tenders four or five out of five, and it was right about relevance. But five deadlines had already passed and two were prior-information notices. Checkpoint 1 recommended conditional bids on four of them and crashed on two. That is why I built Agent 10."},{"id":"c2-02","scene":"distribution","seconds":30,"title":"Each bid is a distribution","text":"Agent 10 simulates four thousand outcomes for every bid. Blue uses the Checkpoint 1 assumptions; orange is a conservative profile with half the win chance and an eighteen percent margin target. On blue, every eligible tender looks profitable. On orange, only four do. There is no win-loss history yet, so the engine always shows both."},{"id":"c2-03","scene":"portfolio","seconds":30,"title":"Choose the portfolio","text":"Bids compete for the same budget, the same people in the same weeks, and the same delivery capacity. The optimiser checks all 127 possible portfolios exactly. Bidding on everything breaks the budget. One tender is selected under both profiles: that is the bid I would defend today."},{"id":"c2-04","scene":"console","seconds":70,"title":"The portfolio console","text":"This is the lightweight interface on the same four thousand scenarios as the Python engine. Seven of the fourteen tenders fail a hard gate, each with its reason. The optimiser selects four bids. Switch to the conservative profile, and four bids become one. Back on the first profile, raise risk aversion to four: the selection changes, because the bad tail now weighs more. Open a tender to see its reasons, conditions and a draft proposal outline. Finally, the bid authority approves with a written rationale. In n8n, that approval resumes the Stage 10 workflow. Nothing is ever submitted automatically."},{"id":"c2-05","scene":"langsmith","seconds":35,"title":"Evaluation in LangSmith","text":"Both systems ran on the same twenty-three examples with the same evaluators. On the key test, rejecting tenders that cannot be bid on, Checkpoint 1 scores 0.2 and Checkpoint 2 scores 1.0. Two failures are fixed, one is confirmed and scheduled, and three questions remain open. Each has a place in the pilot."},{"id":"c2-06","scene":"roi","seconds":35,"title":"ROI and cost","text":"For a client firm, the base case breaks even in month seven: plus sixty-five percent in year one and plus one hundred sixty-one over three years, on operational benefits alone. Across twenty thousand simulated assumption sets, first-year ROI sits between plus twenty-seven and plus one hundred forty-five percent. If every assumption lands at its worst, it never pays back, so the pilot measures hours first."},{"id":"c2-07","scene":"risks","seconds":20,"title":"Major risks","text":"Twelve risks are registered. Two already happened in this project: closed tenders were recommended, and credentials ended up in a shared archive. The top open risk is uncalibrated assumptions."},{"id":"c2-08","scene":"aiact","seconds":35,"title":"EU AI Act","text":"Under the AI Act this is an AI system, not prohibited and not high-risk: it is not a safety component of energy infrastructure, it scores no person, and procurement is not an Annex III area. Two duties bind: AI literacy, and machine-readable marking of AI-generated content. Matching named experts to roles would change the classification, so it is out of scope."},{"id":"c2-09","scene":"gdpr","seconds":20,"title":"GDPR","text":"GDPR applies because notices and annexes name real people. The basis is legitimate interests, with a DPIA before the pilot. The fix is mostly engineering: strip personal data before model calls, sign processor agreements, and delete each tender's vectors when it closes."},{"id":"c2-10","scene":"plan","seconds":25,"title":"Go to market","text":"Ten days of hardening, then a three-month paid pilot with one energy engineering firm. It succeeds if it saves at least twenty-two hours a month and recommends no closed tenders. Commercially it is a managed service: about eleven thousand euros to set up and twelve hundred a month."},{"id":"c2-11","scene":"end","seconds":15,"title":"Recommendation","text":"So, should we proceed? Yes, to a three-month pilot, under four conditions: measure the manual workload first, record every bid outcome, close the data-protection pre-conditions, and keep a human approving every portfolio. Thank you."}]} || { c1: [], c2: [] };
  const DEMO_MODE = CONFIG.demo || (CONFIG.c2Mode === "recorded" ? "auto" : "manual");
  const ecProcurement = "https://defence-industry-space.ec.europa.eu/funding-opportunities/public-procurement_en";

  const font = document.createElement("link");
  font.rel = "stylesheet";
  font.href = "https://fonts.googleapis.com/css2?family=Limelight&family=Bangers&display=swap";
  document.head.appendChild(font);

  // ------------------------------------------------------------ styles
  const css = `
  .cp2 .slide-body { height: 72%; padding-top: 2.2%; }
  .cp2-grid { display: grid; gap: 2.4%; height: 100%; }
  .cp2-grid.auto { height: auto; }
  .cp2-cols-2 { grid-template-columns: 1fr 1fr; }
  .cp2-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .cp2-cols-wide { grid-template-columns: 1.35fr .65fr; }
  .cp2-cols-evid { grid-template-columns: 1.85fr .65fr; }
  .cp2-cols-even { grid-template-columns: 1.1fr .9fr; }
  .cp2-card { border-top: 4px solid var(--cyan); padding-top: 10px; min-width: 0; }
  .cp2-card.warn { border-top-color: var(--amber); }
  .cp2-card.good { border-top-color: var(--green); }
  .cp2-card h3 { margin: 0 0 6px; font: 800 12px/1.2 ui-monospace, Menlo, monospace; text-transform: uppercase; letter-spacing: .05em; color: var(--navy); }
  .cp2-card p { margin: 0 0 6px; color: var(--muted); font-size: 14px; line-height: 1.32; }
  .cp2-cols-3 .cp2-card p { font-size: 16px; line-height: 1.4; }
  .cp2-card b.big { display: block; color: var(--navy); font-size: 26px; line-height: 1.1; margin: 2px 0 4px; }
  .cp2-band { margin-top: 18px; padding: 13px 22px; border-radius: 10px; background: var(--navy); color: white; font-size: 18px; font-weight: 800; text-align: center; }
  .cp2-band.light { background: #dceff7; color: var(--ink); font-size: 15px; }
  .cp2-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
  .cp2-table th { text-align: left; font: 800 10.5px ui-monospace, Menlo, monospace; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); padding: 6px 8px; border-bottom: 2px solid var(--line); }
  .cp2-table td { padding: 6px 8px; border-bottom: 1px solid var(--line); vertical-align: top; color: var(--ink); }
  .cp2-table.tight td { white-space: nowrap; padding: 6px 6px; }
  .cp2-table td.id { white-space: nowrap; font-family: ui-monospace, Menlo, monospace; font-size: 12.5px; }
  .cp2-table td.n { text-align: right; font-variant-numeric: tabular-nums; font-family: ui-monospace, Menlo, monospace; white-space: nowrap; }
  .cp2-table tr.hl td { background: #e4f2f8; font-weight: 700; }
  .cp2-chip { display: inline-block; padding: 1px 8px; border-radius: 999px; font: 800 10.5px/1.6 ui-monospace, Menlo, monospace; white-space: nowrap; }
  .cp2-chip.ok { background: #dff3e9; color: #1d6b45; }
  .cp2-chip.bad { background: #fbe1dc; color: #9b2c1f; }
  .cp2-chip.mid { background: #fdf0d2; color: #7d5300; }
  .cp2-lead { font-size: 18px; line-height: 1.35; color: var(--ink); margin: 0 0 12px; }
  .cp2-lead b { color: var(--navy); }
  .cp2-list { margin: 0; padding-left: 18px; color: var(--ink); font-size: 14.5px; line-height: 1.4; }
  .cp2-list li { margin-bottom: 5px; }
  .cp2-note { font-size: 12.5px; color: var(--muted); margin-top: 6px; }
  .cp2 svg text { font-family: ui-monospace, Menlo, monospace; fill: #4f6477; font-size: 12.5px; }
  .cp2 svg text.lbl { fill: #103b5e; font-size: 13px; font-weight: 700; }
  .cp2-flow { display: grid; gap: 8px; }
  .cp2-step { display: grid; grid-template-columns: 210px 1fr; gap: 12px; align-items: center; padding: 7px 10px; border-left: 4px solid var(--cyan); background: #f1f8fb; }
  .cp2-step b { font-size: 14px; color: var(--navy); }
  .cp2-step span { font-size: 13.5px; color: var(--ink); }
  .cp2-step.yes { border-left-color: var(--amber); }
  .start-actions.cp2-actions { grid-template-columns: 1fr 1fr; margin-top: 10px; }
  .cp2-config { margin-top: 8px; font: 600 11px ui-monospace, Menlo, monospace; opacity: .75; }

  /* ---------- film ---------- */
  .slide.fx-film { padding: 0 !important; background: #0a0a0a !important; overflow: hidden; color: #f3ead8; }
  .slide.fx-film::before { display: none; }
  .fx-frame { position: absolute; inset: 0; overflow: hidden; background: #111; }
  .fx-img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform-origin: 50% 50%; }
  .fx-img.missing { display: none; }
  .fx-ph { position: absolute; inset: 6%; display: none; place-content: center; text-align: center; gap: 10px; border: 2px dashed rgba(243,234,216,.35); border-radius: 6px; background: repeating-linear-gradient(135deg, #1a1a1a 0 14px, #161616 14px 28px); }
  .fx-img.missing + .fx-ph { display: grid; }
  .fx-ph b { font: 700 28px ui-monospace, Menlo, monospace; letter-spacing: .06em; color: #f3ead8; }
  .fx-ph span { font: 500 15px/1.4 Inter, system-ui, sans-serif; color: rgba(243,234,216,.75); max-width: 46ch; margin: 0 auto; }
  .fx-kb-in { animation: fxKbIn var(--dur) linear forwards; }
  .fx-kb-out { animation: fxKbOut var(--dur) linear forwards; }
  .fx-kb-left { animation: fxKbLeft var(--dur) linear forwards; }
  .fx-pix { position: absolute; inset: 0; width: 100%; height: 100%; image-rendering: pixelated; transform-origin: 50% 50%; }
  .fx-res { position: absolute; top: 5.5%; right: 4%; z-index: 5; font: 700 12px ui-monospace, Menlo, monospace; color: #fff; background: rgba(16,35,58,.8); padding: 4px 9px; border-radius: 4px; letter-spacing: .03em; }
  .fx-silent .fx-res, .fx-res:empty { display: none; }
  @keyframes fxKbIn { from { transform: scale(1.02); } to { transform: scale(1.14) translate(-1.5%, -1%); } }
  @keyframes fxKbOut { from { transform: scale(1.16) translate(1%, 1%); } to { transform: scale(1.03); } }
  @keyframes fxKbLeft { from { transform: scale(1.12) translate(3%, 0); } to { transform: scale(1.12) translate(-3%, 0); } }
  .fx-grain, .fx-vignette, .fx-scratch { position: absolute; inset: 0; pointer-events: none; }
  .fx-vignette { background: radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,.65) 100%); }
  .fx-grain { opacity: 0; background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)' opacity='.55'/></svg>"); animation: fxGrain .5s steps(4) infinite; mix-blend-mode: overlay; }
  .fx-scratch { opacity: 0; background: linear-gradient(90deg, transparent 0 31%, rgba(255,255,255,.18) 31.1% 31.25%, transparent 31.4% 77%, rgba(255,255,255,.12) 77.1% 77.2%, transparent 77.3%); animation: fxScratch 1.3s steps(6) infinite; }
  @keyframes fxGrain { 0% { background-position: 0 0; } 25% { background-position: -40px 30px; } 50% { background-position: 30px -50px; } 75% { background-position: -20px -10px; } 100% { background-position: 10px 40px; } }
  @keyframes fxScratch { 0% { transform: translateX(0); opacity: .7; } 33% { transform: translateX(-12%); opacity: .2; } 66% { transform: translateX(9%); opacity: .6; } 100% { transform: translateX(-4%); opacity: .3; } }
  @keyframes fxFlicker { 0%,100% { filter: var(--fx-filter) brightness(1); } 8% { filter: var(--fx-filter) brightness(.86); } 12% { filter: var(--fx-filter) brightness(1.05); } 47% { filter: var(--fx-filter) brightness(.93); } 52% { filter: var(--fx-filter) brightness(1.02); } }
  .fx-silent .fx-frame { --fx-filter: grayscale(1) sepia(.38) contrast(1.12); filter: var(--fx-filter); animation: fxFlicker 1.7s infinite; }
  .fx-silent .fx-grain, .fx-silent .fx-scratch, .fx-transition .fx-grain { opacity: 1; }
  .fx-transition .fx-frame { animation: fxColour var(--dur) ease-in forwards; }
  @keyframes fxColour { 0% { filter: grayscale(1) sepia(.38) contrast(1.1); } 55% { filter: grayscale(.85) sepia(.2); } 100% { filter: grayscale(0) sepia(0); } }
  .fx-iris-in .fx-frame { animation-name: fxFlicker, fxIrisIn; animation-duration: 1.7s, 1.2s; animation-iteration-count: infinite, 1; animation-timing-function: linear, ease-out; }
  @keyframes fxIrisIn { from { clip-path: circle(0% at 50% 50%); } to { clip-path: circle(75% at 50% 50%); } }
  .fx-card { position: absolute; inset: 0; display: grid; place-items: center; background: #0b0b0b; z-index: 6; transition: opacity .7s ease; }
  .fx-card.gone { opacity: 0; pointer-events: none; }
  .fx-card .fx-card-in { width: 74%; padding: 4.5% 6%; text-align: center; border: 3px double rgba(243,234,216,.75); outline: 1px solid rgba(243,234,216,.35); outline-offset: 10px; font-family: "Limelight", "Didot", "Bodoni 72", Georgia, serif; font-size: clamp(20px, 3.6vw, 44px); line-height: 1.25; color: #f3ead8; text-wrap: balance; }
  .fx-card .fx-card-in small { display: block; margin-top: 18px; font-size: .45em; letter-spacing: .18em; text-transform: uppercase; opacity: .8; }
  .fx-caption { position: absolute; left: 5%; right: 5%; bottom: 7%; z-index: 5; text-align: center; font-family: "Limelight", "Didot", "Bodoni 72", Georgia, serif; font-size: clamp(16px, 2.2vw, 28px); color: #f3ead8; text-shadow: 0 2px 8px rgba(0,0,0,.85); text-wrap: balance; opacity: 0; transition: opacity .8s ease; }
  .fx-caption.on { opacity: 1; }
  .fx-anime .fx-caption { left: 4%; right: auto; max-width: 62%; bottom: 6%; text-align: left; font: 700 clamp(15px, 2vw, 24px)/1.3 Inter, system-ui, sans-serif; color: #10233a; text-shadow: none; background: #fff; border: 3px solid #10233a; border-radius: 18px; padding: 14px 20px; box-shadow: 6px 6px 0 #10233a; }
  .fx-anime .fx-caption::after { content: ""; position: absolute; left: 34px; bottom: -18px; border: 9px solid transparent; border-top: 12px solid #10233a; }
  .fx-kicker { position: absolute; top: 6%; left: 4%; z-index: 5; font: 400 clamp(18px, 2.6vw, 34px) "Bangers", Impact, "Arial Black", sans-serif; letter-spacing: .04em; color: #fff; background: #e2483d; padding: 4px 14px 2px; transform: rotate(-2deg); box-shadow: 4px 4px 0 #10233a; display: none; }
  .fx-anime .fx-kicker { display: block; }
  .fx-burst { position: absolute; inset: -20%; z-index: 4; pointer-events: none; opacity: 0; background: repeating-conic-gradient(from 0deg, rgba(255,255,255,.75) 0deg 2deg, transparent 2deg 9deg); -webkit-mask: radial-gradient(circle, transparent 28%, #000 62%); mask: radial-gradient(circle, transparent 28%, #000 62%); }
  .fx-anime .fx-burst { animation: fxBurst 1.1s ease-out; }
  @keyframes fxBurst { 0% { opacity: .95; transform: scale(1.2) rotate(0deg); } 100% { opacity: 0; transform: scale(1) rotate(6deg); } }
  .fx-leader { position: absolute; inset: 0; z-index: 7; display: grid; place-items: center; background: #1a1714; }
  .fx-leader .ring { width: 34vmin; height: 34vmin; border-radius: 50%; border: 3px solid rgba(243,234,216,.8); display: grid; place-items: center; position: relative; overflow: hidden; }
  .fx-leader .ring::before { content: ""; position: absolute; inset: 0; background: conic-gradient(rgba(243,234,216,.28) var(--sweep, 0deg), transparent 0); }
  .fx-leader .ring b { position: relative; font: 400 18vmin/1 "Limelight", "Didot", Georgia, serif; color: #f3ead8; }
  .fx-leader .cross { position: absolute; inset: 0; background: linear-gradient(rgba(243,234,216,.25), rgba(243,234,216,.25)) center/100% 1px no-repeat, linear-gradient(rgba(243,234,216,.25), rgba(243,234,216,.25)) center/1px 100% no-repeat; }
  .fx-end { position: absolute; inset: 0; z-index: 8; display: grid; place-content: center; gap: 22px; text-align: center; background: #0b0b0b; opacity: 0; transition: opacity 1s ease; padding: 0 8%; }
  .fx-end.on { opacity: 1; }
  .fx-end h2 { margin: 0; font: 400 clamp(30px, 5.4vw, 66px)/1.1 "Limelight", "Didot", Georgia, serif; color: #f3ead8; }
  .fx-end p { margin: 0; font: 600 clamp(15px, 1.8vw, 22px)/1.4 Inter, system-ui, sans-serif; color: #f3ead8; }
  .fx-end p.small { font-weight: 500; font-size: clamp(12px, 1.3vw, 16px); opacity: .75; }
  .fx-irisout .fx-frame { animation: fxIrisOut 2.2s ease-in forwards; animation-delay: var(--irisAt, 6s); }
  @keyframes fxIrisOut { from { clip-path: circle(75% at 50% 50%); } to { clip-path: circle(0% at 50% 50%); } }

  /* ---------- team ---------- */
  .tm .slide-body { height: 70%; display: grid; grid-template-rows: 1fr auto; gap: 16px; padding-top: 1.6%; }
  .tm-grid { display: grid; grid-template-columns: repeat(5, 1fr); grid-auto-rows: 1fr; gap: 14px; align-content: stretch; }
  .tm-card { display: grid; grid-template-columns: 1fr; justify-items: center; text-align: center; gap: 8px; align-content: center; padding: 10px 8px; border: 1px solid var(--line); border-radius: 10px; background: #f6fafc; opacity: .45; transition: opacity .3s, transform .3s, box-shadow .3s, border-color .3s; min-width: 0; }
  .tm-card.done { opacity: 1; }
  .tm-card.on { opacity: 1; transform: translateY(-3px); border-color: var(--cyan); box-shadow: 0 6px 18px rgba(16,59,94,.18); background: #fff; }
  .tm-card.new { border-style: dashed; border-color: var(--amber); }
  .tm-face { width: 68px; height: 68px; border-radius: 50%; background: #dceff7; display: grid; place-items: center; overflow: hidden; font: 800 15px ui-monospace, Menlo, monospace; color: var(--navy); }
  .tm-face img { width: 100%; height: 100%; object-fit: cover; }
  .tm-card b { display: block; font-size: 15px; line-height: 1.2; color: var(--navy); }
  .tm-card span { display: block; margin-top: 3px; font: 700 10.5px ui-monospace, Menlo, monospace; color: var(--muted); letter-spacing: .04em; }
  .tm-cap { min-height: 92px; border-radius: 12px; background: var(--navy); color: #fff; padding: 14px 20px; display: grid; gap: 6px; }
  .tm-cap .who { font: 800 12px ui-monospace, Menlo, monospace; letter-spacing: .06em; text-transform: uppercase; color: #9fd8ef; display: flex; justify-content: space-between; gap: 12px; }
  .tm-cap .who em { font-style: normal; color: #f0b95e; }
  .tm-cap .line { font-size: 20px; line-height: 1.35; font-weight: 700; }
  /* ---------- team: positions, roles, functions ---------- */
  .tm2 .slide-body { height: 73%; display: grid; grid-template-rows: auto minmax(0, 1fr); gap: 3%; padding-top: .6%; }
  .tm2-pipe { display: flex; align-items: center; gap: 3px; }
  .tm2-node { display: grid; justify-items: center; gap: 2px; flex: 0 0 auto; opacity: .45; transition: opacity .3s, transform .3s; }
  .tm2-node.on { opacity: 1; transform: translateY(-4px); }
  .tm2-node.done { opacity: 1; }
  .tm2-dot { width: 46px; height: 46px; border-radius: 50%; background: #dceff7; overflow: hidden; display: grid; place-items: center; border: 3px solid transparent; font: 800 11px ui-monospace, Menlo, monospace; color: var(--navy); }
  .tm2-dot img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 18%; transform: scale(1.5); }
  .tm2-node.on .tm2-dot { border-color: var(--cyan); }
  .tm2-node.new .tm2-dot { border-style: dashed; border-color: var(--amber); }
  .tm2-node span { font: 700 10px ui-monospace, Menlo, monospace; color: var(--muted); }
  .tm2-node.human .tm2-dot { background: var(--navy); color: #fff; font-size: 9px; text-align: center; line-height: 1.1; }
  .tm2-arrow { flex: 1 1 auto; min-width: 4px; height: 2px; background: var(--line); position: relative; }
  .tm2-arrow::after { content: ""; position: absolute; right: -1px; top: -4px; border: 5px solid transparent; border-left: 7px solid var(--line); }
  .tm2-main { display: grid; grid-template-columns: minmax(0, 30%) minmax(0, 1fr); gap: 4%; align-items: center; min-height: 0; }
  .tm2-portrait { width: 100%; max-width: 250px; aspect-ratio: 1; justify-self: center; border-radius: 50%; background: #e6f3f9; overflow: hidden; display: grid; place-items: center; font: 800 40px ui-monospace, Menlo, monospace; color: var(--navy); }
  .tm2-portrait img { width: 100%; height: 100%; object-fit: contain; }
  .tm2-info { display: grid; gap: 8px; min-width: 0; }
  .tm2-pos { font: 700 11.5px ui-monospace, Menlo, monospace; color: var(--cyan); text-transform: uppercase; letter-spacing: .05em; }
  .tm2-info h3 { margin: 0; font-size: 28px; line-height: 1.1; color: var(--navy); }
  .tm2-role { font-size: 14px; color: var(--muted); font-weight: 700; }
  .tm2-info dl { margin: 0; display: grid; grid-template-columns: 120px 1fr; gap: 6px 12px; font-size: 14.5px; line-height: 1.35; }
  .tm2-info dt { font: 700 10.5px ui-monospace, Menlo, monospace; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); padding-top: 3px; }
  .tm2-info dd { margin: 0; color: var(--ink); }
  .tm2-line { background: var(--navy); color: #fff; border-radius: 12px; padding: 11px 16px; font-size: 17px; font-weight: 700; line-height: 1.35; display: grid; gap: 4px; }
  .tm2-line em { font: 800 10.5px ui-monospace, Menlo, monospace; color: #f0b95e; font-style: normal; text-transform: uppercase; letter-spacing: .05em; }

  /* ---------- console scene ---------- */
  .cs .slide-header .slide-subtitle { display: none; }
  .cs-stage { position: absolute; left: 3.4%; right: 2.4%; top: 17%; bottom: 6.5%; overflow: hidden; border: 1px solid var(--line); border-radius: 10px; background: #f4f8fb; }
  .cs-frame { border: 0; transform-origin: 0 0; display: block; }
  .cs-cap { position: absolute; left: 6%; right: 6%; bottom: 9%; z-index: 6; background: rgba(7,57,95,.94); color: #fff; border-radius: 10px; padding: 10px 16px; font-size: 17px; font-weight: 800; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,.25); }
  .cs-ctrl { position: absolute; top: 4.2%; right: 3%; z-index: 7; display: flex; gap: 8px; }
  .cs-ctrl button { border: 1px solid var(--line); background: #fff; color: var(--navy); border-radius: 8px; padding: 6px 12px; font: 700 12.5px Inter, system-ui, sans-serif; cursor: pointer; }
  .cs-ctrl button.primary { background: var(--navy); color: #fff; border-color: var(--navy); }
  @media (prefers-reduced-motion: reduce) { .fx-img, .fx-frame, .fx-grain, .fx-scratch, .fx-burst { animation: none !important; } }
  `;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  // ------------------------------------------------------------ helpers
  const card = (title, big, text, cls = "") =>
    `<div class="cp2-card ${cls}"><h3>${title}</h3>${big ? `<b class="big">${big}</b>` : ""}<p>${text}</p></div>`;
  const chip = (text, cls) => `<span class="cp2-chip ${cls}">${text}</span>`;
  const T = (from, to) => ({ timing: `${from} to ${to}`, naturalTiming: `${from} to ${to}` });
  const cp2 = (o) => ({ type: "cp2", cue: "", script: [], sources: [["Repository", repo]], ...o });
  const byNumber = n => JSON.parse(JSON.stringify(original[n - 1]));
  const media = name => CONFIG.mediaDir + name;
  const img = n => media(`img-${String(n).padStart(2, "0")}.${CONFIG.imageExt}`);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function rangeChart(rows) {
    const W = 600, rowH = 40, top = 18, left = 182, right = 16;
    const H = top + rows.length * rowH + 26;
    const lo = -90000, hi = 680000;
    const x = v => left + ((v - lo) / (hi - lo)) * (W - left - right);
    let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Profit ranges per tender under two assumption profiles">`;
    for (const t of [0, 200000, 400000, 600000]) {
      svg += `<line x1="${x(t)}" x2="${x(t)}" y1="${top - 6}" y2="${H - 22}" stroke="#c9e1ec" stroke-width="1" ${t === 0 ? 'stroke-dasharray="3 3" stroke="#5d7388"' : ""}/>`;
      svg += `<text x="${x(t)}" y="${H - 6}" text-anchor="middle">${t === 0 ? "€0" : "€" + t / 1000 + "k"}</text>`;
    }
    rows.forEach((r, i) => {
      const y = top + i * rowH;
      svg += `<text class="lbl" x="${left - 10}" y="${y + 16}" text-anchor="end">${r.id}</text>`;
      [[r.c1, "#0f7fb0", 7], [r.cons, "#c2702a", 21]].forEach(([d, col, dy]) => {
        svg += `<line x1="${x(d[0])}" x2="${x(d[2])}" y1="${y + dy}" y2="${y + dy}" stroke="${col}" stroke-width="3" stroke-linecap="round"/>`;
        svg += `<circle cx="${x(d[1])}" cy="${y + dy}" r="5" fill="${col}" stroke="#f8fbfd" stroke-width="2"/>`;
      });
    });
    return svg + "</svg>";
  }

  function roiChart() {
    const a36 = { 0: -13800, 3: -10785, 6: -765, 9: 9255, 12: 19275, 15: 29295, 18: 39315, 21: 49335, 24: 59355, 27: 69375, 30: 79395, 33: 89415, 36: 99435 };
    const b36 = { 0: -13800, 3: -4035, 6: 19485, 9: 43005, 12: 66525, 15: 90045, 18: 113565, 21: 137085, 24: 160605, 27: 184125, 30: 207645, 33: 231165, 36: 254685 };
    const W = 700, H = 300, L = 62, R = 76, Tp = 14, B = 30;
    const lo = -40000, hi = 260000;
    const x = m => L + (m / 36) * (W - L - R);
    const y = v => Tp + (1 - (v - lo) / (hi - lo)) * (H - Tp - B);
    const path = obj => Object.entries(obj).map(([m, v], i) => `${i ? "L" : "M"}${x(+m)},${y(v)}`).join("");
    let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Cumulative net position over 36 months">`;
    for (const v of [0, 100000, 200000]) {
      s += `<line x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}" stroke="${v === 0 ? "#5d7388" : "#c9e1ec"}" stroke-width="1" ${v === 0 ? 'stroke-dasharray="3 3"' : ""}/>`;
      s += `<text x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${v === 0 ? "€0" : "€" + v / 1000 + "k"}</text>`;
    }
    for (const m of [0, 6, 12, 18, 24, 30, 36]) s += `<text x="${x(m)}" y="${H - 8}" text-anchor="middle">m${m}</text>`;
    s += `<path d="${path(b36)}" fill="none" stroke="#c2702a" stroke-width="2.5" stroke-dasharray="6 4"/>`;
    s += `<path d="${path(a36)}" fill="none" stroke="#0f7fb0" stroke-width="3"/>`;
    s += `<circle cx="${x(7)}" cy="${y(2575)}" r="5" fill="#0f7fb0" stroke="#f8fbfd" stroke-width="2"/><text class="lbl" x="${x(7) + 8}" y="${y(2575) + 18}">break-even, month 7</text>`;
    s += `<text class="lbl" x="${x(36) + 8}" y="${y(99435) + 4}">+€99k</text>`;
    s += `<text class="lbl" x="${x(36) + 8}" y="${y(254685) + 4}" style="fill:#c2702a">+€255k</text>`;
    return s + "</svg>";
  }

  // ------------------------------------------------------------ film style
  function styleFor(era) {
    if (CONFIG.filmStyle === "silent") return "silent";
    if (CONFIG.filmStyle === "anime") return "anime";
    if (era === "now") return "transition";
    if (era === "agents") return "anime";
    return "silent"; // leader, stone, dialup, web, end
  }
  const film = (o) => ({ type: "film", cue: "The film plays by itself.", script: [], sources: [["Repository", repo]], selfAdvance: true, music: true, ...o });

  // ------------------------------------------------------------ Act I: the film
  const s1 = film({ ...T("0:00", "0:08"), era: "leader", section: "Act I · The film", title: "actsEU presents: The Search",
    card: "actsEU presents<br>THE SEARCH", sfx: "projector",
    script: ["Silent. Let the countdown run."] });
  const s2 = film({ ...T("0:08", "0:20"), era: "stone", slot: 1, kb: "in", section: "Act I · The film", title: "40,000 BC",
    card: "40,000 BC.<br>One question:<br>where is the next opportunity?", kicker: "40,000 BC",
    what: "A stone slab shaped like a computer; a question chiselled in rock; two elders shrug.", sfx: "projector" });
  const s3 = film({ ...T("0:20", "0:32"), era: "dialup", slot: 2, kb: "left", section: "Act I · The film", title: "1996",
    card: "1996.<br>Connecting at 56k…<br>still connecting.", kicker: "1996",
    what: "Beige CRT, blinking modem, a browser frozen on its loading bar.", sfx: "dialup" });
  const s4 = film({ ...T("0:32", "0:46"), era: "web", slot: 3, kb: "out", section: "Act I · The film", title: "2006",
    card: "2006.<br>Ten blue links.<br>Then ten thousand.", kicker: "2006",
    what: "Buried in printed PDFs and dozens of browser tabs; a plain search box.", sfx: "projector" });
  const s5 = film({ ...T("0:46", "1:00"), era: "now", slot: 4, kb: "in", section: "Act I · The film", title: "2026",
    card: "2026.<br>25 new energy tenders this week.<br>Some already closed. Which do you bid on?", kicker: "2026",
    what: "A bid manager at night facing a wall of tender notices and a deadline clock." });
  const s6 = film({ ...T("1:00", "1:15"), era: "agents", slot: 5, kb: "out", section: "Act I · The film", title: "Tender Intelligence",
    card: "Not a machine that decides.<br>A team that prepares the decision.", kicker: "actsEU",
    caption: "Not a machine that decides. A team that prepares the decision.",
    what: "Ten small agents sort cards into BID and NO BID trays; the human holds the APPROVED stamp.", music: "fade" });

  // ------------------------------------------------------------ Act II: meet the system
  const strip = (s, scene) => {
    if (!CONFIG.presenterClips[scene]) delete s.presenterVideo;
    delete s.narrationAudio;
    return s;
  };
  const s7 = strip(byNumber(3), 7);
  Object.assign(s7, T("1:15", "1:40"), {
    section: "Act II · The problem",
    subtitle: "Over 250,000 EU public authorities spend about €2 trillion a year through public procurement.",
    cue: "Live. One sentence about yourself, then the problem.",
    script: ["I'm Walid Barakat, and I run i@work. Every year more than 250,000 public authorities in the EU spend around two trillion euros through procurement. Finding the calls is easy. Deciding which ones to bid on, with evidence, is where firms lose time and money. This system is built for that decision."],
    sources: [["European Commission: public procurement", ecProcurement], ["Repository", repo]],
  });
  const s8 = strip(byNumber(4), 8);
  Object.assign(s8, T("1:40", "2:05"), {
    section: "Act II · How it is built",
    cue: "Live. Let the architecture zoom run.",
    script: ["n8n runs the operation: schedules, webhooks, retries, delivery to Notion, Slack and Drive. Python runs the reasoning: a FastAPI service with a LangGraph state machine, a ReAct agent that calls tools over MCP, and Pinecone for grounded retrieval."],
  });

  const AGENTS = [
    { id: "A01", name: "Source validator", role: "Gatekeeper of data quality", fn: "Searches the EU Funding & Tenders API for Energy calls, normalises each record and rejects malformed ones.", io: "Raw portal results → validated tender records", line: "I pull every Energy call from the EU portal and reject broken records first." },
    { id: "A02", name: "Relevance triage", role: "First filter", fn: "Scores relevance on metadata only and decides: archive, watch or advance.", io: "Validated records → a shortlist (14 of 25 on the live run)", line: "I read the metadata only: archive, watch or advance. Last run, I advanced 14 of 25." },
    { id: "A03", name: "ReAct researcher", role: "Evidence collector", fn: "Reasons, acts and observes: chooses the next MCP tool until the evidence is enough.", io: "One shortlisted tender → an evidence set with sources", line: "I choose the next tool, read the answer, and stop when the evidence is enough." },
    { id: "A04", name: "Document intelligence", role: "Reader of the annexes", fn: "Extracts, cleans and chunks the tender documents.", io: "Attachments → structured, searchable chunks", line: "I open the annexes, clean them, and cut them into searchable chunks." },
    { id: "A05", name: "RAG grounding", role: "Librarian", fn: "Stores chunks in Pinecone and retrieves cited passages, with a labelled local fallback.", io: "Chunks and questions → cited evidence", line: "I keep those chunks in Pinecone and return evidence with its citations." },
    { id: "A06", name: "Eligibility", role: "Compliance gate", fn: "Checks the mandatory conditions against the company profile. Any failure means no bid.", io: "Evidence and company profile → pass or fail, with reasons", line: "I check the mandatory conditions. If one fails, the answer is no bid." },
    { id: "A07", name: "Technical, finance, risk", role: "Three specialists", fn: "Score delivery feasibility, margin and bid cost, and risk exposure.", io: "Eligible tender with evidence → three scored assessments", line: "We are three: can we deliver it, does it pay, and what could go wrong?" },
    { id: "A08", name: "Decision strategy", role: "Recommender", fn: "Weighs the scores into BID, CONDITIONAL BID or NO BID, with conditions written out.", io: "Scored assessments → decision and report", line: "I turn the evidence into BID, CONDITIONAL BID or NO BID, with the conditions written out." },
    { id: "A09", name: "Report and run director", role: "Delivery and receipts", fn: "Publishes the report to Drive, updates the Notion radar, alerts Slack and records the receipts.", io: "Decision and report → delivered report and receipts", line: "I publish every report to Drive, Notion and Slack, and I keep the receipts." },
    { id: "A10", name: "Portfolio strategist", role: "New in Checkpoint 2", fn: "Checks a bid is still possible, simulates 4,000 outcomes per bid, chooses the portfolio, then waits for a human.", io: "All Stage 9 decisions → a portfolio for approval", line: "I'm new. I check that a bid is still possible, simulate four thousand futures, choose the portfolio, and wait for a human." },
  ];
  const s9 = { type: "team", ...T("2:05", "3:15"), section: "Act II · Meet the team",
    title: "Ten agents, one pipeline: who does what.",
    subtitle: "",
    cue: CONFIG.voiceMode === "live" ? "Read each agent's line as it lights up, about 7 seconds each." : "Let the agents speak. Step in only if a voice fails.",
    script: AGENTS.map(a => `${a.name}: ${a.line}`), sources: [["Repository", repo]] };

  const sC = { type: "console", ...T("0:00", "1:10"), section: "Act III · Lightweight UI",
    title: "The portfolio console: the decision engine in a browser.",
    subtitle: "", cue: DEMO_MODE === "auto" ? "The walkthrough runs by itself." : "Click Run demo, or drive the console yourself. Use Next to move on.",
    script: [], sources: [["Tender Portfolio Console", repo + "/blob/main/ui/tender_portfolio_console.html"]] };

  const s10 = strip(byNumber(10), 10);
  if (!CONFIG.keepEvidenceClip) delete s10.media;
  Object.assign(s10, T("3:15", "3:45"), {
    section: "Act II · Proof",
    title: "One real autonomous run: 25 found, 14 advanced, 11 archived.",
    subtitle: "",
    cue: "Live, over the recording. Advance after about 30 seconds; the clip does not need to finish.",
    script: ["This is one real run, on the 12th of August. Twenty-five official opportunities found, fourteen advanced by the relevance agent, eleven archived. Every advanced tender ends as a PDF report, a Notion record and a Slack alert."],
  });

  const s11 = cp2({ ...T("3:45", "4:15"), section: "Act II · What the data showed",
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
    cue: "Live. This is the hinge of the story.",
    script: ["The system worked as designed, and its own data showed what was missing. The relevance agent scored all seven of these four or five out of five. It was right about relevance. But five deadlines had passed and two were prior-information notices. Checkpoint 1 recommended conditional bids on four of them and crashed on two. That is why I built Agent 10."],
    sources: [["Live-run records", repo + "/blob/main/data/live_run_2026_08_12/stage2_advanced_tenders.json"]] });

  // ------------------------------------------------------------ Act III: the decision engine
  const rows = [
    { id: "EC-ENER/2026/OP/0064", c1: [-71084, 287901, 659874], cons: [-82036, 39422, 329975] },
    { id: "EC-JRC/…/3886-EXA", c1: [-14067, 80266, 270077], cons: [-16326, 13546, 105256] },
    { id: "CINEA/2026/OP/0028", c1: [-33737, 62704, 246716], cons: [-37409, 1688, 119258] },
    { id: "ACER/2026/OP/0020", c1: [-15515, 32244, 109813], cons: [-16825, 1643, 54468] },
    { id: "CINEA/2026/OP/0015", c1: [-32347, 27537, 238589], cons: [-35448, -6391, 95699] },
    { id: "EC-ENER/2026/OP/0042", c1: [-28422, 26789, 181524], cons: [-30603, -5912, 77544] },
    { id: "ACER/2026/OP/0016", c1: [-13061, 12705, 53088], cons: [-14055, -3279, 25647] },
  ];
  const s12 = cp2({ ...T("4:15", "4:45"), section: "Act III · Stochastic modelling",
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
    cue: "Show the gap between blue and orange. That gap is model uncertainty, stated openly.",
    script: ["Agent 10 simulates four thousand outcomes for every bid. Blue uses the Checkpoint 1 assumptions; orange is a conservative profile with half the win chance and the company's own eighteen percent margin target. On blue every eligible tender looks profitable; on orange only four do. There is no win-loss history yet, so the engine always shows both."],
    sources: [["monte_carlo.py", repo + "/blob/main/src/tender_agent/decision_engine/monte_carlo.py"]] });

  const s13 = cp2({ ...T("4:45", "5:15"), section: "Act III · Optimisation",
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
    script: ["Bids compete for the same budget, the same people in the same weeks, and the same delivery capacity if several are won. The optimiser checks all 127 possible portfolios exactly. Bidding on everything overspends the budget and, on blue, risks winning more than the firm can deliver. One tender is selected under both profiles: that is the bid I would defend today."],
    sources: [["portfolio.py", repo + "/blob/main/src/tender_agent/decision_engine/portfolio.py"]] });

  const s14 = cp2({ ...T("5:15", "6:05"), section: "Act III · Working MVP, live",
    title: "Live demo: the portfolio console and the Stage 10 workflow.",
    subtitle: "Same 4,000 scenarios as the Python engine; the browser re-runs the exact optimiser on every change.",
    html: `<div class="cp2-grid cp2-cols-2">
      <div class="cp2-flow">
        <div class="cp2-step"><b>1 · Open the console</b><span>14 real tenders; 7 fail a hard gate, with the reason.</span></div>
        <div class="cp2-step"><b>2 · Switch to Conservative</b><span>The portfolio falls from 4 bids to 1.</span></div>
        <div class="cp2-step"><b>3 · Risk aversion to 4</b><span>ACER/2026/OP/0020 replaces two riskier bids.</span></div>
        <div class="cp2-step"><b>4 · Open a tender</b><span>Reasons, conditions, draft proposal outline.</span></div>
        <div class="cp2-step"><b>5 · Approve with a rationale</b><span>In n8n this resumes the Stage 10 Wait node. Nothing is submitted.</span></div>
      </div>
      <div><p class="cp2-lead">Stage 10 in n8n: aggregate Stage 9 → <b>POST /decision-engine/run</b> → Slack approval request → wait for the bid authority → record the decision.</p>
      <ul class="cp2-list"><li>Retries on the engine call; failures raise an alert.</li>
      <li>The engine is read-only, so a retry cannot duplicate anything.</li></ul>
      <p class="cp2-note">If the network fails: the backup recording, then <code>python -m tender_agent.decision_engine.cli --input data/live_run_2026_08_12/stage2_advanced_tenders.json</code></p></div>
    </div>`,
    cue: "Switch to the console tab. Five clicks, 45 seconds. If anything stalls, play the backup clip.",
    script: ["Here is the working MVP. Fourteen real tenders, seven rejected at the gate with the reason. Switch to conservative: four bids become one. Raise risk aversion: the selection changes. Open a tender: reasons, conditions and a draft proposal outline. Approve with a rationale. In n8n, that click resumes the Stage 10 wait node. The system never submits anything."],
    sources: [["Stage 10 workflow", repo + "/blob/main/workflows/n8n/stage_10_portfolio_decision_engine.json"]] });

  const s15 = cp2({ ...T("6:05", "6:45"), section: "Act III · Evaluation in LangSmith",
    title: "What improved, what failed, and what is still open.",
    subtitle: "Dataset eu-tender-decisions-v2: 23 examples, 14 of them real live-run tenders. Same evaluators for both systems.",
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
    cue: "Replace the table with the LangSmith compare-view screenshot once uploaded.",
    script: ["Both systems ran on the same dataset with the same evaluators. On the key test, rejecting tenders that cannot be bid on, Checkpoint 1 scores 0.2 and Checkpoint 2 scores 1.0. Two failures are fixed, one is confirmed and scheduled, and three things are still open. They are not hidden; each one has a place in the pilot."],
    sources: [["evaluation/langsmith.md", repo]] });

  // ------------------------------------------------------------ Act IV: the business case
  const s16 = cp2({ ...T("6:45", "7:20"), section: "Act IV · ROI and cost",
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
    script: ["For a client firm, the base case breaks even in month seven: sixty-five percent in year one, one hundred sixty-one over three years, on operational benefits alone. Across twenty thousand simulated assumption sets the first-year ROI sits between plus twenty-seven and plus one hundred forty-five percent. If every assumption lands at its worst, it never pays back, so the pilot measures hours first."],
    sources: [["analysis/roi_model.py", repo]] });

  const s17 = cp2({ ...T("7:20", "7:45"), section: "Act IV · Major risks",
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
    cue: "Name the two that already happened. Skip this scene if you are behind.",
    script: ["Twelve risks are registered. Two already happened in this project: non-biddable tenders were recommended, and credentials ended up in a shared archive. The top open risk is uncalibrated assumptions. The ethical one is an approver who trusts precise-looking numbers too much, which is why approval needs a written rationale."],
    sources: [["roi_risk_assessment.md", repo]] });

  const voiced = CONFIG.voiceMode !== "live";
  const s18 = cp2({ ...T("7:45", "8:20"), section: "Act IV · EU AI Act",
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
      <ul class="cp2-list">${voiced ? "<li>The agent voices you heard were labelled as AI-generated: transparency in practice.</li>" : ""}
      <li>Gaps before the pilot: write the marking fields; deliver the literacy module.</li>
      <li>Main uncertainty: matching named experts to proposal roles could fall under Annex III point 4. Out of scope, with a re-classification gate.</li></ul></div>
    </div>`,
    cue: "Walk the ladder top to bottom, then the one uncertainty.",
    script: [`Under the AI Act this is an AI system, not prohibited and not high-risk: it is not a safety component of energy infrastructure, it scores no person, and procurement is not an Annex III area. Two duties bind: AI literacy, and machine-readable marking of AI-generated text.${voiced ? " The agent voices you heard were labelled as AI-generated for the same reason." : ""} The one thing that would change the classification is matching named experts to roles, so that is locked out of scope.`],
    sources: [["eu_ai_act_compliance.md", repo], ["Gibson Dunn: Omnibus agreement", "https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/"]] });

  const s19 = cp2({ ...T("8:20", "8:40"), section: "Act IV · GDPR",
    title: "GDPR: proceed with conditions.",
    subtitle: "The decision is about organisations, but tender notices and annexes still carry personal data.",
    html: `<div class="cp2-grid cp2-cols-3 auto">
      ${card("Personal data", "", "Officer contacts in notices; people named in annexes and CVs; client users; the Stage 10 approver record; logs. The decision engine itself uses no personal data.")}
      ${card("Basis and DPIA", "", "Art. 6(1)(f) with an LIA; Art. 14 position open. 2 of 9 EDPB criteria met, so a DPIA before the pilot.", "warn")}
      ${card("Highest risk", "", "Annex text sent to non-EU LLM and embedding providers and kept in a vector store. Transfers need DPF certification or SCCs.", "warn")}
    </div><div class="cp2-band light">Before the pilot: PII filter before every LLM and embedding call · executed DPAs · per-tender vector deletion.</div>`,
    cue: "Three cards, then the band.",
    script: ["GDPR applies because notices and annexes name real people. The basis is legitimate interests, and a DPIA comes before the pilot. The highest risk is sending annex text to non-EU model providers and keeping it in a vector store; the fix is to strip personal data first, sign processor agreements, and delete each tender's vectors when it closes."],
    sources: [["gdpr_documentation.md", repo]] });

  const s20 = cp2({ ...T("8:40", "9:05"), section: "Act IV · Go to market",
    title: "POC → Pilot → Full deployment, each gated on evidence.",
    subtitle: "",
    html: `<div class="cp2-grid auto" style="grid-template-columns:repeat(4,1fr)">
      ${card("POC · done", "Jul–Oct 2026", "Checkpoint 1 live run; Checkpoint 2 engine, evaluation, compliance pack.", "good")}
      ${card("Harden · ~10 days", "13 Oct–6 Nov", "Rotate keys, EU hosting, PII filter, DPAs, AI marking, Stage 9 fixes, LangSmith upload.")}
      ${card("Pilot · 3 months", "9 Nov–5 Feb", "One energy engineering firm, ≤25 assessments a month, weekly portfolio run with human approval.", "warn")}
      ${card("Full deployment", "Mar 2027 →", "Multi-client, calibrated model, TED and CORDIS sources; re-classify before 2 Dec 2027.")}
    </div><div class="cp2-band light">Pilot succeeds if: ≥22 h/month saved · 0 bids on non-biddable tenders · ≥95% runs complete · 100% approvals with rationale.<br>Managed service: €10.8k setup + €1,200/month · target contribution ≈ €9k per client per year.</div>`,
    cue: "Read the success criteria and the price. This is the investor slide.",
    script: ["Ten days of hardening, then a three-month paid pilot with one energy engineering firm. It succeeds if it saves at least twenty-two hours a month, recommends no closed tenders, completes ninety-five percent of runs, and every approval carries a rationale. Commercially it is a managed service: about eleven thousand euros setup and twelve hundred a month, a target contribution of about nine thousand euros per client per year. Those are targets the pilot will test."],
    sources: [["strategic_plan.md", repo]] });

  const s21 = film({ ...T("9:05", "9:20"), era: "end", slot: 7, kb: "in", selfAdvance: false, music: "reprise", ending: true,
    section: "Recommendation", title: "Proceed to a three-month pilot, under four conditions.",
    what: "The character and the agent team, framed for an iris-out.",
    cue: "Stop talking at the end card. Invite questions.",
    script: ["So, should we proceed? Yes, to a pilot, under four conditions: measure the manual workload first, record every bid outcome, close the data-protection pre-conditions, and keep a human approving every portfolio. Thank you."] });

  const fmt = x => `${Math.floor(x / 60)}:${String(Math.round(x % 60)).padStart(2, "0")}`;
  function retime(list) {
    let t = 0;
    list.forEach(s => {
      const d = s.__dur != null ? s.__dur : timingDuration(s.timing);
      s.timing = s.naturalTiming = `${fmt(t)} to ${fmt(t + d)}`;
      t += d;
    });
  }
  let main;
  if (CONFIG.version === "B") {
    let c1;
    if (CONFIG.c1Mode === "voice" && SCRIPTS_B.c1.length) {
      // All 19 Checkpoint 1 slides, with the visuals and evidence clips as they are and your short new narration.
      c1 = SCRIPTS_B.c1.map(e => {
        const s = byNumber(e.slide);
        delete s.presenterVideo;
        const src = CONFIG.voiceDir + e.id + ".m4a";
        s.narrationAudio = { src, duration: fmt(e.seconds), playbackRate: 1 };
        s.__voice = { ...e, src, base: true };
        s.__dur = e.seconds;
        s.script = [e.text];
        s.cue = `Recorded narration ${e.id}.m4a. The slide moves on when it ends.`;
        s.section = `Act II · Checkpoint 1 · ${s.section}`;
        return s;
      });
    } else {
      // Six slides with the original narration and presenter videos, at the deck's 15-minute pace.
      c1 = CONFIG.c1Slides.map(n => {
        const s = byNumber(n);
        s.__dur = CONFIG.c1Seconds[n] || Math.round(timingDuration(s.timing));
        s.section = `Act II · Checkpoint 1 · ${s.section}`;
        s.__c1 = n;
        return s;
      });
    }
    s9.section = "Act III · Meet the team";
    const c2 = { hinge: s11, distribution: s12, portfolio: s13, console: sC, langsmith: s15, roi: s16, risks: s17, aiact: s18, gdpr: s19, plan: s20, end: s21 };
    [s11, s12, s13, s15, s16, s17, s18, s19, s20].forEach(s => { s.section = s.section.replace(/^Act (II|III|IV) · /, "Act III · "); });
    for (const e of SCRIPTS_B.c2) {
      const s = c2[e.scene];
      if (!s) continue;
      s.__dur = e.seconds;
      if (e.scene === "console") s.script = [e.text];
      if (CONFIG.c2Mode === "recorded") {
        s.__voice = { ...e, src: CONFIG.voiceDir + e.id + ".m4a", base: false };
        s.script = [e.text];
        s.cue = `Recorded narration ${e.id}.m4a.`;
      }
    }
    if (CONFIG.c2Mode !== "recorded") s11.liveStart = true;
    main = [...(CONFIG.intro ? [s1, s2, s3, s4, s5, s6] : []), ...c1, ...(CONFIG.teamScene ? [s9] : []),
      s11, s12, s13, sC, s15, s16, s17, s18, s19, s20, s21];
    retime(main);
  } else {
    main = [s1, s2, s3, s4, s5, s6, s7, s8, ...(CONFIG.teamScene ? [s9] : []), s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21];
    if (!CONFIG.teamScene) retime(main);
  }
  const MAIN = main.length;
  const RUNTIME = timingDuration(`0:00 to ${main[MAIN - 1].timing.split(" to ")[1]}`);

  // Appendix: the 19 original narrated slides, untouched apart from a label.
  const appendix = original.map((s, i) => Object.assign(s, { section: `Appendix A${i + 1} · ${s.section}`, __origIndex: i + 1 }));
  const subs = window.presentationSubtitles || {};
  const remapped = {};
  appendix.forEach((s, i) => { if (subs[s.__origIndex]) remapped[MAIN + i + 1] = subs[s.__origIndex]; });
  main.forEach((s, i) => { if (s.__c1 && subs[s.__c1]) remapped[i + 1] = subs[s.__c1]; });
  window.presentationSubtitles = remapped;
  const deck = window.presentationSlides;
  deck.splice(0, deck.length, ...main, ...appendix);

  // ------------------------------------------------------------ sound (Web Audio, original material)
  const sound = {
    ctx: null, master: null, musicGain: null, playing: false, timer: null, step: 0, next: 0, proj: null, file: null,
    ensure() {
      if (this.ctx || CONFIG.music === "off") return;
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      this.ctx = new AC();
      this.master = this.ctx.createGain(); this.master.gain.value = 0.9; this.master.connect(this.ctx.destination);
    },
    tone(freq, t, dur, vol, type = "triangle") {
      const c = this.ctx, o = c.createOscillator(), o2 = c.createOscillator(), g = c.createGain(), g2 = c.createGain();
      o.type = type; o.frequency.value = freq; o2.type = "sine"; o2.frequency.value = freq * 2; g2.gain.value = 0.25;
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.006); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      o.connect(g); o2.connect(g2); g2.connect(g); g.connect(this.musicGain || this.master);
      o.start(t); o2.start(t); o.stop(t + dur + 0.05); o2.stop(t + dur + 0.05);
    },
    startMusic() {
      if (CONFIG.music === "off" || this.playing) return;
      if (CONFIG.music === "file") {
        if (!this.file) { this.file = new Audio(CONFIG.musicFile); this.file.loop = true; this.file.volume = 0.5; }
        this.file.play().catch(() => {}); this.playing = true; return;
      }
      if (!this.ctx) return;
      if (this.ctx.state === "suspended") this.ctx.resume();
      this.musicGain = this.ctx.createGain(); this.musicGain.gain.value = 0.16; this.musicGain.connect(this.master);
      const f = m => 440 * Math.pow(2, (m - 69) / 12);
      // Original ragtime-style loop: C, A7, D7, G7. Bass on 1 and 3, chords on 2 and 4.
      const bars = [
        { bass: [48, 43], chord: [64, 67, 72], mel: [76, null, 79, 76, null, 72, 74, null] },
        { bass: [45, 40], chord: [61, 64, 67], mel: [73, null, 76, 79, null, 76, 73, null] },
        { bass: [50, 45], chord: [66, 69, 72], mel: [74, null, 78, 81, null, 78, 74, 72] },
        { bass: [43, 38], chord: [65, 67, 71], mel: [71, null, 74, 77, null, 74, 71, 67] },
      ];
      const stepDur = 60 / 108 / 2;
      this.step = 0; this.next = this.ctx.currentTime + 0.1; this.playing = true;
      this.timer = setInterval(() => {
        if (!this.ctx) return;
        while (this.next < this.ctx.currentTime + 0.35) {
          const bar = bars[Math.floor(this.step / 8) % 4], s = this.step % 8, t = this.next;
          if (s === 0) this.tone(f(bar.bass[0]), t, 0.4, 0.5);
          if (s === 4) this.tone(f(bar.bass[1]), t, 0.4, 0.45);
          if (s === 2 || s === 6) bar.chord.forEach(m => this.tone(f(m), t, 0.22, 0.16));
          if (bar.mel[s]) this.tone(f(bar.mel[s]), t, 0.3, 0.3);
          this.step += 1; this.next += stepDur;
        }
      }, 90);
    },
    stopMusic(fade = 1.2) {
      if (!this.playing) return;
      this.playing = false;
      if (this.file) { const a = this.file; const v0 = a.volume; let k = 0; const iv = setInterval(() => { k += 1; a.volume = Math.max(0, v0 * (1 - k / 10)); if (k >= 10) { clearInterval(iv); a.pause(); a.volume = v0; } }, fade * 100); return; }
      clearInterval(this.timer); this.timer = null;
      if (this.musicGain && this.ctx) { const g = this.musicGain; g.gain.setTargetAtTime(0.0001, this.ctx.currentTime, fade / 3); setTimeout(() => g.disconnect(), fade * 1500); this.musicGain = null; }
    },
    projector(on) {
      if (!this.ctx) return;
      if (on && !this.proj) {
        const c = this.ctx, len = c.sampleRate * 2, buf = c.createBuffer(1, len, c.sampleRate), d = buf.getChannelData(0);
        for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
        const src = c.createBufferSource(); src.buffer = buf; src.loop = true;
        const bp = c.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 2600; bp.Q.value = 0.9;
        const g = c.createGain(); g.gain.value = 0.012;
        const lfo = c.createOscillator(); lfo.type = "square"; lfo.frequency.value = 18;
        const depth = c.createGain(); depth.gain.value = 0.01; lfo.connect(depth); depth.connect(g.gain);
        src.connect(bp); bp.connect(g); g.connect(this.master); src.start(); lfo.start();
        this.proj = { src, lfo, g };
      } else if (!on && this.proj) {
        const p = this.proj; this.proj = null;
        p.g.gain.setTargetAtTime(0.0001, this.ctx.currentTime, 0.2);
        setTimeout(() => { try { p.src.stop(); p.lfo.stop(); } catch (e) { /* already stopped */ } }, 900);
      }
    },
    dialup() {
      if (!this.ctx) return;
      const c = this.ctx; let t = c.currentTime + 4.2;
      const pairs = { 1: [697, 1209], 9: [852, 1477], 4: [770, 1209], 2: [697, 1336], 8: [852, 1336], 0: [941, 1336], 7: [852, 1209] };
      [0, 2, 2, 8, 1, 9, 4].forEach(dg => { pairs[dg].forEach(fq => this.tone(fq, t, 0.11, 0.05, "sine")); t += 0.17; });
      t += 0.35;
      const o = c.createOscillator(), g = c.createGain(); o.type = "sawtooth";
      o.frequency.setValueAtTime(1000, t); o.frequency.linearRampToValueAtTime(2100, t + 0.6); o.frequency.setValueAtTime(1300, t + 0.8); o.frequency.linearRampToValueAtTime(2400, t + 1.6);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.025, t + 0.05); g.gain.setValueAtTime(0.025, t + 1.7); g.gain.exponentialRampToValueAtTime(0.0001, t + 2.0);
      o.connect(g); g.connect(this.master); o.start(t); o.stop(t + 2.1);
    },
    onScene(slide) {
      if (!presentationStarted) return;
      if (slide.music === true) this.startMusic();
      else if (slide.music === "fade") { this.startMusic(); }
      else if (slide.music === "reprise") { this.startMusic(); }
      else this.stopMusic();
      const silentLook = slide.type === "film" && ["silent", "transition"].includes(styleFor(slide.era));
      this.projector(silentLook && CONFIG.music !== "off");
      if (slide.sfx === "dialup" && CONFIG.music !== "off") this.dialup();
    },
  };

  // ------------------------------------------------------------ runtime state
  const fx = { timers: [], filmTimer: null, audio: null };
  const later = (fn, ms) => { const id = setTimeout(fn, ms); fx.timers.push(id); return id; };
  function clearFx() {
    fx.timers.forEach(clearTimeout); fx.timers = [];
    clearTimeout(fx.filmTimer); fx.filmTimer = null;
    try { if (window.speechSynthesis) speechSynthesis.cancel(); } catch (e) { /* no speech */ }
    if (fx.audio) { fx.audio.pause(); fx.audio = null; }
  }
  const durMs = slide => timingDuration(timingFor(slide)) * 1000;

  // ------------------------------------------------------------ renderers
  function renderCp2(slide, index) {
    canvas.innerHTML = `<section class="slide light cp2">${header(slide)}<div class="slide-body">${slide.html}</div>${footer(index)}</section>`;
  }

  // Anime style: the picture's resolution and colour depth grow with the era.
  const RAMP = { stone: { w: 192, levels: 4, mono: true }, dialup: { w: 320, levels: 6 }, web: { w: 640, levels: 16 }, now: { w: 1280, levels: 64 } };
  function resLabel(w, levels, mono) {
    const h = Math.round(w * 9 / 16), c = mono ? levels : Math.pow(levels, 3);
    return `${w} × ${h} · ${c >= 1e6 ? (c / 1e6).toFixed(1) + "M" : c.toLocaleString("en")} colours`;
  }
  function drawPixel(image, cv, w, levels, mono) {
    const h = Math.round(w * 9 / 16);
    cv.width = w; cv.height = h;
    const ctx = cv.getContext("2d");
    const iw = image.naturalWidth, ih = image.naturalHeight, tr = 16 / 9;
    let sx = 0, sy = 0, sw = iw, sh = ih;
    if (iw / ih > tr) { sw = ih * tr; sx = (iw - sw) / 2; } else { sh = iw / tr; sy = (ih - sh) / 2; }
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(image, sx, sy, sw, sh, 0, 0, w, h);
    try {
      const d = ctx.getImageData(0, 0, w, h), px = d.data, step = 255 / (levels - 1);
      const bayer = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
      const q = v => Math.round(Math.min(255, Math.max(0, v)) / step) * step;
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4, t = (bayer[(y % 4) * 4 + (x % 4)] / 16 - 0.5) * step;
        if (mono) { const g = q(0.3 * px[i] + 0.59 * px[i + 1] + 0.11 * px[i + 2] + t); px[i] = px[i + 1] = px[i + 2] = g; }
        else { px[i] = q(px[i] + t); px[i + 1] = q(px[i + 1] + t); px[i + 2] = q(px[i + 2] + t); }
      }
      ctx.putImageData(d, 0, 0);
    } catch (e) { /* opened from a local file: pixels only, no colour reduction */ }
  }
  function applyResolution(root, ramp, upgrade) {
    const im = root.querySelector(".fx-img");
    if (!im) return;
    const badge = document.createElement("div"); badge.className = "fx-res"; root.appendChild(badge);
    const go = () => {
      if (!root.isConnected || im.classList.contains("missing") || !im.naturalWidth) { badge.remove(); return; }
      const cv = document.createElement("canvas");
      cv.className = "fx-pix " + [...im.classList].filter(c => c.startsWith("fx-kb")).join(" ");
      im.after(cv); im.style.visibility = "hidden";
      if (ramp) { drawPixel(im, cv, ramp.w, ramp.levels, ramp.mono); badge.textContent = resLabel(ramp.w, ramp.levels, ramp.mono); }
      if (upgrade) {
        const steps = [[160, 6], [480, 16], [960, 64]];
        steps.forEach(([w, l], k) => later(() => { drawPixel(im, cv, w, l, false); badge.textContent = resLabel(w, l, false); }, k * 300));
        later(() => { cv.remove(); im.style.visibility = ""; badge.textContent = `${im.naturalWidth} × ${im.naturalHeight} · 16.7M colours · HD`; }, steps.length * 300 + 250);
      }
    };
    if (im.complete) go();
    else { im.addEventListener("load", go, { once: true }); im.addEventListener("error", () => badge.remove(), { once: true }); }
  }

  function renderFilm(slide, index) {
    const look = styleFor(slide.era);
    const dur = durMs(slide);
    const isLeader = slide.era === "leader";
    const kb = slide.kb ? `fx-kb-${slide.kb}` : "";
    const slotId = slide.slot ? `IMG-${String(slide.slot).padStart(2, "0")}` : "";
    const imageHtml = slide.slot
      ? `<img class="fx-img ${kb}" src="${img(slide.slot)}" alt="" onerror="this.classList.add('missing')"><div class="fx-ph"><b>${slotId}</b><span>${esc(slide.what || "")}</span></div>`
      : "";
    const showCard = look !== "anime" && slide.card && !slide.ending;
    const cardMs = Math.min(4200, dur * 0.4);
    canvas.innerHTML = `<section class="slide fx-film fx-${look}${slide.ending ? " fx-irisout" : ""}" style="--dur:${dur}ms;--irisAt:${slide.ending ? 6 : 0}s">
      <div class="fx-frame">${imageHtml}<div class="fx-vignette"></div><div class="fx-grain"></div><div class="fx-scratch"></div></div>
      <div class="fx-burst"></div>
      ${slide.kicker ? `<div class="fx-kicker">${esc(slide.kicker)}</div>` : ""}
      ${look === "anime" && (slide.caption || slide.card) ? `<div class="fx-caption">${slide.caption ? esc(slide.caption) : slide.card.replace(/<br>/g, " ")}</div>` : ""}
      ${showCard ? `<div class="fx-card"><div class="fx-card-in">${slide.card}</div></div>` : ""}
      ${isLeader ? `<div class="fx-leader"><div class="ring"><div class="cross"></div><b>3</b></div></div>` : ""}
      ${slide.ending ? `<div class="fx-end"><h2>THE END… of guessing.</h2><p>Proceed to a three-month pilot, under four conditions.</p><p class="small">Measure the manual baseline · record every bid outcome · close the GDPR pre-conditions · keep human approval</p><p class="small">walid.barakat@i-atwork.com · github.com/Walid-Barakat/eu-tender-autonomous-agent-2</p></div>` : ""}
    </section>`;
    const root = canvas.querySelector(".fx-film");
    if (!presentationStarted) return;
    if (isLeader) {
      const ring = root.querySelector(".ring"), num = ring.querySelector("b");
      let n = 3; const t0 = performance.now();
      const tick = () => {
        if (!root.isConnected) return;
        const el = (performance.now() - t0) / 1000;
        n = 3 - Math.floor(el); ring.style.setProperty("--sweep", `${(el % 1) * 360}deg`);
        if (n >= 1) { num.textContent = n; requestAnimationFrame(tick); }
        else {
          root.querySelector(".fx-leader").remove();
          const c = root.querySelector(".fx-card"); if (c) c.classList.remove("gone");
        }
      };
      const c = root.querySelector(".fx-card"); if (c) c.classList.add("gone");
      requestAnimationFrame(tick);
      return;
    }
    const ramp = look === "anime" && CONFIG.animeRamp ? RAMP[slide.era] : null;
    const upgrade = look === "anime" && slide.era === "agents";
    if (slide.slot && (ramp || upgrade)) applyResolution(root, ramp, upgrade);
    const cardEl = root.querySelector(".fx-card");
    const cap = root.querySelector(".fx-caption");
    if (cardEl) later(() => { cardEl.classList.add("gone"); if (look === "silent") root.classList.add("fx-iris-in"); }, cardMs);
    if (cap) later(() => cap.classList.add("on"), look === "anime" ? 900 : cardMs + 400);
    if (slide.ending) later(() => root.querySelector(".fx-end").classList.add("on"), 8200);
  }

  function pickVoices() {
    try {
      const all = speechSynthesis.getVoices().filter(v => /^en[-_]/i.test(v.lang));
      const pref = ["Daniel", "Samantha", "Karen", "Moira", "Tessa", "Rishi", "Arthur", "Martha", "Aaron", "Nicky", "Fred", "Alex", "Google UK English Male", "Google US English", "Google UK English Female"];
      const rank = v => { const i = pref.findIndex(p => v.name.startsWith(p)); return i < 0 ? 99 : i; };
      return all.sort((a, b) => rank(a) - rank(b));
    } catch (e) { return []; }
  }
  if (window.speechSynthesis) { try { speechSynthesis.getVoices(); speechSynthesis.onvoiceschanged = () => {}; } catch (e) { /* no speech */ } }

  function renderTeam(slide, index) {
    const img = i => media(`ag-${String(i + 1).padStart(2, "0")}.png`);
    const nodes = AGENTS.map((a, i) => `<div class="tm2-node${i === 9 ? " new" : ""}" data-i="${i}"><div class="tm2-dot"><img src="${img(i)}" alt="" onerror="this.replaceWith('${a.id}')"></div><span>${a.id}</span></div>`).join('<i class="tm2-arrow"></i>');
    const label = CONFIG.voiceMode === "live" ? "Presenter reads" : "AI-generated voice";
    canvas.innerHTML = `<section class="slide light tm2">${header(slide)}<div class="slide-body">
      <div class="tm2-pipe">${nodes}<i class="tm2-arrow"></i><div class="tm2-node human"><div class="tm2-dot">BID<br>AUTH.</div><span>Human</span></div></div>
      <div class="tm2-main"><div class="tm2-portrait" id="tm2Face"></div>
        <div class="tm2-info"><div class="tm2-pos" id="tm2Pos">Ten agents · one pipeline · one human decision</div><h3 id="tm2Name">Meet the team</h3><div class="tm2-role" id="tm2Role">Nine from Checkpoint 1, one new in Checkpoint 2</div>
          <dl><dt>Function</dt><dd id="tm2Fn">Each agent has one job and an explicit input and output contract.</dd><dt>Input → output</dt><dd id="tm2Io">Raw EU portal records → an approved bid portfolio</dd></dl>
          <div class="tm2-line"><span id="tm2Line">Each of us introduces our position, role and function.</span><em>${label}</em></div></div></div>
    </div>${footer(index)}</section>`;
    const face = canvas.querySelector("#tm2Face");
    const showFace = i => { face.innerHTML = `<img src="${img(i)}" alt="">`; face.querySelector("img").onerror = () => { face.textContent = AGENTS[i].id; }; };
    showFace(9);
    if (!presentationStarted) return;
    const nodeEls = [...canvas.querySelectorAll(".tm2-node:not(.human)")];
    const $t = id => canvas.querySelector("#" + id);
    const budget = Math.max(5000, (durMs(slide) - 1500) / AGENTS.length);
    const voices = CONFIG.voiceMode === "browser" ? pickVoices() : [];
    const pitches = [1, 0.92, 1.08, 0.98, 1.12, 0.88, 1.02, 0.95, 1.06, 1];
    const root = canvas.querySelector(".tm2");
    const play = i => {
      if (!root.isConnected) return;
      nodeEls.forEach((e, k) => { e.classList.toggle("on", k === i); e.classList.toggle("done", k < i); });
      if (i >= AGENTS.length) {
        canvas.querySelector(".tm2-node.human").classList.add("on");
        $t("tm2Pos").textContent = "Position 11 · after the Portfolio strategist";
        $t("tm2Name").textContent = "And then a human decides";
        $t("tm2Role").textContent = "Bid authority";
        $t("tm2Fn").textContent = "Approves or rejects the portfolio with a written rationale. Nothing is submitted automatically.";
        $t("tm2Io").textContent = "Portfolio for approval → approved bids";
        $t("tm2Line").textContent = "Nine agents prepare the evidence. Agent 10 prepares the portfolio. A human decides.";
        return;
      }
      const a = AGENTS[i];
      showFace(i);
      $t("tm2Pos").textContent = `Position ${i + 1} of 10 · ${i ? "after " + AGENTS[i - 1].name : "first in line"} · ${i < 9 ? "before " + AGENTS[i + 1].name : "before the bid authority"}`;
      $t("tm2Name").textContent = `${a.id} · ${a.name}`;
      $t("tm2Role").textContent = a.role;
      $t("tm2Fn").textContent = a.fn;
      $t("tm2Io").textContent = a.io;
      $t("tm2Line").textContent = `"${a.line}"`;
      const next = () => later(() => play(i + 1), 350);
      if (CONFIG.voiceMode === "browser" && window.speechSynthesis) {
        const u = new SpeechSynthesisUtterance(a.line);
        if (voices.length) u.voice = voices[i % voices.length];
        u.pitch = pitches[i]; u.rate = 1.04;
        let done = false; const fin = () => { if (!done) { done = true; next(); } };
        u.onend = fin; u.onerror = fin; later(fin, budget + 3500);
        speechSynthesis.speak(u);
      } else if (CONFIG.voiceMode === "files") {
        const au = new Audio(media(`ag-${String(i + 1).padStart(2, "0")}.mp3`)); fx.audio = au;
        let done = false; const fin = () => { if (!done) { done = true; next(); } };
        au.onended = fin; au.onerror = () => later(fin, budget); au.play().catch(() => later(fin, budget));
      } else {
        later(() => play(i + 1), budget);
      }
    };
    later(() => play(0), 900);
  }

  // Scripted walkthrough of the portfolio console: [time ms, command, caption].
  const DEMO = (() => {
    const steps = [
      [0, { cmd: "reset" }, "14 real tenders from the live run of 12 August 2026"],
      [3500, { cmd: "scroll", value: "tbody tr:has(.pill.neutral)", block: "center" }, "7 of the 14 fail a hard gate, each with its reason"],
      [4300, { cmd: "flash", value: "tbody tr:has(.pill.neutral)", ms: 4500 }, null],
      [10500, { cmd: "scroll", value: "verdict", block: "center" }, "The optimiser selects 4 bids: €458k expected profit"],
      [11300, { cmd: "flash", value: "#kpis", ms: 3500 }, null],
      [17500, { cmd: "profile", value: "conservative" }, "Conservative profile: four bids become one"],
      [18300, { cmd: "flash", value: "#verdict", ms: 3500 }, null],
      [26000, { cmd: "profile", value: "checkpoint1" }, "Back to the Checkpoint 1 profile, then raise risk aversion to 4"],
    ];
    [1, 1.5, 2, 2.5, 3, 3.5, 4].forEach((v, k) => steps.push([28000 + k * 400, { cmd: "lam", value: v }, null]));
    steps.push([31500, { cmd: "flash", value: "#verdict", ms: 4000 }, "ACER/2026/OP/0020 replaces the two CINEA bids: the bad tail now weighs more"]);
    steps.push([39500, { cmd: "open", value: "EC-JRC/SVQ/2026/MVP/3886-EXA" }, "Open a tender: reasons, conditions and a draft proposal outline"]);
    steps.push([50500, { cmd: "scroll", value: "rationale", block: "center" }, "The bid authority approves with a written rationale"]);
    const why = "Robust under both profiles. Bid EC-JRC first; confirm a consortium lead before the larger tenders.";
    for (let k = 1; k <= 12; k++) steps.push([51500 + k * 380, { cmd: "type", value: why.slice(0, Math.round(why.length * k / 12)) }, null]);
    steps.push([58000, { cmd: "approve" }, "Approved. In n8n this resumes the Stage 10 Wait node. Nothing is submitted."]);
    return steps;
  })();

  function renderConsole(slide, index) {
    canvas.innerHTML = `<section class="slide light cs">${header(slide)}
      <div class="cs-stage"><iframe class="cs-frame" title="Tender Portfolio Console" src="${CONFIG.consoleSrc}?embed=1"></iframe></div>
      <div class="cs-cap" hidden></div>
      <div class="cs-ctrl">${DEMO_MODE === "auto" ? "" : '<button type="button" class="primary" id="csRun">Run demo</button>'}<button type="button" id="csNext">Next ▶</button></div>
      ${footer(index)}</section>`;
    const stage = canvas.querySelector(".cs-stage"), frame = canvas.querySelector(".cs-frame"), cap = canvas.querySelector(".cs-cap");
    const W = 1280, k = stage.clientWidth / W;
    frame.style.width = W + "px";
    frame.style.height = Math.ceil(stage.clientHeight / k) + "px";
    frame.style.transform = `scale(${k})`;
    const send = m => { try { frame.contentWindow.postMessage({ source: "actsEU-deck", ...m }, "*"); } catch (e) { /* console not loaded */ } };
    canvas.querySelector("#csNext").addEventListener("click", () => { if (current < slides.length - 1) { current += 1; renderSlide(); } });
    let running = false;
    const run = () => {
      if (running) return; running = true;
      const btn = canvas.querySelector("#csRun"); if (btn) btn.disabled = true;
      DEMO.forEach(([t, msg, text]) => later(() => {
        send(msg);
        if (text) { cap.textContent = text; cap.hidden = false; }
      }, t));
      later(() => { cap.hidden = true; }, 66000);
    };
    const runBtn = canvas.querySelector("#csRun");
    if (runBtn) runBtn.addEventListener("click", run);
    if (DEMO_MODE === "auto" && presentationStarted) frame.addEventListener("load", () => later(run, 700), { once: true });
  }

  // Recorded narration for a scene: plays the file, shows the script as captions in step with it,
  // and moves on when it ends. A missing file falls back to captions on the target time.
  function runVoice(slide) {
    const v = slide.__voice, root = canvas.querySelector(".slide");
    if (!v || !root || !presentationStarted) return;
    clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; autoAdvanceDeadline = null;
    // Split into sentences, keeping abbreviations such as "Dr.-Ing." together.
    const safe = v.text.replace(/\b(Dr|Mr|Ms|Prof|Ing|e\.g|i\.e|vs|No)\./g, "$1\u2024");
    const parts = (safe.match(/[^.!?]+[.!?]+["”]?(\s|$)/g) || [safe]).map(x => x.trim().replace(/\u2024/g, "."));
    const total = parts.reduce((n, x) => n + x.length, 0);
    const cap = document.createElement("div");
    cap.className = "subtitle-overlay";
    // The console walkthrough has its own captions; do not stack two.
    if (slide.type !== "console") root.appendChild(cap);
    let mediaEl = v.base ? activeNarrationMedia : null;
    if (!mediaEl) {
      mediaEl = new Audio(v.src); fx.audio = mediaEl;
      if (!presentationPaused) mediaEl.play().catch(() => {});
    }
    const t0 = performance.now();
    let failed = !!mediaEl.error;
    const progress = () => (failed || !mediaEl.duration || !isFinite(mediaEl.duration))
      ? (performance.now() - t0) / (v.seconds * 1000) : mediaEl.currentTime / mediaEl.duration;
    const tick = () => {
      if (!cap.isConnected) return;
      const p = Math.min(0.999, progress());
      let acc = 0, text = parts[parts.length - 1];
      for (const x of parts) { acc += x.length; if (p < acc / total) { text = x; break; } }
      if (cap.textContent !== text) cap.textContent = text;
      const show = typeof captionsVisible === "undefined" || captionsVisible;
      cap.classList.toggle("visible", show);
      cap.classList.toggle("caption-disabled", !show);
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    const minMs = slide.type === "console" ? 67000 : 0; // let the console walkthrough finish
    const go = () => {
      if (slides[current] !== slide || !autoplayEnabled) return;
      if (presentationPaused) { later(go, 500); return; }
      const wait = minMs - (performance.now() - t0);
      if (wait > 0) { later(go, wait); return; }
      if (current < slides.length - 1) { current += 1; renderSlide(); }
    };
    mediaEl.addEventListener("ended", () => later(go, 700));
    mediaEl.addEventListener("error", () => { if (!failed) { failed = true; later(go, v.seconds * 1000); } });
    mediaEl.addEventListener("loadedmetadata", () => later(go, (mediaEl.duration / (mediaEl.playbackRate || 1)) * 1000 + 4000));
    if (failed) later(go, v.seconds * 1000);
  }

  // ------------------------------------------------------------ wrap the renderer
  const baseRender = renderSlide;
  let liveMode = false;
  renderSlide = function () {
    clearFx();
    baseRender();
    const slide = slides[current];
    if (slide.type === "cp2") renderCp2(slide, current);
    else if (slide.type === "film") renderFilm(slide, current);
    else if (slide.type === "team") renderTeam(slide, current);
    else if (slide.type === "console") renderConsole(slide, current);
    sound.onScene(slide);
    if (slide.__voice) runVoice(slide);
    // The film plays by itself in both live and rehearsal mode.
    if (slide.type === "film" && slide.selfAdvance && presentationStarted) {
      clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; autoAdvanceDeadline = null;
      const ms = durMs(slide);
      const tick = () => {
        if (slides[current] !== slide) return;
        if (presentationPaused) { fx.filmTimer = setTimeout(tick, 400); return; }
        if (current < slides.length - 1) { current += 1; renderSlide(); }
      };
      fx.filmTimer = setTimeout(tick, ms);
    }
    // Version B, live talk: the recorded part plays by itself; you take over at Checkpoint 2.
    if (slide.liveStart && liveMode && autoplayEnabled) {
      autoplayEnabled = false; clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; autoAdvanceDeadline = null; autoAdvanceRemainingMs = null;
      updateAutoplayUI("Live from here");
    }
    // Stop autoplay at the final scene so it never runs into the appendix.
    if (current === MAIN - 1 && autoplayEnabled) {
      autoplayEnabled = false; clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; autoAdvanceDeadline = null; autoAdvanceRemainingMs = null;
      updateAutoplayUI("End of main sequence");
    }
  };

  // ------------------------------------------------------------ start card
  const inner = document.querySelector("#startCard .start-inner");
  if (inner) {
    const B = CONFIG.version === "B";
    inner.querySelector("h1").textContent = "actsEU · The Search";
    const kick = inner.querySelector(".notes-kicker"); if (kick) kick.textContent = `Final presentation · version ${B ? "B" : "A"} · 10 October 2026`;
    const p = inner.querySelector("p:not(.notes-kicker):not(.start-media-note)");
    if (p) p.textContent = B
      ? `${CONFIG.intro ? "A 75-second film, " : ""}Checkpoint 1 as recorded (${CONFIG.c1Mode === "voice" ? "all 19 slides, short narration" : CONFIG.c1Slides.length + " slides, original narration"})${CONFIG.teamScene ? ", the ten agents" : ""}, then Checkpoint 2 ${CONFIG.c2Mode === "recorded" ? "recorded" : "presented live"} with the portfolio console: ${MAIN} scenes in ${fmt(RUNTIME)}. The 19 original narrated slides follow as Appendix A.`
      : `A 75-second film, the system${CONFIG.teamScene ? " and its ten agents" : ""}, the decision engine, and the business case: ${MAIN} scenes in ${fmt(RUNTIME)}. The 19 narrated Checkpoint 1 slides follow as Appendix A.`;
    const stats = inner.querySelector(".start-stats");
    if (stats) stats.innerHTML = [[String(MAIN), "scenes"], [fmt(RUNTIME), "runtime"], B ? [CONFIG.c1Mode === "voice" ? "19" : String(CONFIG.c1Slides.length), "C1 slides"] : ["10", "agents"], ["4,000", "scenarios per bid"], ["23", "eval examples"], ["19", "appendix slides"]]
      .map(([b, s]) => `<div class="start-stat"><b>${b}</b><span>${s}</span></div>`).join("");
    const actions = inner.querySelector(".start-actions");
    if (actions) {
      actions.classList.add("cp2-actions");
      actions.innerHTML = `<button class="start-button" id="startLiveButton">${B ? "Start live talk (recorded part plays, then you advance)" : "Start live talk (film plays, then you advance)"}</button><button class="start-button secondary" id="startRehearsalButton">Rehearse or record (auto-advance)</button>`;
      const cfg = document.createElement("div"); cfg.className = "cp2-config";
      cfg.textContent = `Version ${CONFIG.version}${B ? ` · C1: ${CONFIG.c1Mode} · C2: ${CONFIG.c2Mode} · Demo: ${DEMO_MODE}` : ""} · Film: ${CONFIG.filmStyle}${CONFIG.filmStyle === "anime" && CONFIG.animeRamp ? " (resolution ramp)" : ""} · Team scene: ${CONFIG.teamScene ? "on" : "off"} · Voices: ${CONFIG.voiceMode} · Music: ${CONFIG.music}`;
      actions.after(cfg);
      const mode = B ? "paced" : "natural";
      document.getElementById("startLiveButton").addEventListener("click", () => {
        sound.ensure(); liveMode = true; startPresentation(mode);
        if (!B) toggleAutoplay();
      });
      document.getElementById("startRehearsalButton").addEventListener("click", () => { sound.ensure(); liveMode = false; startPresentation(mode); });
    }
  }
  window.ACTSEU = { CONFIG, sound, scenes: MAIN, runtime: fmt(RUNTIME) };
  current = 0;
  renderSlide();
})();
