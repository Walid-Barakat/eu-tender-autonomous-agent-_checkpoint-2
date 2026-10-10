"""Writes CHECKPOINT2_SCRIPTS.md from version_b_scripts.json, checkpoint2_slides.js and voice/narration.json."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
sl = (HERE / "checkpoint2_slides.js").read_text(encoding="utf-8")
titles = dict(re.findall(r'id: "(c2-\d\d)"[^\n]*?\n?\s*title: "([^"]+)"', sl))
scripts = json.loads((HERE.parent.parent / "version_b_scripts.json").read_text(encoding="utf-8"))["c2"]
narr = json.loads((HERE / "voice" / "narration.json").read_text(encoding="utf-8"))
fmt = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
first, last = scripts[0]["id"], scripts[-1]["id"]
out = ["# Checkpoint 2: scripts", "",
       f"{len(scripts)} scenes. Target time when you present live: **{fmt(sum(e['seconds'] for e in scripts))}**.", "",
       f"To record your own voice: one file per scene, named as below (`{first}.m4a` … `{last}.m4a`; mp3 or wav also work). On the start card of "
       "`Checkpoint2.html`, click **Load my recordings** and select them; they replace the narration and the slides follow your timing. "
       "Speak calmly and leave half a second of silence at each end.", ""]
t = 0
for e in scripts:
    out += [f"## {e['id']} · {titles.get(e['id'], e['title'])}", "", f"*{fmt(t)}–{fmt(t + e['seconds'])} · {e['seconds']} s · file `{e['id']}.m4a`*", "", e["text"], ""]
    if e["scene"] == "console":
        out += ["Walkthrough on screen while you speak: 0 s all 14 tenders · 3.5 s the 7 gate failures · 10.5 s 4 bids, €458k · 17.5 s Conservative: 1 bid · "
                "26 s back, risk aversion to 4 · 31.5 s ACER/2026/OP/0020 replaces the two CINEA bids · 39.5 s EC-JRC opens · 50.5 s rationale typed · 58 s approved.", ""]
    t += e["seconds"]
(HERE / "CHECKPOINT2_SCRIPTS.md").write_text("\n".join(out), encoding="utf-8")
print("scripts doc:", len(scripts), "scenes", fmt(t))
