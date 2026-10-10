"""Synthesise the agents' voices offline with Piper (AI-generated, labelled as such in the scene).

Usage: python3 make_voices.py <piper voices folder> <out folder>
The voices folder holds the unpacked Piper voices: voice-en-us-libritts-high/, voice-en-us-ryan-high/,
voice-en-us-lessac-medium/ (from github.com/rhasspy/piper/releases/tag/v0.0.2). Writes vo-intro.mp3,
vo-a01.mp3 … vo-a10.mp3, vo-finale.mp3 and voices.json (durations) into <out folder>.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VOICES, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
team = json.loads((HERE / "team.json").read_text(encoding="utf-8"))
MODELS = {"libritts": "voice-en-us-libritts-high/en-us-libritts-high.onnx",
          "ryan": "voice-en-us-ryan-high/en-us-ryan-high.onnx",
          "lessac": "voice-en-us-lessac-medium/en-us-lessac-medium.onnx"}

jobs = [("intro", team["narrator"]["voice"], team["narrator"]["intro"])]
jobs += [(a["id"].lower(), a["voice"], a["line"]) for a in team["agents"]]
jobs += [("finale", team["narrator"]["voice"], team["narrator"]["finale"])]

durations = {}
for key, voice, text in jobs:
    model, _, speaker = voice.partition(":")
    wav, mp3 = OUT / f"vo-{key}.wav", OUT / f"vo-{key}.mp3"
    cmd = ["piper", "-m", str(VOICES / MODELS[model]), "-f", str(wav), "--length-scale", "0.94", "--sentence-silence", "0.25"]
    if speaker:
        cmd += ["-s", speaker]
    subprocess.run(cmd, input=text.encode(), check=True, capture_output=True)
    # trim the silence at both ends, even out loudness, light warmth, mono MP3 (plays in every browser)
    af = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "highpass=f=70,loudnorm=I=-17:TP=-1.5:LRA=7,apad=pad_dur=0.15")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", af, "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "80k", str(mp3)], check=True)
    wav.unlink()
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                             capture_output=True, text=True, check=True).stdout)
    durations[key] = round(d, 2)
    print(f"{key:7s} {voice:14s} {d:5.2f} s")
(OUT / "voices.json").write_text(json.dumps(durations, indent=1), encoding="utf-8")
print(f"total speech {sum(durations.values()):.1f} s")
