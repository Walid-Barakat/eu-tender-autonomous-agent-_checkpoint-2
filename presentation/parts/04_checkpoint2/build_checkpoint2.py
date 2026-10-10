"""Part 04: Checkpoint 2 as one self-contained, autoplay, interactive HTML.

Eleven scenes on the Checkpoint 1 deck engine (same look and controls), with the portfolio console running
inside scene 4 and its scripted walkthrough. Three ways to run it, chosen on the start card:
  * Present live:   no narration, you advance with → (scripts in Notes, N). The console waits for Run demo.
  * Narrated:       the AI rehearsal voice reads the scripts (labelled), with exact subtitles; slides advance
                    when the voice ends; the console walkthrough is synchronised to the narration.
  * Your recordings: load c2-01 … c2-11 (m4a/mp3/wav) from disk on the start card; they replace the AI voice.

Usage: python3 build_checkpoint2.py <Checkpoint 1 source folder> <out folder> [--face <face.jpg>]
Writes <out>/Checkpoint2.html.
"""
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRES = HERE.parent.parent
args = sys.argv[1:]
SRC, OUT = Path(args[0]).resolve(), Path(args[1]).resolve()
FACE = Path(args[args.index("--face") + 1]).resolve() if "--face" in args else None
# --clone <dir>: narration in Walid's own voice (voice_clone.py) instead of the rehearsal voice; same timing and cues
CLONE = Path(args[args.index("--clone") + 1]).resolve() if "--clone" in args else None
TAG = "AI voice clone of the presenter" if CLONE else "AI-generated rehearsal voice"
PLAY = "Play in my voice (AI clone)" if CLONE else "Play with narration"
OUT.mkdir(parents=True, exist_ok=True)
VOICE = HERE / "voice"
FONTS = HERE / "fonts"


def fmt(x):
    return f"{int(x // 60)}:{int(x % 60):02d}"


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


# ---------------------------------------------------------------- slides, scripts, narration
node = r"""
const vm=require('vm'),fs=require('fs');const ctx={window:{}};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),ctx);
process.stdout.write(JSON.stringify(ctx.window.C2_SLIDES));
"""
slides = json.loads(subprocess.run(["node", "-e", node, str(HERE / "checkpoint2_slides.js")], capture_output=True, check=True, text=True).stdout)
scripts = {e["id"]: e for e in json.loads((PRES / "version_b_scripts.json").read_text(encoding="utf-8"))["c2"]}
narr = json.loads((VOICE / "narration.json").read_text(encoding="utf-8"))
subs, t = {}, 0.0
CONSOLE_MIN = 68.0  # the walkthrough's last step lands at 58 s; leave time to read the approval
for i, s in enumerate(slides, start=1):
    e, n = scripts[s["id"]], narr[s["id"]]
    s["script"] = [e["text"]]
    s["narrationAudio"] = {"src": f"voice/{s['id']}.mp3", "duration": fmt(n["duration"]), "playbackRate": 1}
    s["aiVoice"] = True
    s["targetSeconds"] = e["seconds"]
    slot = max(n["duration"], CONSOLE_MIN if s["type"] == "console" else 0) + 1.2
    s["timing"] = s["naturalTiming"] = f"{fmt(t)} to {fmt(t + slot)}"
    t += slot
    subs[str(i)] = n["cues"]
NARRATED = t
LIVE = sum(e["seconds"] for e in scripts.values())
print(f"{len(slides)} scenes · narrated {fmt(NARRATED)} · live target {fmt(LIVE)}")

# ---------------------------------------------------------------- the console, offline and in embed mode
console = (PRES / "console.html").read_text(encoding="utf-8")
face_css = "\n".join(
    f'@font-face {{ font-family: "{fam}"; font-weight: {w}; font-display: swap; src: url(data:font/woff2;base64,{b64(FONTS / f"{slug}-latin-{w}-normal.woff2")}) format("woff2"); }}'
    for fam, slug, ws in [("Space Grotesk", "space-grotesk", (500, 600, 700)), ("Inter", "inter", (400, 500, 600, 700)), ("JetBrains Mono", "jetbrains-mono", (500, 700))]
    for w in ws)
console = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", console)
console, n_links = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', f"<style>{face_css}</style>", console)
assert n_links == 1 and "fonts.googleapis" not in console
console, n_embed = re.subn(r'if \(/\[\?&\]embed=1/\.test\(location\.search\)\)', "if (true)", console)
assert n_embed == 1
console_path = OUT / "console_offline.html"
console_path.write_text(console, encoding="utf-8")

assets = {f"voice/{s['id']}.mp3": ("audio/mpeg", (CLONE or VOICE) / f"{s['id']}.mp3") for s in slides}
assets["console.html"] = ("text/html", console_path)
if FACE:
    assets["face.jpg"] = ("image/jpeg", FACE)

# ---------------------------------------------------------------- styles
src_js = (PRES / "final_presentation.src.js").read_text(encoding="utf-8")
cp2_css = src_js[src_js.index("const css = `") + len("const css = `"): src_js.index("/* ---------- film ---------- */")]
cs_css = src_js[src_js.index("/* ---------- console scene ---------- */"): src_js.index("@media (prefers-reduced-motion")]
extra_css = cp2_css + cs_css + """
  .cs-cap { top: 19.5%; bottom: auto; }
  .cp2 .cp2-grid { height: auto; align-items: start; }
  .cp2-zoom { transform-origin: 0 0; }
  .narration-audio { top: auto; bottom: 7.2%; right: 2.4%; }
  .cs .ai-voice-tag { top: auto; bottom: 2.2%; right: 3%; }
  .cs-ctrl button:disabled { opacity: .45; }
  .cp2 .grow { stroke-dasharray: 1000; stroke-dashoffset: 1000; animation: cp2Grow 1.2s ease-out forwards; }
  .cp2 path.draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: cp2Draw 2.4s ease-out .3s forwards; }
  @keyframes cp2Grow { to { stroke-dashoffset: 0; } }
  @keyframes cp2Draw { to { stroke-dashoffset: 0; } }
  .cp2 .cp2-table tbody tr, .cp2 .cp2-step, .cp2 .cp2-card { animation: cp2In .5s ease-out both; }
  .cp2 .cp2-table tbody tr:nth-child(2), .cp2 .cp2-step:nth-child(2), .cp2 .cp2-card:nth-child(2) { animation-delay: .12s; }
  .cp2 .cp2-table tbody tr:nth-child(3), .cp2 .cp2-step:nth-child(3), .cp2 .cp2-card:nth-child(3) { animation-delay: .24s; }
  .cp2 .cp2-table tbody tr:nth-child(4), .cp2 .cp2-step:nth-child(4), .cp2 .cp2-card:nth-child(4) { animation-delay: .36s; }
  .cp2 .cp2-table tbody tr:nth-child(5), .cp2 .cp2-step:nth-child(5) { animation-delay: .48s; }
  .cp2 .cp2-table tbody tr:nth-child(n+6) { animation-delay: .6s; }
  @keyframes cp2In { from { opacity: 0; transform: translateY(8px); } }
  .ai-voice-tag { position: absolute; z-index: 25; right: 2.2%; top: 2.6%; font: 800 10px ui-monospace, Menlo, monospace; letter-spacing: .06em;
    text-transform: uppercase; color: #5d7388; background: rgba(255,255,255,.8); border: 1px solid #c9e1ec; border-radius: 999px; padding: 4px 9px; }
  .slide.dark .ai-voice-tag { color: #9fd8ef; background: rgba(3,31,53,.7); border-color: rgba(132,210,238,.35); }
  .cp2.dark .slide-title { color: #fff; } .cp2.dark .kicker { color: #84d2ee; }
  .c2-market { display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; margin-top: 10px; }
  .c2-stat { border-top: 4px solid #f0b95e; padding-top: 14px; animation: cp2In .6s ease-out both; }
  .c2-stat:nth-child(2) { animation-delay: .2s; } .c2-stat:nth-child(3) { animation-delay: .4s; }
  .c2-stat b { display: block; white-space: nowrap; color: #fff; font-size: 46px; line-height: 1.05; font-variant-numeric: tabular-nums; letter-spacing: -.01em; }
  .c2-stat span { display: block; margin-top: 8px; color: #cfe6f3; font-size: 18px; line-height: 1.35; }
  .c2-market-src { margin-top: 26px; color: #8fb4ca; font: 600 11px ui-monospace, Menlo, monospace; }
  .c2-now { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; padding: 8px 12px; border-radius: 12px; background: #eaf4fa; border: 1px solid var(--line); }
  .c2-now-k { font: 800 11px ui-monospace, Menlo, monospace; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-right: 6px; }
  .c2-dot { display: inline-grid; justify-items: center; gap: 2px; font: 800 9.5px ui-monospace, Menlo, monospace; color: var(--navy); }
  .c2-dot img { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; border: 2px solid var(--cyan); background: #dff3ff; }
  .c2-dot.human { align-self: center; padding: 6px 8px; border-radius: 8px; background: var(--navy); color: #f0b95e; }
  .c2-next { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 12px; }
  .c2-new { display: grid; grid-template-columns: 38px 1fr; gap: 9px; align-items: start; padding: 10px; border-radius: 12px; border: 2px dashed #9fcbe0; background: #fff; animation: cp2In .5s ease-out both; }
  .c2-new:nth-child(2) { animation-delay: .1s; } .c2-new:nth-child(3) { animation-delay: .2s; } .c2-new:nth-child(4) { animation-delay: .3s; }
  .c2-new:nth-child(5) { animation-delay: .4s; } .c2-new:nth-child(6) { animation-delay: .5s; } .c2-new:nth-child(7) { animation-delay: .6s; }
  .c2-new .c2-dot img { width: 38px; height: 38px; border: 2px dashed #f0b95e; filter: saturate(.6); opacity: .85; }
  .c2-new b { display: block; color: var(--navy); font-size: 13.5px; line-height: 1.2; }
  .c2-new p { margin: 4px 0 6px; color: var(--ink); font-size: 12px; line-height: 1.32; }
  .c2-new em { font-style: normal; font: 800 10px ui-monospace, Menlo, monospace; color: #0f7fb0; text-transform: uppercase; letter-spacing: .04em; }
  .c2-new.warn { border-color: #f0b95e; } .c2-new.warn em { color: #9b5c00; }
  .c2-new.plus { background: #f1f8fb; animation-delay: .7s; }
  .c2-plus { width: 38px; height: 38px; border-radius: 50%; display: grid; place-items: center; border: 2px dashed var(--cyan); color: var(--cyan); font: 800 22px/1 Inter, sans-serif; }
  .c2-close { display: grid; grid-template-columns: 1.25fr .75fr; gap: 5%; height: 100%; align-items: center; padding: 0 6% 0 6.5%; }
  .c2-close .kicker { color: #84d2ee; }
  .c2-close h2 { margin: 10px 0 26px; color: #fff; font-size: clamp(30px, 3.6vw, 56px); line-height: 1.05; }
  .c2-conds { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .c2-cond { border-radius: 12px; padding: 14px 16px; background: rgba(255,255,255,.07); border: 1px solid rgba(132,210,238,.3); animation: cp2In .6s ease-out both; }
  .c2-cond:nth-child(2) { animation-delay: .25s; } .c2-cond:nth-child(3) { animation-delay: .5s; } .c2-cond:nth-child(4) { animation-delay: .75s; }
  .c2-cond b { display: block; font: 800 12px ui-monospace, Menlo, monospace; letter-spacing: .08em; text-transform: uppercase; color: #f0b95e; margin-bottom: 4px; }
  .c2-cond span { color: #e8f4fb; font-size: clamp(13px, 1.25vw, 19px); line-height: 1.35; }
  .c2-thanks { display: grid; justify-items: center; text-align: center; gap: 12px; animation: cp2In .8s ease-out 1.2s both; }
  .c2-thanks .agent-me { width: min(240px, 18vw); aspect-ratio: 380 / 620; max-height: 44vh; }
  .c2-close ~ .narration-audio, .slide.dark:has(.c2-close) .narration-audio { display: none; }
  .c2-close { padding-bottom: 5%; }
  .c2-thanks .agent-me svg { width: 100%; height: 100%; overflow: visible; }
  .me-bob { animation: meBob 3.2s ease-in-out infinite; }
  @keyframes meBob { 50% { transform: translateY(-10px); } }
  .me-wave { transform-box: view-box; transform-origin: 110px -200px; animation: meWave 1.6s ease-in-out 1.6s 3; }
  @keyframes meWave { 50% { transform: rotate(-24deg); } }
  .me-bulb { animation: meBulb 1.4s ease-in-out infinite; }
  @keyframes meBulb { 50% { fill: #fff3c4; filter: drop-shadow(0 0 10px #f0b95e); } }
  .me-rings circle { animation: meRing 2.8s ease-out infinite; transform-box: fill-box; transform-origin: center; opacity: 0; }
  .me-rings circle + circle { animation-delay: 1.4s; }
  @keyframes meRing { 0% { opacity: .7; transform: scale(.85); } 100% { opacity: 0; transform: scale(1.25); } }
  .c2-thanks strong { color: #fff; font-size: clamp(22px, 2.4vw, 38px); }
  .c2-thanks span { color: #cfe6f3; font-size: clamp(12px, 1vw, 15px); line-height: 1.4; }
  .c2-thanks em { font-style: normal; font: 700 clamp(11px, .9vw, 13px) ui-monospace, Menlo, monospace; color: #84d2ee; }
  .start-actions.c2-actions { grid-template-columns: 1fr 1fr; }
  .c2-load { margin-top: 10px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; font-size: 13px; color: #9fc4da; }
  .c2-load label { cursor: pointer; border: 1px dashed rgba(132,210,238,.5); border-radius: 10px; padding: 8px 12px; color: #e8f4fb; }
  .c2-load input { display: none; }
"""

# ---------------------------------------------------------------- renderer: Checkpoint 1 engine + Checkpoint 2 scene types
js = (SRC / "presentation.js").read_text(encoding="utf-8")


def patch(old, new):
    global js
    assert js.count(old) == 1, old
    js = js.replace(old, new)


patch('else if (slide.type === "closing") renderClosing(slide,current);',
      'else if (slide.type === "closing") renderClosing(slide,current);\n  else if (slide.type === "cp2") renderCp2(slide,current);\n'
      '  else if (slide.type === "console") renderConsole(slide,current);\n  else if (slide.type === "closing2") renderClosing2(slide,current);')
patch("function attachNarration(slide, index) {\n  if (!slide.presenterVideo && !slide.narrationAudio) return false;",
      "function attachNarration(slide, index) {\n  if (!slide.presenterVideo && !slide.narrationAudio) return false;\n"
      "  if (window.C2_LIVE) return false;\n"
      "  if (slide.aiVoice) canvas.querySelector('.slide').insertAdjacentHTML('beforeend', '<div class=\"ai-voice-tag\">__TAG__</div>');")
patch("function stopActiveMedia() {", "function stopActiveMedia() {\n  if (typeof clearDemo === 'function') clearDemo();")
# never leave a slide while the narration is still speaking
patch("""  autoAdvanceTimer = setTimeout(() => {
    autoAdvanceTimer = null;
    autoAdvanceDeadline = null;
    if (current < slides.length - 1) {""", """  autoAdvanceTimer = setTimeout(() => {
    autoAdvanceTimer = null;
    autoAdvanceDeadline = null;
    const voice = activeNarrationMedia;
    if (voice && !voice.ended && !voice.paused && voice.currentTime > 0) {
      const slideAtWait = current;
      voice.addEventListener("ended", () => { if (current === slideAtWait && autoplayEnabled && !presentationPaused) { autoAdvanceRemainingMs = 900; scheduleAutoAdvance(); } }, {once: true});
      return;
    }
    if (current < slides.length - 1) {""")
patch("""      autoplayEnabled = false;
      updateAutoplayUI("Presentation complete");""", """      autoplayEnabled = false;
      updateAutoplayUI("Checkpoint 2 complete");
      try { window.parent.postMessage({source: "checkpoint2", event: "complete"}, "*"); } catch (e) {}""")
patch("const footer = index => `<div class=\"footer\"><span>EU Tender Autonomous AI Agent</span>",
      "const footer = index => `<div class=\"footer\"><span>EU Tender Autonomous AI Agent · Checkpoint 2</span>")

DEMO = r"""
// Scripted walkthrough of the portfolio console: [ms, command, caption]. Timed to the narration of c2-04.
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
  steps.push([66000, null, ""]);
  return steps;
})();
var demoTimer = null;  // var: the deck renders slide 1 before this line runs
function clearDemo() { clearInterval(demoTimer); demoTimer = null; }

function renderCp2(slide, index) {
  const faceUrl = window.embeddedAssets?.["face.jpg"] ? assetUrl("face.jpg") : "";
  canvas.innerHTML = `<section class="slide ${slide.dark ? "dark" : "light"} cp2">${header(slide)}<div class="slide-body"><div class="cp2-zoom">${slide.html.replace(/__FACE__/g, faceUrl)}</div></div>${footer(index)}</section>`;
  // The slide text was laid out for a small slide: scale it up to the screen, as far as it fits.
  const body = canvas.querySelector(".slide-body"), inner = canvas.querySelector(".cp2-zoom");
  let z = Math.min(1.6, canvas.clientWidth / 1000);
  // fit above the footer (titles of two lines push the body down)
  const foot = canvas.querySelector(".footer"), limit = () => (foot ? foot.getBoundingClientRect().top : body.getBoundingClientRect().bottom) - 6;
  const fits = () => { inner.style.zoom = z; return inner.getBoundingClientRect().bottom <= limit(); };
  while (z > 0.8 && !fits()) z -= 0.04;
  // big numbers count up once
  inner.querySelectorAll(".count[data-to]").forEach(el => {
    const to = +el.dataset.to, pre = el.dataset.prefix || "", suf = el.dataset.suffix || "", t0 = performance.now(), ms = 1400;
    const step = now => {
      const k = Math.min(1, (now - t0) / ms), v = to * (1 - Math.pow(1 - k, 3));
      el.textContent = pre + (el.dataset.fmt === "int" ? Math.round(v).toLocaleString("en-GB") : (k < 1 ? v.toFixed(to < 10 ? 1 : 0) : String(to))) + suf;
      if (k < 1 && el.isConnected) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });
}

function renderClosing2(slide, index) {
  // "AI agent me": the same mini-me robot as the team scene, with Walid's face in the helmet
  const C = "#1ea8d8", F = assetUrl("face.jpg");
  const face = window.embeddedAssets?.["face.jpg"] ? `<div class="agent-me"><svg viewBox="-190 -600 380 620" role="img" aria-label="Walid as an AI agent">
    <defs><clipPath id="meFace"><circle cx="0" cy="-22" r="96"/></clipPath><radialGradient id="meHalo"><stop offset="0" stop-color="#84d2ee" stop-opacity=".55"/><stop offset="1" stop-color="#84d2ee" stop-opacity="0"/></radialGradient></defs>
    <circle cx="0" cy="-300" r="260" fill="url(#meHalo)"/>
    <g class="me-rings" transform="translate(0,-352)"><circle r="150" fill="none" stroke="#84d2ee" stroke-width="4"/><circle r="185" fill="none" stroke="#84d2ee" stroke-width="3"/></g>
    <g class="me-bob">
      <rect x="-70" y="-60" width="34" height="70" rx="16" fill="${C}" opacity=".9"/><rect x="36" y="-60" width="34" height="70" rx="16" fill="${C}" opacity=".9"/>
      <rect x="-90" y="-220" width="180" height="170" rx="40" fill="${C}"/>
      <rect x="-56" y="-180" width="112" height="78" rx="22" fill="#eaf6ff" opacity=".95"/>
      <text x="0" y="-128" text-anchor="middle" font-family="ui-monospace, Menlo, monospace" font-weight="700" font-size="30" fill="#0f2236">AI · ME</text>
      <g transform="translate(0,-330)">
        <line x1="0" y1="-140" x2="0" y2="-172" stroke="#0f2236" stroke-width="8"/>
        <circle class="me-bulb" cx="0" cy="-180" r="16" fill="#f0b95e"/>
        <rect x="-118" y="-140" width="236" height="230" rx="70" fill="${C}"/>
        <circle cx="0" cy="-22" r="96" fill="#dff3ff"/>
        <image href="${F}" x="-104" y="-126" width="208" height="208" clip-path="url(#meFace)" preserveAspectRatio="xMidYMid slice"/>
        <circle cx="0" cy="-22" r="96" fill="none" stroke="#0f2236" stroke-width="7"/>
        <path d="M-60,-104 Q-30,-116 -6,-112" stroke="#fff" stroke-width="8" fill="none" opacity=".55" stroke-linecap="round"/>
        <rect x="-136" y="-50" width="22" height="64" rx="10" fill="${C}"/><rect x="114" y="-50" width="22" height="64" rx="10" fill="${C}"/>
      </g>
      <rect x="-128" y="-200" width="38" height="120" rx="19" fill="${C}" transform="rotate(16 -110 -200)"/>
      <g class="me-wave"><rect x="90" y="-200" width="38" height="120" rx="19" fill="${C}" transform="rotate(-150 110 -200)"/></g>
    </g></svg></div>` : "";
  canvas.innerHTML = `<section class="slide dark"><div class="c2-close">
    <div><div class="kicker">${slide.section}</div><h2>${slide.title}</h2>
      <div class="c2-conds">${slide.conditions.map(([a, b]) => `<div class="c2-cond"><b>${a}</b><span>${b}</span></div>`).join("")}</div></div>
    <div class="c2-thanks">${face}<strong>Thank you.</strong><span>Dr.-Ing. Walid Barakat · i@work<br>Principal Consultant for AI-Energy Systems and Sustainable AI Infrastructure</span>
      <em>github.com/Walid-Barakat/eu-tender-autonomous-agent-2</em></div>
  </div>${footer(index)}</section>`;
}

function renderConsole(slide, index) {
  canvas.innerHTML = `<section class="slide light cs">${header(slide)}
    <div class="cs-stage"><iframe class="cs-frame" title="Tender Portfolio Console"></iframe></div>
    <div class="cs-cap" hidden></div>
    <div class="cs-ctrl"><button type="button" class="primary" id="csRun">Run demo</button><button type="button" id="csNext">Next ▶</button></div>
    ${footer(index)}</section>`;
  const stage = canvas.querySelector(".cs-stage"), frame = canvas.querySelector(".cs-frame"), cap = canvas.querySelector(".cs-cap");
  const fit = () => {
    const W = 1280, k = stage.clientWidth / W;
    frame.style.width = W + "px"; frame.style.height = Math.ceil(stage.clientHeight / k) + "px"; frame.style.transform = `scale(${k})`;
  };
  fit();
  frame.src = assetUrl("console.html");
  const send = m => { try { frame.contentWindow.postMessage({ source: "actsEU-deck", ...m }, "*"); } catch (e) {} };
  canvas.querySelector("#csNext").addEventListener("click", () => nextSlide());
  const runBtn = canvas.querySelector("#csRun");
  const run = () => {
    if (demoTimer) return;
    runBtn.disabled = true;
    // The walkthrough follows the narration clock when there is one, so pausing pauses both.
    const voice = window.C2_LIVE ? null : activeNarrationMedia;
    let elapsed = 0, last = performance.now(), k = 0;
    demoTimer = setInterval(() => {
      const now = performance.now();
      if (!presentationPaused) elapsed += now - last;
      last = now;
      const t = voice && !voice.ended && voice.currentTime > 0 ? voice.currentTime * 1000 : elapsed;
      if (voice && voice.currentTime > 0) elapsed = t;
      while (k < DEMO.length && DEMO[k][0] <= t) {
        const [, msg, text] = DEMO[k++];
        if (msg) send(msg);
        if (text) { cap.textContent = text; cap.hidden = false; } else if (text === "") cap.hidden = true;
      }
      if (k >= DEMO.length) clearDemo();
    }, 80);
  };
  runBtn.addEventListener("click", run);
  if (presentationStarted && !window.C2_LIVE) frame.addEventListener("load", () => setTimeout(run, 150), { once: true });
}
"""
js += DEMO

START = r"""
// ---- start card: present live, narrated, or with your own recordings
(() => {
  const fmtT = s => `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, "0")}`;
  const own = document.getElementById("c2Files"), info = document.getElementById("c2FilesInfo");
  function retime() {
    let t = 0;
    slides.forEach((s, i) => {
      const d = s.__ownSeconds || timingDuration(s.timing);
      s.timing = s.naturalTiming = `${fmtT(t)} to ${fmtT(t + d)}`;
      t += d;
    });
    document.getElementById("startNaturalButton").textContent = `__PLAY__, ${fmtT(t)}`;
  }
  own.addEventListener("change", async () => {
    const found = [];
    for (const file of own.files) {
      const m = file.name.match(/c2-(\d{2})/i);
      if (!m) continue;
      const slide = slides.find(s => s.id === `c2-${m[1]}`);
      if (!slide) continue;
      const url = URL.createObjectURL(file);
      const secs = await new Promise(res => { const a = new Audio(); a.preload = "metadata"; a.onloadedmetadata = () => res(a.duration); a.onerror = () => res(0); a.src = url; });
      if (!secs) continue;
      const i = slides.indexOf(slide), cues = window.presentationSubtitles[i + 1] || [];
      const old = cues.length ? cues[cues.length - 1].end : secs, k = secs / old;
      cues.forEach(c => { c.start *= k; c.end *= k; });
      slide.narrationAudio = { src: url, duration: fmtT(secs), playbackRate: 1 };
      slide.aiVoice = false;
      slide.__ownSeconds = Math.max(secs, slide.type === "console" ? 68 : 0) + 1.2;
      found.push(`c2-${m[1]}`);
    }
    retime();
    info.textContent = found.length ? `Your recordings: ${found.sort().join(", ")}. The others keep the AI voice.` : "No files named c2-01 … c2-11 were found.";
  });
  document.getElementById("startLiveButton").addEventListener("click", () => {
    window.C2_LIVE = true;
    startPresentation("natural");
    autoplayEnabled = false; clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; autoAdvanceDeadline = null; autoAdvanceRemainingMs = null;
    updateAutoplayUI("Live: → advances");
    if (captionsVisible) toggleCaptions();
  });
  // the merged presentation can start this part directly
  window.addEventListener("message", e => {
    const m = e.data || {};
    if (m.target === "checkpoint2" && m.command === "start") {
      if (m.mode === "live") document.getElementById("startLiveButton").click(); else startPresentation("natural");
    }
  });
  const q = new URLSearchParams(location.search).get("autostart");
  if (q) { if (q === "live") document.getElementById("startLiveButton").click(); else startPresentation("natural"); }
})();
"""
js += START
js = js.replace("__TAG__", TAG).replace("__PLAY__", PLAY)
assert "</script" not in js.lower()

loader = """
window.embeddedAssets = {};
document.querySelectorAll('script[type="application/x-embedded-asset"]').forEach(tag => {
  window.embeddedAssets[tag.dataset.src] = {mime: tag.dataset.mime, node: tag};
});
window.getEmbeddedAssetUrl = source => {
  const asset = window.embeddedAssets[source];
  if (!asset) return source;
  if (!asset.url) {
    const binary = atob(asset.node.textContent.trim());
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
    asset.url = URL.createObjectURL(new Blob([bytes], {type: asset.mime}));
    asset.node.textContent = "";
  }
  return asset.url;
};
"""

# ---------------------------------------------------------------- page
html = (SRC / "presentation.html").read_text(encoding="utf-8")
css = (SRC / "presentation.css").read_text(encoding="utf-8")
html = html.replace('<link rel="stylesheet" href="presentation.css" />', f"<style>\n{css}\n{extra_css}\n</style>")
html = re.sub(r"<title>.*?</title>", "<title>Checkpoint 2 · EU Tender Autonomous AI Agent</title>", html)
html = html.replace('<p class="notes-kicker">Narrated presenter edition</p>', '<p class="notes-kicker">Checkpoint 2 · decision engine and business case</p>')
html = html.replace("<h1>EU Tender Autonomous AI Agent</h1>", "<h1>Checkpoint 2: from a good decision to a good portfolio</h1>")
html = html.replace(
    "This self-contained presentation includes every slide, image, workflow recording, presenter video, narration track, and subtitle. After one Start click, the complete presentation plays and advances automatically at your original speech speed.",
    f"Eleven scenes: what the data showed, Agent 10's simulation and portfolio optimiser, the portfolio console live, evaluation, ROI, risks, "
    f"EU AI Act, GDPR, go to market and the recommendation. Present it live ({fmt(LIVE)} target), or let it play with narration "
    f"({fmt(NARRATED)}): {'your voice, cloned by AI from your Checkpoint 1 recordings' if CLONE else 'the AI rehearsal voice'}, or your own recordings c2-01 … c2-11 loaded below.")
stats = [(len(slides), "scenes"), (fmt(LIVE), "live target"), (fmt(NARRATED), "narrated"), ("4,000", "scenarios per bid"), ("127", "portfolios checked"), ("23", "evaluation examples")]
html = re.sub(r'<div class="start-stats">.*?</div>\s*</div>\s*<div class="shortcut-list">',
              '<div class="start-stats">' + "".join(f'<div class="start-stat"><b>{b}</b><span>{l}</span></div>' for b, l in stats)
              + '</div>\n      <div class="shortcut-list">', html, flags=re.S)
html = re.sub(r'<div class="start-actions">.*?</div>',
              '<div class="start-actions c2-actions">'
              '<button class="start-button" id="startLiveButton">Present live: you speak, → advances</button>'
              f'<button class="start-button secondary" id="startNaturalButton">{PLAY}, {fmt(NARRATED)}</button>'
              '<button id="startPacedButton" hidden></button></div>'
              '<div class="c2-load"><label for="c2Files">Load my recordings (c2-01 … c2-11)</label><input type="file" id="c2Files" accept="audio/*" multiple>'
              f'<span id="c2FilesInfo">Optional. Without them the narration is the {TAG.lower().replace("ai ", "AI ")}, labelled on screen.</span></div>',
              html, flags=re.S)
html = html.replace("Evidence videos include Dock, Float, and Fullscreen controls. Floating applies only to workflow evidence and never changes the presenter speech window.",
                    "Scene 4 runs the real portfolio console inside the slide. Live, click Run demo or use the console yourself; Next ▶ moves on.")
blobs = "\n".join(f'<script type="application/x-embedded-asset" data-src="{k}" data-mime="{m}">{b64(p)}</script>' for k, (m, p) in assets.items())
html = html.replace(
    '<script src="presentation-data.js"></script>\n  <script src="subtitles-data.js"></script>\n  <script src="presentation.js"></script>',
    f"{blobs}\n<script>\n{loader}\nwindow.presentationSlides = {json.dumps(slides, ensure_ascii=False)};\n"
    f"window.presentationSubtitles = {json.dumps(subs, ensure_ascii=False)};\n</script>\n<script>\n{js}\n</script>")
assert "presentation-data.js" not in html
out = OUT / "Checkpoint2.html"
out.write_text(html, encoding="utf-8")
print(f"{out}  {out.stat().st_size / 1e6:.2f} MB")

# ---------------------------------------------------------------- fragment for the merged presentation
# The merged deck (../02_checkpoint1/build_checkpoint1.py --c2 …) runs these slides on the same engine after the team scene.
# Asset keys get a "c2/" prefix; the closing portrait reuses the team scene's face ("team/face.jpg").
embed_js = DEMO.replace('assetUrl("console.html")', 'assetUrl("c2/console.html")') \
               .replace('window.embeddedAssets?.["face.jpg"]', 'window.embeddedAssets?.["team/face.jpg"]') \
               .replace('assetUrl("face.jpg")', 'assetUrl("team/face.jpg")')
embed_slides = json.loads(json.dumps(slides))
for s in embed_slides:
    s["narrationAudio"]["src"] = "c2/" + s["narrationAudio"]["src"]
    s["c2"] = True
embed = {"slides": embed_slides, "subs": [subs[str(i)] for i in range(1, len(slides) + 1)], "css": extra_css, "js": embed_js,
         "tag": TAG, "narrated": NARRATED, "live": LIVE,
         "assets": {("c2/" + k): [m, str(p)] for k, (m, p) in assets.items() if k != "face.jpg"}}
(OUT / "checkpoint2_embed.json").write_text(json.dumps(embed, ensure_ascii=False), encoding="utf-8")
print("fragment:", OUT / "checkpoint2_embed.json")
