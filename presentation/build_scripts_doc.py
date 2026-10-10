"""Write VERSION_B_RECORDING_SCRIPTS.md from version_b_scripts.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "version_b_scripts.json").read_text(encoding="utf-8"))
WPS = 2.5  # words per second at a calm presenting pace


def table(items):
    rows = ["| File | Slide or scene | Target | Words | At a calm pace |", "|---|---|---:|---:|---:|"]
    for it in items:
        w = len(it["text"].split())
        rows.append(f"| `{it['id']}.m4a` | {it['title']} | {it['seconds']} s | {w} | {w / WPS:.0f} s |")
    total = sum(i["seconds"] for i in items)
    rows.append(f"| | **Total** | **{total // 60}:{total % 60:02d}** | | |")
    return "\n".join(rows)


def scripts(items):
    return "\n\n".join(f"**{it['id']} · {it['title']}** ({it['seconds']} s)\n{it['text']}" for it in items)


md = f"""# Version B: recording scripts

Version B: film → Checkpoint 1 (all 19 slides, re-recorded short) → the agents' scene → Checkpoint 2 (live or recorded) → end card.
Target 14:02 for a 15-minute slot.

## How to record

1. Use QuickTime Player (File → New Audio Recording) or Voice Memos. One file per block below, named exactly as listed, saved as `.m4a`.
2. Speak at a calm pace and leave half a second of silence at the start and end. A take may run a few seconds over or under: the deck moves on when each recording ends, so nothing needs re-timing.
3. Put the files in the deck's `media-final/voice/` folder (the installer creates it). Slides without a recording show the script as captions and advance on the target time, so you can rehearse before recording.
4. Checkpoint 2 can be recorded the same way (`c2-…` files), or you present it live: choose with `--c2 live` or `--c2 recorded` when installing, or `?c2=live` in the address bar.

## Checkpoint 1: 19 slides, all kept

The slide visuals and evidence clips stay exactly as they are on eu-tender-presentation.firebaseapp.com; only the narration is shorter. It was 20:39 at normal speed and 14:44 at the deck's 15-minute pace.

{table(data["c1"])}

{scripts(data["c1"])}

## Checkpoint 2: 11 scenes, live or recorded

{table(data["c2"])}

{scripts(data["c2"])}
"""
(HERE / "VERSION_B_RECORDING_SCRIPTS.md").write_text(md, encoding="utf-8")
print("written")
