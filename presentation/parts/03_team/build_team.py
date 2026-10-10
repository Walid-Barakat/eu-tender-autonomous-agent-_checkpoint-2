"""Part 03: the agents' scene as one self-contained autoplay HTML.

Usage: python3 build_team.py <face source image> <voices folder from make_voices.py> <out folder>
The face source is Walid's cartoon (m13.jpg, "AI + Web Research Agent"); the face disc is cropped from it.
Robot shapes, colours and props come from ../../art/art.js, so the agents look as designed there.
"""
import base64
import json
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
FACE_SRC, VOICES, OUT = (Path(a).resolve() for a in sys.argv[1:4])
OUT.mkdir(parents=True, exist_ok=True)
FONTS = HERE.parent / "01_movie" / "fonts"
FACE_CIRCLE = (757, 718, 136)  # centre x, centre y, radius of the face inside the helmet of m13.jpg

# face disc
cx, cy, r = FACE_CIRCLE
face = Image.open(FACE_SRC).convert("RGB").crop((cx - r, cy - r, cx + r, cy + r)).resize((420, 420), Image.LANCZOS)
face_path = OUT / "face.jpg"
face.save(face_path, quality=90)

# robot colours and props, shared with the original artwork
art = (HERE.parent.parent / "art" / "art.js").read_text(encoding="utf-8")
colors = re.search(r"const AGENT_COLORS = \[.*?\];", art, re.S).group(0)
props = re.search(r"const PROPS = \[.*?\n\];", art, re.S).group(0)

team = json.loads((HERE / "team.json").read_text(encoding="utf-8"))
voices = json.loads((VOICES / "voices.json").read_text(encoding="utf-8"))

def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()

fonts = "\n".join(
    f'@font-face {{ font-family: {fam}; font-weight: {w}; src: url(data:font/woff2;base64,{b64(FONTS / f"{fam.lower()}-latin-{w}-normal.woff2")}) format("woff2"); }}'
    for fam, w in [("Inter", 400), ("Inter", 600), ("Oswald", 400), ("Oswald", 600)])
assets = [("face.jpg", "image/jpeg", face_path)] + [(p.name, "audio/mpeg", p) for p in sorted(VOICES.glob("vo-*.mp3"))]
tags = "\n".join(f'<script type="application/x-embedded-asset" data-src="{k}" data-mime="{m}">{b64(p)}</script>' for k, m, p in assets)

html = (HERE / "team_template.html").read_text(encoding="utf-8")
data = f"const TEAM = {json.dumps(team, ensure_ascii=False)};\nconst VOICES = {json.dumps(voices)};"
for marker, value in [("/*__FONTS__*/", fonts), ("<!--__ASSETS__-->", tags), ("/*__DATA__*/", data), ("/*__ART__*/", colors + "\n" + props)]:
    assert html.count(marker) == 1, marker
    html = html.replace(marker, value)
assert "</script" not in (data + colors + props).lower()
out = OUT / "Team_scene.html"

# ---------------------------------------------------------------- the same scene as a fragment for the merged presentation
# It runs inside a shadow root, so its styles and the deck's never meet. Fonts get their own names (TeamInter,
# TeamOswald) because @font-face must live in the page, and the deck must keep its own typography.
def between(text, start, end):
    i, j = text.index(start) + len(start), text.index(end)
    return text[i:j]

tpl = (HERE / "team_template.html").read_text(encoding="utf-8")
css = between(tpl, "/*TEAM-CSS-START*/", "/*TEAM-CSS-END*/")
for a_, b_ in [(":root {", ":host {"), ("html, body {", ":host {"), ("body.idle #bar", ":host(.idle) #bar"), ("body.no-captions #caption", ":host(.no-captions) #caption")]:
    assert a_ in css, a_
    css = css.replace(a_, b_)
css = re.sub(r"\bInter\b", "TeamInter", css)
css = re.sub(r"\bOswald\b", "TeamOswald", css)
css = (":host { position: fixed; inset: 0; z-index: 300; display: none; opacity: 0; transition: opacity .8s ease; }\n"
       ":host(.shown) { display: block; } :host(.active) { opacity: 1; }\n#start { display: none !important; }\n" + css)
embed = {
    "fonts": fonts.replace("font-family: Inter", "font-family: TeamInter").replace("font-family: Oswald", "font-family: TeamOswald"),
    "css": css,
    "markup": between(tpl, "<!--TEAM-MARKUP-START-->", "<!--TEAM-MARKUP-END-->"),
    "engine": "window.__teamEngine = () => {\n" + data + "\n" + colors + "\n" + props + "\n"
              + between(tpl, "/*TEAM-ENGINE-START*/", "/*TEAM-ENGINE-END*/") + "\n};",
    "assets": [{"key": "team/" + k, "mime": m, "path": str(p)} for k, m, p in assets],
    "runtime": round(sum(voices.values()) + 13 * 1.05, 1),
}
assert "</script" not in embed["engine"].lower()
(OUT / "team_embed.json").write_text(json.dumps(embed, ensure_ascii=False), encoding="utf-8")
out.write_text(html, encoding="utf-8")
print(f"{out}  {out.stat().st_size / 1e6:.2f} MB, {len(assets)} embedded assets, speech {sum(voices.values()):.1f} s")
