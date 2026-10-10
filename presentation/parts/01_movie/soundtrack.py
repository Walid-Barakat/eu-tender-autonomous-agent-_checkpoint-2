"""Original cinematic score for "From Dial-Up to Decision", synthesised from scratch and timed to timeline.json.

Drones, heartbeat and clock ticks for the dark sections; impacts and braams on the big cuts; risers into
transitions; a pulsing ostinato for the web era; a hopeful pad and piano theme for the agents; the supplied
dial-up recording on top of the flashback. Writes soundtrack.wav and soundtrack.m4a.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

HERE = Path(__file__).resolve().parent
TL = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
SR = 44100
DUR = TL["duration"]
N = int(SR * DUR)
mix = np.zeros((2, N))
rng = np.random.default_rng(20261010)


def place(sig, at, gain=1.0, pan=0.0):
    """Add a mono or stereo signal at time `at` (seconds) with constant-power pan."""
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.vstack([sig * l * np.sqrt(2), sig * r * np.sqrt(2)])
    i = int(at * SR)
    if i >= N:
        return
    n = min(sig.shape[1], N - i)
    mix[:, i:i + n] += gain * sig[:, :n]


def tt(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def env(d, a=0.01, r=0.3, curve="exp"):
    t = tt(d)
    e = np.minimum(1, t / max(a, 1e-4))
    tail = np.clip((d - t) / max(r, 1e-4), 0, 1)
    return e * (tail ** 2 if curve == "exp" else tail)


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def reverb(x, secs=2.4, wet=0.3):
    t = tt(secs)
    out = []
    for ch in range(2):
        ir = rng.standard_normal(len(t)) * np.exp(-t / (secs / 5))
        ir = lp(ir, 6000) * 0.05
        out.append(fftconvolve(x[ch] if x.ndim == 2 else x, ir)[: (x.shape[-1])])
    out = np.vstack(out)
    dry = x if x.ndim == 2 else np.vstack([x, x])
    return dry * (1 - wet) + out * wet * 3


# ---------------------------------------------------------------- dark drone
def drone(start, end, level, roots=(41.2, 55.0, 82.4), noise=0.4):
    d = end - start
    t = tt(d)
    sig = sum(np.sin(2 * np.pi * f * t) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.05 + k * 0.03) * t + k)) for k, f in enumerate(roots))
    sig += noise * lp(rng.standard_normal(len(t)), 260) * 3
    fade = np.minimum(1, np.minimum(t / 2.0, (d - t) / 2.0))
    place(sig / len(roots) * fade, start, level)


sec = TL["audio"]["sections"]
drone(*sec["cold"], 0.5)
drone(sec["flashback"][0], sec["flashback"][1], 0.07, roots=(55.0, 82.4))
drone(sec["web"][0], sec["hinge"][1], 0.45, roots=(41.2, 55.0, 61.7))


# ---------------------------------------------------------------- heartbeat and clock
def thump(level=1.0):
    t = tt(0.22)
    return np.sin(2 * np.pi * (60 - 25 * t / 0.22) * t) * np.exp(-t / 0.06) * level


def heartbeat(start, end, period):
    x = start
    while x < end:
        place(thump(0.9), x, 0.9)
        place(thump(0.6), x + 0.27, 0.9)
        x += period


heartbeat(0.2, 3.0, 1.0)
heartbeat(66.2, 73.4, 0.85)
for k, x in enumerate(np.arange(66.0, 73.5, 0.5)):
    click = hp(rng.standard_normal(int(0.012 * SR)), 3000) * np.exp(-tt(0.012) / 0.003)
    place(click, x, 0.25, pan=0.3 if k % 2 else -0.3)


# ---------------------------------------------------------------- impacts, braams, risers, flash
def impact():
    t = tt(2.2)
    sub = np.sin(2 * np.pi * (35 + 55 * np.exp(-t / 0.25)) * t) * np.exp(-t / 0.7)
    crack = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t / 0.18)
    return reverb(np.vstack([sub + 0.5 * crack, sub + 0.5 * crack]), 2.6, 0.35)


for at in TL["audio"]["impacts"]:
    place(impact(), at, 0.16)


def braam(freqs, d=4.5):
    t = tt(d)
    sig = sum(saw(f * (1 + det), t) for f in freqs for det in (-0.004, 0.0, 0.004))
    sig = np.tanh(1.8 * lp(sig / (3 * len(freqs)), 1100, 4)) * env(d, 0.08, 3.6)
    return reverb(np.vstack([sig, sig]), 3.0, 0.4)


braam_chords = {66.0: (55.0, 82.4, 110.0, 130.8), 94.5: (65.4, 98.0, 130.8, 164.8)}
for at in TL["audio"]["braams"]:
    place(braam(braam_chords.get(at, (55.0, 82.4, 110.0))), at, 0.22)


def riser(d):
    t = tt(d)
    noise = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    blocks = 24
    for b in range(blocks):  # rising band-pass, block by block
        lo = 300 * (8 ** (b / blocks))
        seg = slice(b * len(t) // blocks, (b + 1) * len(t) // blocks)
        out[seg] = bp(noise, lo, min(lo * 2.2, 16000))[seg]
    tone = np.sin(2 * np.pi * (180 + 900 * (t / d) ** 2) * t) * 0.25
    e = (t / d) ** 2.5
    return (out * 2.2 + tone) * e


for a, b in TL["audio"]["risers"]:
    place(riser(b - a), a, 0.25)

# ---------------------------------------------------------------- web era: pulsing ostinato, growing to the hinge
w0, w1 = sec["web"]
step = 60 / 100 / 2
pattern = [57, 57, 60, 57, 64, 57, 62, 57]
x, k = w0, 0
while x < w1 - 0.1:
    prog = (x - w0) / (w1 - w0)
    f = note(pattern[k % 8] - 12)
    t = tt(0.32)
    pl = lp(saw(f, t) + 0.5 * saw(f * 1.005, t), 500 + 1800 * prog) * np.exp(-t / 0.12)
    place(pl, x, 0.25 + 0.35 * prog, pan=-0.2 if k % 2 else 0.2)
    if prog > 0.45 and k % 2 == 0:
        place(thump(0.8), x, 0.25 + 0.3 * prog)
    x += step
    k += 1

# ---------------------------------------------------------------- hope: pad, piano, swell into the title
h0, h1 = sec["hope"]
chords = [(57, 60, 64), (53, 57, 60), (48, 55, 64), (55, 59, 62), (57, 60, 64), (53, 57, 60), (55, 59, 62)]
cd = (TL["audio"]["braams"][-1] - h0) / len(chords)


def pad(midis, d, level):
    t = tt(d)
    sig = sum(lp(saw(note(m) * (1 + det), t), 1400) for m in midis for det in (-0.003, 0.003))
    sig += sum(np.sin(2 * np.pi * note(m - 12) * t) for m in midis[:1]) * 1.5
    return sig / (2 * len(midis)) * env(d, 0.9, 0.9, "lin") * level


for i, ch in enumerate(chords):
    place(reverb(pad(ch, cd + 0.4, 1.0), 2.5, 0.3), h0 + i * cd, 0.6 + 0.3 * i / len(chords))


def piano(m, d=1.6):
    t = tt(d)
    f = note(m)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return s * np.exp(-t / 0.45) * np.minimum(1, t / 0.004)


arp_t = TL["scenes"][[s["id"] for s in TL["scenes"]].index("s13")]["start"]
x = arp_t
while x < TL["audio"]["braams"][-1] - 0.2:
    ci = min(int((x - h0) / cd), len(chords) - 1)
    ch = chords[ci]
    j = int(round((x - arp_t) / 0.375))
    lift = 12 if x > TL["audio"]["braams"][-1] - 6 else 0
    m = (ch[j % 3] + 12 + lift) if j % 4 != 3 else ch[0] + 24
    place(reverb(piano(m), 1.8, 0.25), x, 0.35, pan=0.25 if j % 2 else -0.15)
    x += 0.375

# title and credits: C major then a soft A minor fade
place(reverb(pad((48, 55, 64, 67), 6.4, 1.0), 2.5, 0.35), 94.5, 0.8)
place(reverb(pad((45, 52, 60, 64), 7.0, 1.0), 2.5, 0.35), 100.5, 0.6)

# ---------------------------------------------------------------- the dial-up recording
dial = TL["audio"]["dialup"]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HERE / "src" / dial["file"]), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
d = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).T.astype(float)
place(d, dial["at"], 10 ** (dial["gain_db"] / 20))

# ---------------------------------------------------------------- master
mix[:, : int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))
mix[:, -int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR)) ** 1.5
peak = np.max(np.abs(mix))
# Level automation: each part of the story gets its own loudness target (dBFS RMS), with 0.5 s ramps.
targets = [(0, 3, -27), (3, 10.5, -25), (10.5, 24.3, -23), (24.3, 36.8, -20), (36.8, 52, -25), (52, 66, -22),
           (66, 73.5, -21), (73.5, 94.5, -19), (94.5, 100.5, -16), (100.5, DUR, -20)]
gain = np.ones(N)
for a, b, db in targets:
    seg = mix[:, int(a * SR):int(b * SR)]
    gain[int(a * SR):int(b * SR)] = 10 ** (db / 20) / (np.sqrt(np.mean(seg ** 2)) + 1e-9)
k = int(0.5 * SR)
gain = np.convolve(np.pad(gain, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
mix = mix * gain
mix = np.tanh(mix * 1.15) * 0.95
pcm = (mix.T * 32767).astype(np.int16)
import wave
with wave.open(str(HERE / "soundtrack.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "soundtrack.wav"), "-c:a", "aac", "-b:a", "192k", str(HERE / "soundtrack.m4a")], check=True)
print(f"soundtrack: {DUR:.1f} s, peak before limiter {peak:.2f}")
