#!/usr/bin/env python3
"""Install the actsEU final presentation into the Checkpoint 1 deck.

Usage (from this folder):
    python3 install_presentation.py ~/path/to/firebase/public
    python3 install_presentation.py ~/path/to/firebase/public/index.html --version B --team off

What it does:
  1. Backs up the deck HTML once (index.html.before-actsEU.bak).
  2. Removes any earlier install of this script or of checkpoint2_merge.js.
  3. Inserts final_presentation.js, with your chosen settings, before the closing body tag.
  4. Copies media-final/ (default artwork) next to the HTML without overwriting
     images you have already placed there (use --replace-media to overwrite).
Running it again is safe: it replaces the previous install.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
START, END = "<!-- actsEU-final:start -->", "<!-- actsEU-final:end -->"
OLD_MARKERS = (
    "Checkpoint 2 merge for the EU Tender Autonomous AI Agent presentation",
    'actsEU final presentation: "The Search"',
)


def remove_unmarked_script(html: str, marker: str) -> tuple[str, bool]:
    """Remove a pasted script element that contains `marker`."""
    i = html.find(marker)
    if i < 0:
        return html, False
    start = html.rfind("<script", 0, i)
    end = html.find("</script>", i)
    if start < 0 or end < 0:
        sys.exit(f"Found an earlier install ({marker!r}) but could not find its script tags; remove it by hand.")
    return html[:start] + html[end + len("</script>"):], True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="deck folder (containing index.html) or the HTML file itself")
    ap.add_argument("--version", choices=["A", "B"], default="B")
    ap.add_argument("--intro", choices=["on", "off"], default="on", help="version B: open with the film")
    ap.add_argument("--c1", choices=["voice", "original"], default="voice",
                    help="version B: all 19 slides with your short recordings, or 6 slides with the original narration")
    ap.add_argument("--c2", choices=["live", "recorded"], default="live", help="version B: present Checkpoint 2 live or play recordings")
    ap.add_argument("--demo", choices=["auto", "manual", ""], default="", help="console walkthrough; default auto when recorded, manual when live")
    ap.add_argument("--film", choices=["hybrid", "silent", "anime"], default="hybrid")
    ap.add_argument("--voices", choices=["browser", "files", "live"], default="browser")
    ap.add_argument("--music", choices=["synth", "file", "off"], default="synth")
    ap.add_argument("--team", choices=["on", "off"], default="on")
    ap.add_argument("--ramp", choices=["on", "off"], default="on")
    ap.add_argument("--replace-media", action="store_true", help="overwrite images already in media-final/")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    html_path = target / "index.html" if target.is_dir() else target
    if not html_path.is_file():
        sys.exit(f"Not found: {html_path}")

    js = (HERE / "final_presentation.js").read_text(encoding="utf-8")
    if "</script" in js.lower():
        sys.exit("final_presentation.js contains a closing script tag; it cannot be inlined.")

    html = html_path.read_text(encoding="utf-8")
    if "</body>" not in html:
        sys.exit("The HTML has no closing body tag.")
    if "presentationSlides" not in html:
        print("Warning: this HTML does not look like the Checkpoint 1 deck (no presentationSlides).")

    backup = html_path.with_name(html_path.name + ".before-actsEU.bak")
    if not backup.exists():
        shutil.copy2(html_path, backup)
        print(f"Backup written: {backup.name}")

    removed = 0
    html, n = re.subn(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", html, flags=re.S)
    removed += n
    for marker in OLD_MARKERS:
        while True:
            html, found = remove_unmarked_script(html, marker)
            if not found:
                break
            removed += 1
    if removed:
        print(f"Removed {removed} earlier install(s).")
    if "renderCp2" in html or "cp2-band" in html:
        print("Warning: leftover code from an earlier paste is still in the HTML. Restore the .before-actsEU.bak backup and run this again.")

    config = {
        "version": args.version, "filmStyle": args.film, "voiceMode": args.voices, "music": args.music,
        "teamScene": args.team == "on", "animeRamp": args.ramp == "on",
        "intro": args.intro == "on", "c1Mode": args.c1, "c2Mode": args.c2, "demo": args.demo,
    }
    block = (f"{START}\n<script>window.ACTSEU_CONFIG = {json.dumps(config)};</script>\n"
             f"<script>\n{js}\n</script>\n{END}\n")
    i = html.rfind("</body>")
    html = html[:i] + block + html[i:]
    html_path.write_text(html, encoding="utf-8")
    assert html.count(START) == 1 and html.count(END) == 1
    print(f"Installed into {html_path} with {config}")

    src, dst = HERE / "media-final", html_path.parent / "media-final"
    if src.is_dir():
        dst.mkdir(exist_ok=True)
        copied = kept = 0
        (dst / "voice").mkdir(exist_ok=True)
        for f in sorted(src.iterdir()):
            if not f.is_file():
                continue
            out = dst / f.name
            if out.exists() and not args.replace_media:
                kept += 1
                continue
            shutil.copy2(f, out)
            copied += 1
        print(f"media-final/: {copied} file(s) copied, {kept} of your own kept.")
        voice = sorted(p.name for p in (dst / "voice").glob("*.m4a"))
        print(f"media-final/voice/: {len(voice)} recording(s) found" + (f" ({voice[0]} … {voice[-1]})" if voice else
              ". Put c1-01.m4a … c1-19.m4a here; until then those slides show captions on the target time."))

    console = HERE / "console.html"
    if console.is_file():
        shutil.copy2(console, html_path.parent / "console.html")
        print("console.html copied (the portfolio console shown inside the presentation).")

    print("\nNext: open the HTML in Chrome to check, then `firebase deploy --only hosting` from the Firebase folder.")
    print("Try other settings in the address bar without reinstalling, e.g. index.html?c2=recorded&film=anime&intro=off")


if __name__ == "__main__":
    main()
