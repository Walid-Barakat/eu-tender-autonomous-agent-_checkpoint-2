"""Part 02: Checkpoint 1 as recorded, one self-contained autoplay HTML.

Whole slides only. Every selected slide keeps its complete original recording, its complete subtitle
track, its script, its image focus path and its evidence clips. Nothing is cut.

The original renderer (presentation.html / .css / .js) is inlined, and every media file is embedded
in the page as base64 and played from blob URLs, so the single HTML file works offline with no folder.
The presenter videos and the evidence clip are re-encoded at full length to keep the file small.

Usage: python3 build_checkpoint1.py <original deck source folder> <out folder> [--film <Act I film .mp4>] [--team <team_embed.json>]

With --film, the opening film plays first (Start → film → Checkpoint 1, one file). To keep that file
under 30 MB, the presenter videos and the evidence clip are then encoded a little smaller.
With --team, the agents' scene (Part 03, built by ../03_team/build_team.py) follows Checkpoint 1 by itself.
"""
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

args = sys.argv[1:]
FILM = Path(args[args.index("--film") + 1]).resolve() if "--film" in args else None
TEAM = json.loads(Path(args[args.index("--team") + 1]).read_text(encoding="utf-8")) if "--team" in args else None
# --c2 <checkpoint2_embed.json>: Checkpoint 2 (../04_checkpoint2) continues on the same engine after the team scene
C2 = json.loads(Path(args[args.index("--c2") + 1]).read_text(encoding="utf-8")) if "--c2" in args else None
assert not C2 or TEAM, "--c2 needs --team"
SRC, OUT = Path(args[0]).resolve(), Path(args[1]).resolve()
# width, crf, maxrate: smaller encodes keep the merged file under 30 MB
PRESENTER = ("480", "33", "220k") if C2 else ("480", "32", "240k") if FILM else ("640", "30", "320k")
EVIDENCE_CRF = "35" if C2 else "33" if FILM else "31"
FILM_CRF = "31" if C2 else "29"
SELECTED = [1, 3, 4, 10, 16, 18]  # original slide numbers, in order
TITLE = "Checkpoint 1 · EU Tender Autonomous AI Agent"
if "--c2" in sys.argv:
    TITLE = "EU Tender Autonomous AI Agent · Final presentation"
MIME = {".mp4": "video/mp4", ".m4a": "audio/mp4", ".jpg": "image/jpeg", ".png": "image/png", ".mp3": "audio/mpeg", ".html": "text/html"}


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def secs(v):
    m, s = v.split(":")
    return int(m) * 60 + int(s)


def fmt(x):
    return f"{int(x // 60)}:{int(x % 60):02d}"


def span(timing):
    a, b = timing.split(" to ")
    return secs(b) - secs(a)


# ---------------------------------------------------------------- original data
node = r"""
const vm=require('vm'),fs=require('fs'),p=require('path');const ctx={window:{}};const d=process.argv[1];
vm.runInNewContext(fs.readFileSync(p.join(d,'presentation-data.js'),'utf8'),ctx);
vm.runInNewContext(fs.readFileSync(p.join(d,'subtitles-data.js'),'utf8'),ctx);
process.stdout.write(JSON.stringify({slides:ctx.window.presentationSlides,subs:ctx.window.presentationSubtitles}));
"""
data = json.loads(subprocess.run(["node", "-e", node, str(SRC)], capture_output=True, check=True, text=True).stdout)

slides, subs, t_paced, t_nat = [], {}, 0, 0
for pos, n in enumerate(SELECTED, start=1):
    s = data["slides"][n - 1]
    dp, dn = span(s["timing"]), span(s["naturalTiming"])
    s["timing"] = f"{fmt(t_paced)} to {fmt(t_paced + dp)}"
    s["naturalTiming"] = f"{fmt(t_nat)} to {fmt(t_nat + dn)}"
    s["originalSlide"] = n
    t_paced, t_nat = t_paced + dp, t_nat + dn
    subs[str(pos)] = data["subs"][str(n)]  # the complete original track
    slides.append(s)
    print(f"slide {n:2d} -> {pos}  paced {dp:3d} s  natural {dn:3d} s  {len(subs[str(pos)])} subtitle cues")
print(f"runtime: {fmt(t_paced)} at the 15-minute pace, {fmt(t_nat)} at natural speed")

# ---------------------------------------------------------------- media, full length, re-encoded
MEDIA = OUT / ("media-final" if C2 else "media-compact" if FILM else "media")
MEDIA.mkdir(parents=True, exist_ok=True)
needed = []
for s in slides:
    for key in ("presenterVideo", "narrationAudio"):
        if key in s:
            needed.append(s[key]["src"])
            if s[key].get("poster"):
                needed.append(s[key]["poster"])
    for clip in s.get("media", []):
        needed += [clip["src"], clip["poster"]]
    if s.get("image"):
        needed.append(s["image"])

assets = {}
for rel in dict.fromkeys(needed):
    src, dst = SRC / rel, MEDIA / rel.replace("/", "__")
    if not dst.exists():
        if rel.startswith("presenter-media/") and rel.endswith(".mp4"):   # talking head in a small window
            ffmpeg("-i", str(src), "-vf", f"scale={PRESENTER[0]}:-2", "-c:v", "libx264", "-preset", "slow", "-crf", PRESENTER[1],
                   "-maxrate", PRESENTER[2], "-bufsize", "640k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                   "-movflags", "+faststart", str(dst))
        elif rel.startswith("media-full/") and rel.endswith(".mp4"):      # screen recording, keep it legible
            ffmpeg("-i", str(src), "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "slow", "-crf", EVIDENCE_CRF,
                   "-tune", "stillimage", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(dst))
        else:                                                              # narration audio and images as they are
            dst.write_bytes(src.read_bytes())
        if dst.suffix in (".mp4", ".m4a"):
            d_in = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                                        capture_output=True, text=True).stdout.strip())
            d_out = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dst)],
                                         capture_output=True, text=True).stdout.strip())
            assert abs(d_in - d_out) < 0.15, f"{rel}: {d_in} s became {d_out} s"
    assets[rel] = dst
    print(f"  {rel:45s} {src.stat().st_size / 1e6:6.2f} MB -> {dst.stat().st_size / 1e6:6.2f} MB")

FILM_SECS = 0
if FILM:
    film_dst = MEDIA / f"film__act1_crf{FILM_CRF}.mp4"
    if not film_dst.exists():
        ffmpeg("-i", str(FILM), "-c:v", "libx264", "-preset", "slow", "-crf", FILM_CRF, "-tune", "stillimage", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(film_dst))
    assets["film/act1.mp4"] = film_dst
    FILM_SECS = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(film_dst)],
                                     capture_output=True, text=True).stdout)
    print(f"  film                                          {FILM.stat().st_size / 1e6:6.2f} MB -> {film_dst.stat().st_size / 1e6:6.2f} MB, {FILM_SECS:.1f} s")

C1_COUNT = len(slides)
if C2:
    base_p = t_paced + (TEAM["runtime"] if TEAM else 0)
    base_n = t_nat + (TEAM["runtime"] if TEAM else 0)
    for k, s in enumerate(C2["slides"]):
        a_, b_ = s["timing"].split(" to ")
        sa, sb = secs(a_), secs(b_)
        s["timing"] = f"{fmt(base_p + sa)} to {fmt(base_p + sb)}"
        s["naturalTiming"] = f"{fmt(base_n + sa)} to {fmt(base_n + sb)}"
        slides.append(s)
        subs[str(len(slides))] = C2["subs"][k]
    for key, (mime, path) in C2["assets"].items():
        path = Path(path)
        if mime == "audio/mpeg":  # speech: 48 kbit/s mono is plenty
            dst = MEDIA / key.replace("/", "__")
            if not dst.exists():
                ffmpeg("-i", str(path), "-ac", "1", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "48k", str(dst))
            path = dst
        assets[key] = path
    print(f"  Checkpoint 2: {len(C2['slides'])} slides, narrated {fmt(C2['narrated'])}, live target {fmt(C2['live'])}")

# ---------------------------------------------------------------- renderer patches
js = (SRC / "presentation.js").read_text(encoding="utf-8")


def patch(old, new):
    global js
    assert js.count(old) == 1, old
    js = js.replace(old, new)


# keep each presenter window where it was on the original slide
patch("shell.className = `presenter-pip presenter-slide-${index + 1}`;",
      "shell.className = `presenter-pip presenter-slide-${slide.originalSlide || index + 1}`;")
# never leave a slide while the recording is still speaking: wait for its end, then a short breath
patch("""  autoAdvanceTimer = setTimeout(() => {
    autoAdvanceTimer = null;
    autoAdvanceDeadline = null;
    if (current < slides.length - 1) {""",
      """  autoAdvanceTimer = setTimeout(() => {
    autoAdvanceTimer = null;
    autoAdvanceDeadline = null;
    const voice = activeNarrationMedia;
    if (voice && !voice.ended && !voice.paused && voice.currentTime > 0) {
      const slideAtWait = current;
      voice.addEventListener("ended", () => { if (current === slideAtWait && autoplayEnabled && !presentationPaused) { autoAdvanceRemainingMs = 600; scheduleAutoAdvance(); } }, {once: true});
      return;
    }
    if (window.__beforeAdvance && window.__beforeAdvance(current)) return;
    if (current < slides.length - 1) {""")
patch("function nextSlide(){ if(current<slides.length-1){ current+=1; renderSlide(); } }",
      "function nextSlide(){ if (window.__beforeAdvance && window.__beforeAdvance(current)) return; if(current<slides.length-1){ current+=1; renderSlide(); } }")
# tell a parent page (the merged presentation) when Checkpoint 1 has finished
patch("""      autoplayEnabled = false;
      updateAutoplayUI("Presentation complete");""",
      """      autoplayEnabled = false;
      updateAutoplayUI(window.C2_IN_DECK ? "Presentation complete" : "Checkpoint 1 complete");
      try { window.parent.postMessage({source: "checkpoint1", event: "complete"}, "*"); } catch (e) {}""")
# the merged presentation can start this part without the start card
js += """
window.addEventListener("message", event => {
  const msg = event.data || {};
  if (msg.target === "checkpoint1" && msg.command === "start") startPresentation(msg.mode === "natural" ? "natural" : "paced");
});
if (new URLSearchParams(location.search).get("autostart")) startPresentation(new URLSearchParams(location.search).get("autostart") === "natural" ? "natural" : "paced");
"""
if TEAM:
    for a_ in TEAM["assets"]:
        assets[a_["key"]] = Path(a_["path"])
    js += f"\nwindow.C1_LAST = {C1_COUNT - 1};\nwindow.C2_IN_DECK = {'true' if C2 else 'false'};\n" + TEAM["engine"] + "\n" + """
// ---- Part 03: the agents' scene follows Checkpoint 1 (it lives in a shadow root, so its styles stay its own)
(() => {
  const host = document.getElementById("teamHost");
  const root = host.attachShadow({ mode: "open" });
  root.innerHTML = "<style>" + window.TEAM_CSS + "</style>" + window.TEAM_MARKUP;
  window.__teamHost = host;
  window.__teamEngine();
  const show = () => {
    if (host.classList.contains("active")) return;
    host.classList.add("shown");
    requestAnimationFrame(() => requestAnimationFrame(() => host.classList.add("active")));
    setTimeout(() => window.__team.start(), 900);
  };
  const hide = () => {
    host.classList.remove("active");
    setTimeout(() => host.classList.remove("shown"), 800);
  };
  window.__teamBack = () => { hide(); current = window.C1_LAST; renderSlide(); };
  window.__showTeam = show;
  // when Checkpoint 1's last slide ends (or → / Next on it), the team scene takes over
  window.__beforeAdvance = idx => {
    if (idx !== window.C1_LAST || !presentationStarted || host.classList.contains("active")) return false;
    clearTimeout(autoAdvanceTimer); autoAdvanceTimer = null; autoAdvanceDeadline = null;
    if (activeNarrationMedia) activeNarrationMedia.pause();
    setTimeout(show, 400);
    return true;
  };
  // after the team: Checkpoint 2 on the same deck, narrated, or live (you present)
  window.addEventListener("message", event => {
    const m = event.data || {};
    if (m.source !== "team" || m.event !== "complete" || !window.C2_IN_DECK) return;
    setTimeout(() => {
      hide();
      current = window.C1_LAST + 1;
      if (window.C2_LIVE) {
        autoplayEnabled = false; autoAdvanceRemainingMs = null;
        updateAutoplayUI("Live: → advances");
        if (captionsVisible) toggleCaptions();
      }
      renderSlide();
    }, 1500);
  });
})();
"""
if C2:
    patch('else if (slide.type === "closing") renderClosing(slide,current);',
          'else if (slide.type === "closing") renderClosing(slide,current);\n  else if (slide.type === "cp2") renderCp2(slide,current);\n'
          '  else if (slide.type === "console") renderConsole(slide,current);\n  else if (slide.type === "closing2") renderClosing2(slide,current);')
    patch("function attachNarration(slide, index) {\n  if (!slide.presenterVideo && !slide.narrationAudio) return false;",
          "function attachNarration(slide, index) {\n  if (!slide.presenterVideo && !slide.narrationAudio) return false;\n"
          "  if (window.C2_LIVE && slide.c2) return false;\n"
          f"  if (slide.aiVoice) canvas.querySelector('.slide').insertAdjacentHTML('beforeend', '<div class=\"ai-voice-tag\">{C2['tag']}</div>');")
    patch("function stopActiveMedia() {", "function stopActiveMedia() {\n  if (typeof clearDemo === 'function') clearDemo();")
    js += "\n// ---- Checkpoint 2 scene types\n" + C2["js"] + """
// live Checkpoint 2 without the film (?film=0): the live button starts directly
document.getElementById("startLiveC2Button").addEventListener("click", () => { window.C2_LIVE = true; if (!presentationStarted) startPresentation("paced"); });
"""
if FILM:
    js += """
// ---- Act I: the opening film plays first, then Checkpoint 1 starts by itself
(() => {
  const film = document.getElementById("introFilm"), video = film.querySelector("video"), hint = document.getElementById("filmHint");
  let mode = "paced", active = false;
  const finish = () => {
    if (!active) return;
    active = false; video.pause();
    film.classList.add("fading");
    setTimeout(() => { film.classList.add("hidden"); film.classList.remove("fading"); }, 900);
    startPresentation(mode);
  };
  const play = m => {
    mode = m; active = true;
    document.getElementById("startCard").classList.add("hidden");
    film.classList.remove("hidden");
    if (!video.src) video.src = assetUrl("film/act1.mp4");
    video.currentTime = 0;
    video.play().catch(() => { hint.textContent = "Click to play the film"; hint.classList.add("show"); });
  };
  if (new URLSearchParams(location.search).get("film") === "0") return;
  document.addEventListener("click", event => {
    const button = event.target.closest("#startPacedButton, #startNaturalButton, #startLiveC2Button");
    if (!button || active) return;
    event.stopPropagation(); event.preventDefault();
    if (button.id === "startLiveC2Button") window.C2_LIVE = true;
    play(button.id === "startNaturalButton" ? "natural" : "paced");
  }, true);
  video.addEventListener("ended", finish);
  video.addEventListener("click", () => { if (video.paused) { video.play(); hint.classList.remove("show"); } else video.pause(); });
  document.getElementById("filmSkip").addEventListener("click", finish);
  document.addEventListener("keydown", event => {
    if (!active) return;
    const k = event.key.toLowerCase();
    event.stopPropagation(); event.preventDefault();
    if (k === " " || k === "p") { if (video.paused) video.play(); else video.pause(); }
    else if (["arrowright", "pagedown", "escape", "enter"].includes(k)) finish();
    else if (k === "f") { if (!document.fullscreenElement) document.documentElement.requestFullscreen?.(); else document.exitFullscreen?.(); }
  }, true);
})();
"""
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
html = html.replace('<link rel="stylesheet" href="presentation.css" />', f"<style>\n{css}\n</style>")
html = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", html)
html = html.replace("<p class=\"notes-kicker\">Narrated presenter edition</p>", "<p class=\"notes-kicker\">Checkpoint 1 · as recorded</p>")
html = html.replace(
    "This self-contained presentation includes every slide, image, workflow recording, presenter video, narration track, and subtitle. After one Start click, the complete presentation plays and advances automatically at your original speech speed.",
    f"{C1_COUNT} of the 19 Checkpoint 1 slides, each with its complete original recording, subtitles, script and evidence. "
    "Everything is inside this one file. After one Start click the slides play and advance by themselves; "
    "a slide never moves on before its recording has finished.")
if FILM:
    html = html.replace("<h1>EU Tender Autonomous AI Agent</h1>", "<h1>Act I: The Search, then Checkpoint 1</h1>")
    html = html.replace(f"{C1_COUNT} of the 19 Checkpoint 1 slides,",
                        f"The opening film (Act I: The Search, {fmt(FILM_SECS)}) plays first, then {C1_COUNT} of the 19 Checkpoint 1 slides,")
    t_paced, t_nat = t_paced + FILM_SECS, t_nat + FILM_SECS
if TEAM:
    t_paced, t_nat = t_paced + TEAM["runtime"], t_nat + TEAM["runtime"]
    html = html.replace("<h1>Act I: The Search, then Checkpoint 1</h1>", "<h1>Act I · Checkpoint 1 · Meet the team</h1>")
    html = html.replace("Everything is inside this one file.", "Then the ten mini-me agents introduce themselves. Everything is inside this one file.", 1)
if C2:
    t_paced, t_nat = t_paced + C2["narrated"], t_nat + C2["narrated"]
    html = html.replace("<h1>Act I · Checkpoint 1 · Meet the team</h1>", "<h1>EU Tender Autonomous AI Agent · Final presentation</h1>")
    html = html.replace('<p class="notes-kicker">Checkpoint 1 · as recorded</p>', '<p class="notes-kicker">Dr.-Ing. Walid Barakat · i@work · 10 October 2026</p>', 1)
    html = html.replace("Then the ten mini-me agents introduce themselves. Everything is inside this one file.",
                        f"Then the ten mini-me agents introduce themselves, and Checkpoint 2 follows: {len(C2['slides'])} scenes with the portfolio console, "
                        "narrated in your voice (AI clone, labelled) or presented live by you. Everything is inside this one file.", 1)
stats = [(C1_COUNT, "Checkpoint 1 slides"), (sum(len(s.get("media", [])) for s in slides), "evidence clip"),
         (C1_COUNT, "complete recordings"), (C1_COUNT, "subtitle tracks"),
         (fmt(t_paced), "15-minute pace"), (fmt(t_nat), "natural speed")]
if FILM:
    stats[3] = (fmt(FILM_SECS), "opening film")
if TEAM:
    stats[1] = (10, "agents introduce themselves")
if C2:
    stats[2] = (len(C2["slides"]), "Checkpoint 2 scenes")
html = re.sub(r'<div class="start-stats">.*?</div>\s*</div>\s*<div class="shortcut-list">',
              '<div class="start-stats">' + "".join(f'<div class="start-stat"><b>{b}</b><span>{l}</span></div>' for b, l in stats)
              + '</div>\n      <div class="shortcut-list">', html, flags=re.S)
html = re.sub(r'<div class="start-actions">.*?</div>',
              '<div class="start-actions">'
              f'<button class="start-button" id="startPacedButton">{"Start the whole presentation" if C2 else "Start the film, Checkpoint 1 and the team" if FILM and TEAM else "Start the film and Checkpoint 1" if FILM else "Start Checkpoint 1"} at the 15-minute pace, {fmt(t_paced)}</button>'
              f'<button class="start-button secondary" id="startNaturalButton">Start at natural speech speed, {fmt(t_nat)}</button>'
              + (f'<button class="start-button secondary" id="startLiveC2Button">Live Checkpoint 2: everything before it plays by itself, then you present ({fmt(t_paced - C2["narrated"] + C2["live"])})</button>' if C2 else '')
              + '</div>', html, flags=re.S)
if C2:
    html = html.replace("</style>", "\n" + C2["css"] + "\n.start-actions { grid-template-columns: 1fr 1fr; } #startLiveC2Button { grid-column: 1 / -1; }\n</style>", 1)
if FILM:
    html = html.replace("</style>", """
.intro-film { position: fixed; inset: 0; z-index: 200; display: grid; place-items: center; background: #000; transition: opacity .9s ease; }
.intro-film.hidden { display: none; }
.intro-film.fading { opacity: 0; }
.intro-film video { width: 100%; height: 100%; object-fit: contain; background: #000; }
.intro-film .film-skip { position: absolute; right: 18px; bottom: 16px; border: 1px solid rgba(255,255,255,.35); border-radius: 10px; padding: 8px 14px;
  color: #e8f4fb; background: rgba(3,31,53,.75); font: 600 13px Inter, sans-serif; opacity: .25; transition: opacity .3s; cursor: pointer; }
.intro-film:hover .film-skip { opacity: 1; }
.intro-film .film-label { position: absolute; left: 18px; bottom: 18px; color: rgba(232,244,251,.55); font: 600 11px Inter, sans-serif; letter-spacing: .08em; text-transform: uppercase; opacity: 0; transition: opacity .3s; }
.intro-film:hover .film-label { opacity: 1; }
.intro-film .film-hint { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%); padding: 14px 22px; border-radius: 12px; background: rgba(3,31,53,.85); color: #fff; font: 700 18px Inter, sans-serif; display: none; pointer-events: none; }
.intro-film .film-hint.show { display: block; }
</style>""", 1)
    html = html.replace('<section class="start-card', '<div class="intro-film hidden" id="introFilm"><video playsinline preload="auto"></video>'
                        '<div class="film-hint" id="filmHint"></div><span class="film-label">Act I · The Search · voices are AI-generated</span>'
                        '<button class="film-skip" id="filmSkip" type="button">Skip film ▶▶</button></div>\n  <section class="start-card', 1)
    assert 'id="introFilm"' in html

if TEAM:
    html = html.replace("</style>", "\n" + TEAM["fonts"] + "\n</style>", 1)
    html = html.replace('<section class="start-card', '<div id="teamHost"></div>\n  <section class="start-card', 1)
    team_data = f"window.TEAM_CSS = {json.dumps(TEAM['css'])};\nwindow.TEAM_MARKUP = {json.dumps(TEAM['markup'])};\n"
    assert "</script" not in team_data.lower()
    js = team_data + js

blobs = "\n".join(
    f'<script type="application/x-embedded-asset" data-src="{rel}" data-mime="{MIME[Path(rel).suffix]}">'
    f'{base64.b64encode(p.read_bytes()).decode()}</script>' for rel, p in assets.items())
html = html.replace(
    '<script src="presentation-data.js"></script>\n  <script src="subtitles-data.js"></script>\n  <script src="presentation.js"></script>',
    f"{blobs}\n<script>\n{loader}\nwindow.presentationSlides = {json.dumps(slides, ensure_ascii=False)};\n"
    f"window.presentationSubtitles = {json.dumps(subs, ensure_ascii=False)};\n</script>\n<script>\n{js}\n</script>")
assert "presentation-data.js" not in html and 'href="presentation.css"' not in html
out = OUT / ("EU_Tender_Final_Presentation.html" if C2 else "Film_Checkpoint1_Team.html" if FILM and TEAM else "Film_and_Checkpoint1.html" if FILM else "Checkpoint1_as_recorded.html")
out.write_text(html, encoding="utf-8")
print(f"{out}  {out.stat().st_size / 1e6:.1f} MB")
