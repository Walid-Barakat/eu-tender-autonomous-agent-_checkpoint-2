"""AI rehearsal narration for Checkpoint 2 (Piper, offline). Labelled as AI-generated in the deck.

Usage: python3 make_narration.py <piper voices folder> [out folder, default: voice]
Reads the scripts from ../../version_b_scripts.json (c2-00 … c2-11). Each sentence is spoken separately and
joined with short pauses, so the subtitles are timed exactly. The console script is laid on the walkthrough:
each sentence starts with the step it describes. Writes c2-XX.mp3 and narration.json (duration and cues).
Walid's own recordings can replace these at runtime (Load my recordings on the start card).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
VOICES = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else HERE / "voice"
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "tmp"
TMP.mkdir(exist_ok=True)
SR = 44100
scripts = json.loads((HERE.parent.parent / "version_b_scripts.json").read_text(encoding="utf-8"))["c2"]
SPOKEN = {"250,000": "two hundred and fifty thousand", "€2 trillion": "two trillion euros", "AI Act": "A.I. Act", "DPIA": "D.P.I.A.", "GDPR": "G.D.P.R.", "ROI": "R.O.I.", "n8n": "n-eight-n", "LangSmith": "Lang Smith", "PMO": "P.M.O.", "R&D": "R and D"}
PAUSE = 0.55
# The console walkthrough (see build_checkpoint2.py, DEMO): seconds at which each sentence should start.
CONSOLE_AT = [0.4, 4.0, 10.8, 17.8, 27.0, 39.8, 50.8, 58.2]


def sentences(text):
    safe = re.sub(r"\b(Dr|Mr|Ms|Prof|Ing|e\.g|i\.e|vs|No)\.", lambda m: m.group(1) + "․", text)
    safe = re.sub(r"(\d)\.(\d)", "\\1\u2024\\2", safe)  # decimals such as 0.2 stay in one sentence
    parts = re.findall(r"[^.!?]+[.!?]+(?:\s|$)", safe) or [safe]
    return [p.strip().replace("․", ".") for p in parts if p.strip()]


def speak(text, path):
    for a, b in SPOKEN.items():
        text = text.replace(a, b)
    raw = path.with_suffix(".raw.wav")
    subprocess.run(["piper", "-m", str(VOICES / "voice-en-us-ryan-high/en-us-ryan-high.onnx"), "-f", str(raw), "--length-scale", "1.08"],
                   input=text.encode(), check=True, capture_output=True)
    af = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          f"aresample={SR},highpass=f=70")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", af, "-ac", "1", str(path)], check=True)
    x, _ = sf.read(path)
    return x


meta = {}
for e in scripts:
    parts = sentences(e["text"])
    clips = [speak(p, TMP / f"{e['id']}_{k}.wav") for k, p in enumerate(parts)]
    starts, t = [], 0.3
    for k, c in enumerate(clips):
        if e["scene"] == "console" and k < len(CONSOLE_AT):
            t = max(t, CONSOLE_AT[k])
        starts.append(t)
        t += len(c) / SR + PAUSE
    total = starts[-1] + len(clips[-1]) / SR + 0.3
    track = np.zeros(int(total * SR) + 1)
    for s, c in zip(starts, clips):
        i = int(s * SR)
        track[i:i + len(c)] += c
    wav = TMP / f"{e['id']}.wav"
    sf.write(wav, track, SR)
    mp3 = OUT / f"{e['id']}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=150,loudnorm=I=-16.5:TP=-1.5:LRA=9",
                    "-ar", str(SR), "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k", str(mp3)], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                             capture_output=True, text=True, check=True).stdout)
    meta[e["id"]] = {"scene": e["scene"], "duration": round(d, 2), "target": e["seconds"],
                     "cues": [{"start": round(s, 2), "end": round(s + len(c) / SR + 0.15, 2), "text": p} for s, c, p in zip(starts, clips, parts)]}
    print(f"{e['id']} {e['scene']:12s} target {e['seconds']:3d} s  spoken {d:5.1f} s  {len(parts)} sentences")
for f in TMP.iterdir():
    f.unlink()
TMP.rmdir()
for f in OUT.glob("durations.json"):
    f.unlink()
(OUT / "narration.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"total {sum(m['duration'] for m in meta.values()):.0f} s (target {sum(e['seconds'] for e in scripts)} s)")
