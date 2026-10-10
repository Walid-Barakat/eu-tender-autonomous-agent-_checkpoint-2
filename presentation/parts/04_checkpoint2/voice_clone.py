"""Checkpoint 2 narration in Walid's own voice, converted from his Checkpoint 1 recordings (kNN-VC).

Requested by Walid for his own talk. The deck labels it "AI voice clone of the presenter" on every slide.

How: kNN-VC (Baas, van Niekerk, Kamper, Interspeech 2023, github.com/bshall/knn-vc) takes the sentence-timed
rehearsal narration (make_narration.py) and replaces every 20 ms frame with the average of its nearest
neighbours among ~19 minutes of Walid's Checkpoint 1 speech, then vocodes the result. The words and timing stay
those of the script, so the subtitles still fit; the voice, timbre and room are Walid's.

Usage: python3 voice_clone.py <knn-vc repo folder> <folder of reference wavs, 16 kHz mono> [out folder, default: voice_walid]
Weights: WavLM-Large.pt and prematch_g_02500000.pt from github.com/bshall/knn-vc/releases (torch hub cache).
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

HERE = Path(__file__).resolve().parent
KNN, REF = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else HERE / "voice_walid"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(KNN))
from hubconf import knn_vc  # noqa: E402

torch.set_num_threads(max(1, torch.get_num_threads()))
SR = 16000
CHUNK = 20 * SR
vc = knn_vc(pretrained=True, prematched=True, device="cpu")


def load16(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return torch.from_numpy(np.frombuffer(raw, dtype=np.float32).copy())


# ---------------------------------------------------------------- matching set: Walid's Checkpoint 1 speech
cache = OUT / "matching_set.pt"
if cache.exists():
    matching = torch.load(cache)
else:
    feats, t0 = [], time.time()
    for wav in sorted(REF.glob("*.wav")):
        x = load16(wav)
        for i in range(0, len(x), CHUNK):
            seg = x[i:i + CHUNK]
            if len(seg) < SR:
                continue
            feats.append(vc.get_features(seg[None], vad_trigger_level=0))
        print(f"  {wav.name}: {len(x) / SR:5.1f} s  ({time.time() - t0:5.0f} s elapsed)", flush=True)
    matching = torch.cat(feats, dim=0)
    torch.save(matching, cache)
print(f"matching set: {matching.shape[0]} frames = {matching.shape[0] * 0.02 / 60:.1f} min of Walid's speech")

# ---------------------------------------------------------------- convert each scene, keep its timing
narr = json.loads((HERE / "voice" / "narration.json").read_text(encoding="utf-8"))
for key in narr:
    src = load16(HERE / "voice" / f"{key}.mp3")
    query = vc.get_features(src[None], vad_trigger_level=0)
    out = vc.match(query, matching, topk=4, tgt_loudness_db=None).cpu().numpy()
    wav = OUT / f"{key}.wav"
    sf.write(wav, out, SR)
    mp3 = OUT / f"{key}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", "highpass=f=60,loudnorm=I=-16.5:TP=-1.5:LRA=9,apad=whole_dur=" + f"{len(src) / SR:.3f}",
                    "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "80k", str(mp3)], check=True)
    wav.unlink()
    print(f"{key}: {len(src) / SR:5.1f} s converted", flush=True)
print("done:", OUT)
