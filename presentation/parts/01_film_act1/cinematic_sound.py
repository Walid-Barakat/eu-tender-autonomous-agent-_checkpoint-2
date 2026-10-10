"""Act I "The Search": a cinematic voice-over and sound design, mixed onto Walid's film.

Three voices tell the story, all AI-generated offline with Piper and labelled as such:
  grandson  - curious, young (a light voice, pitched up)
  grandpa   - warm and experienced, a little reverb for the memory (the flashback, 0:06-0:44)
  narrator  - the deep movie-trailer storyteller (0:44-1:40)
Under them: the film's own score and the dial-up recording, ducked whenever someone speaks, plus
sound design in the Hollywood manner: park ambience, a tape-rewind into the flashback, a clock while
the modem dials, a hit on CONNECTED, whooshes on the cuts, a riser and impact when the agent arrives,
and a braam with sub boom under the title.

Usage: python3 cinematic_sound.py <Act_I_The_Search package folder> <piper voices folder> <out folder>
Writes act1_voice.wav (voice only), act1_mix.wav and Act_I_The_Search_cinematic.mp4 (picture unchanged).
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pyloudnorm
import soundfile as sf
from pedalboard import Compressor, HighpassFilter, HighShelfFilter, LowShelfFilter, PeakFilter, Pedalboard, Reverb, Limiter
from scipy.signal import butter, fftconvolve, sosfilt

PKG, VOICES, OUT = (Path(a).resolve() for a in sys.argv[1:4])
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "tmp"
TMP.mkdir(exist_ok=True)
SR, DUR = 48000, 100.0
N = int(SR * DUR)
rng = np.random.default_rng(1010)
meter = pyloudnorm.Meter(SR)

# ---------------------------------------------------------------- the script, cue by cue
# (start s, latest end s, role, text as spoken[, slower length scale for a single line]). The burnt-in captions in the film stay as they are.
CUES = [
    (1.6, 5.6, "grandson", "Grandpa... how did you find anything, before A.I.?"),
    (6.3, 7.6, "grandpa", "First,", 1.55),
    (8.1, 11.2, "grandpa", "we learned how to wait.", 1.5),
    (12.8, 17.9, "grandpa", "It felt like the Stone Age. A question, a computer, and a very long wait."),
    (18.4, 21.9, "grandpa", "Then came the sound we all remember."),
    (22.4, 25.9, "grandpa", "Every journey began with a connection."),
    (30.3, 33.9, "grandpa", "And sometimes, the question waited longer than we did."),
    (38.7, 43.9, "grandpa", "At last, we were connected. A new world opened."),
    (44.5, 51.0, "narrator", "The years passed. Connections grew faster. Information multiplied. But understanding it, still took work."),
    (51.4, 56.9, "narrator", "We learned to Google it. Then we learned how much there was to read."),
    (57.2, 59.9, "narrator", "Finding information was only the beginning."),
    (60.7, 64.9, "narrator", "Now, an agent can turn a question into a research plan."),
    (65.4, 71.9, "narrator", "Find the documents. Examine their evidence. Cross-check what matters. Make the gaps visible."),
    (72.4, 79.9, "narrator", "For energy tenders, that means organising requirements and findings, into a result someone can inspect."),
    (80.4, 87.7, "narrator", "The purpose is a better decision, with evidence behind it, and a person accountable for what happens next."),
    (88.9, 99.3, "narrator", "This is the E.U. Tender Autonomous A.I. Agent. Energy funding and tender intelligence. Presented by Doctor Engineer Waleed Barakat. i at work."),
]
MODELS = {"libritts": "voice-en-us-libritts-high/en-us-libritts-high.onnx", "ryan": "voice-en-us-ryan-high/en-us-ryan-high.onnx"}
ROLES = {
    # model, speaker, length scale, sentence pause, rubberband pitch ratio, extra ffmpeg filter
    "grandson": ("libritts", "13", 1.0, 0.25, 1.08, ""),
    "grandpa": ("libritts", "117", 1.2, 0.45, 0.95, ",vibrato=f=4.5:d=0.035"),
    "narrator": ("ryan", "", 1.08, 0.45, 0.89, ""),
}
FX = {
    "grandson": Pedalboard([HighpassFilter(140), PeakFilter(3200, 2.5, 1.0), Compressor(-22, 3, 5, 120), Reverb(0.25, 0.6, 0.10, 0.9, 1.0)]),
    "grandpa": Pedalboard([HighpassFilter(70), LowShelfFilter(180, 2.5), PeakFilter(2800, 2.0, 1.0), HighShelfFilter(9000, -2.0),
                           Compressor(-22, 3.5, 6, 140), Reverb(0.55, 0.5, 0.16, 0.86, 1.0)]),
    "narrator": Pedalboard([HighpassFilter(55), LowShelfFilter(120, 4.5), PeakFilter(320, -2.0, 1.0), PeakFilter(3500, 2.5, 0.9),
                            Compressor(-24, 4, 4, 160), Reverb(0.4, 0.45, 0.11, 0.9, 1.0)]),
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def load(path, sr=SR):
    raw = run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"]).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).T.astype(np.float64)


def loud(x, target):
    probe = np.tile(x, (1, int(np.ceil(0.8 * SR / x.shape[1])))) if x.shape[1] < 0.8 * SR else x  # the meter needs 0.4 s or more
    l = meter.integrated_loudness(probe.T)
    return x * 10 ** ((target - l) / 20) if np.isfinite(l) else x


def tt(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)


def place(track, sig, at, gain=1.0, pan=0.0):
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.vstack([sig * l * np.sqrt(2), sig * r * np.sqrt(2)])
    i = int(at * SR)
    n = min(sig.shape[1], N - i)
    if n > 0:
        track[:, i:i + n] += gain * sig[:, :n]


def verb(x, secs=2.5, wet=0.35):
    t = tt(secs)
    out = []
    for ch in range(2):
        ir = lp(rng.standard_normal(len(t)) * np.exp(-t / (secs / 5)), 7000) * 0.05
        out.append(fftconvolve(x[ch] if x.ndim == 2 else x, ir)[: x.shape[-1]])
    dry = x if x.ndim == 2 else np.vstack([x, x])
    return dry * (1 - wet) + np.vstack(out) * wet * 3


# ---------------------------------------------------------------- 1. voices
voice = np.zeros((2, N))
print("voice-over:")
for k, (start, end, role, text, *slow) in enumerate(CUES):
    model, spk, ls, pause, pitch, extra = ROLES[role]
    ls = slow[0] if slow else ls
    wav = TMP / f"cue{k:02d}.wav"
    cmd = ["piper", "-m", str(VOICES / MODELS[model]), "-f", str(wav), "--length-scale", str(ls), "--sentence-silence", str(pause)]
    if spk:
        cmd += ["-s", spk]
    run(cmd, input=text.encode())
    shaped = TMP / f"cue{k:02d}_p.wav"
    af = (f"silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          f"aresample={SR},rubberband=pitch={pitch}:formant=shifted{extra}")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", af, "-ac", "1", str(shaped)])
    x, _ = sf.read(shaped)
    room = end - start
    if len(x) / SR > room:  # tell it a little faster rather than overrun the cut
        tempo = min(1.3, len(x) / SR / room)
        fitted = TMP / f"cue{k:02d}_f.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(shaped), "-af", f"rubberband=tempo={tempo:.4f}", str(fitted)])
        x, _ = sf.read(fitted)
    x = FX[role](x.astype(np.float32)[None, :], SR)[0].astype(np.float64)
    st = np.vstack([x, x])
    st = loud(st, -17.0 if role != "grandson" else -18.0)
    place(voice, st, start)
    print(f"  {start:5.1f}-{start + len(x) / SR:5.1f} (room {room:4.1f})  {role:8s} {text[:60]}")

# ---------------------------------------------------------------- 2. music and modem, ducked under the voice
score = load(PKG / "assets" / "cinematic-soundtrack.mp3")[:, :N]
score = np.pad(score, ((0, 0), (0, N - score.shape[1])))
score = loud(score, -21.0)
modem = loud(load(PKG / "assets" / "dial-up-modem-01.mp3"), -22.0)
bed_modem = np.zeros((2, N))
place(bed_modem, modem, 12.0)
# a mild telephone band on the modem so it sits in the memory, not in the room
bed_modem = np.vstack([bp(bed_modem[c], 250, 5200) * 1.25 for c in range(2)])

env = np.sqrt(np.convolve((voice ** 2).mean(axis=0), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same"))
talking = (env > 10 ** (-48 / 20)).astype(float)
k = int(0.35 * SR)  # hold, so the music does not pump between words
talking = np.convolve(talking, np.ones(k), mode="same") > 0
duck = np.where(talking, 10 ** (-9 / 20), 1.0)
a = int(0.25 * SR)
duck = np.convolve(np.pad(duck, (a, a), mode="edge"), np.ones(a) / a, mode="same")[a:-a]

# ---------------------------------------------------------------- 3. sound design
sfx = np.zeros((2, N))


def impact(d=2.6):
    t = tt(d)
    sub = np.sin(2 * np.pi * (32 + 60 * np.exp(-t / 0.22)) * t) * np.exp(-t / 0.75)
    crack = lp(rng.standard_normal(len(t)), 2000) * np.exp(-t / 0.15)
    return verb(np.vstack([sub + 0.45 * crack] * 2), 3.0, 0.35)


def braam(freqs, d=5.5):
    t = tt(d)
    sig = sum(2 * ((f * (1 + det) * t) % 1) - 1 for f in freqs for det in (-0.004, 0, 0.004))
    sig = np.tanh(2.0 * lp(sig / (3 * len(freqs)), 900, 4)) * np.minimum(1, t / 0.06) * np.clip((d - t) / 4.5, 0, 1) ** 2
    return verb(np.vstack([sig, sig]), 3.5, 0.45)


def riser(d):
    t = tt(d)
    noise = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    for b in range(24):
        lo = 300 * (8 ** (b / 24))
        seg = slice(b * len(t) // 24, (b + 1) * len(t) // 24)
        out[seg] = bp(noise, lo, min(lo * 2.2, 16000))[seg]
    return (out * 2.2 + np.sin(2 * np.pi * (160 + 900 * (t / d) ** 2) * t) * 0.25) * (t / d) ** 2.5


def whoosh(d=1.2, rev=False):
    t = tt(d)
    e = np.sin(np.pi * t / d) ** 2
    sig = np.zeros(len(t))
    noise = rng.standard_normal(len(t))
    for b in range(16):
        f = 400 + 3000 * np.sin(np.pi * (b + 0.5) / 16)
        seg = slice(b * len(t) // 16, (b + 1) * len(t) // 16)
        sig[seg] = bp(noise, f * 0.6, f * 1.6)[seg]
    sig = sig * e
    return sig[::-1] if rev else sig


def birds(d):
    out = np.zeros(int(d * SR))
    x = 0.4
    while x < d - 0.5:
        f0 = rng.uniform(2800, 4800)
        for j in range(rng.integers(2, 5)):
            n = int(rng.uniform(0.05, 0.11) * SR)
            t = np.arange(n) / SR
            ch = np.sin(2 * np.pi * (f0 + 1600 * np.sin(2 * np.pi * 18 * t)) * t) * np.sin(np.pi * t / t[-1]) ** 2
            i = int((x + j * 0.13) * SR)
            out[i:i + n] += ch[: len(out) - i]
        x += rng.uniform(0.7, 1.6)
    return out


# 0-12 s: a walk in the park, then the memory pulls us back
t = tt(12.4)
wind = lp(rng.standard_normal(len(t)), 500) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t)) * np.clip((12.4 - t) / 1.5, 0, 1)
place(sfx, np.vstack([wind, lp(rng.standard_normal(len(t)), 500) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t + 1))]), 0.0, 0.05)
place(sfx, birds(11.0), 0.2, 0.05, pan=-0.35)
place(sfx, birds(10.0), 0.9, 0.035, pan=0.45)
# tape rewind into the flashback
t = tt(1.1)
rewind = np.sin(2 * np.pi * np.cumsum(1400 - 1200 * (t / 1.1)) / SR) * 0.4 + bp(rng.standard_normal(len(t)), 1200, 6000) * 0.8
place(sfx, rewind * (t / 1.1) ** 1.5, 10.9, 0.12)
place(sfx, whoosh(1.3, rev=True), 10.75, 0.16)
place(sfx, impact(), 12.0, 0.16)
# the waiting: a clock under the dial-up, from "Still connecting" to the connection
for i, x in enumerate(np.arange(26.0, 38.0, 0.5)):
    click = hp(rng.standard_normal(int(0.014 * SR)), 2500) * np.exp(-tt(0.014) / 0.0035)
    place(sfx, click, x, 0.10 + 0.05 * (x - 26) / 12, pan=0.25 if i % 2 else -0.25)
place(sfx, riser(2.2), 35.8, 0.12)
# CONNECTED
place(sfx, impact(), 38.0, 0.19)
t = tt(3.0)
shimmer = sum(np.sin(2 * np.pi * f * t) for f in (1318.5, 1760.0, 2637.0)) * np.exp(-t / 0.9) * 0.15
place(sfx, verb(np.vstack([shimmer, shimmer]), 2.5, 0.5), 38.05, 0.35)
# the years pass: whooshes on the cuts of the web era
for at in (43.6, 50.6, 56.6):
    place(sfx, whoosh(1.0), at, 0.14, pan=rng.uniform(-0.4, 0.4))
# the agent arrives
place(sfx, riser(2.6), 57.6, 0.2)
place(sfx, impact(), 60.2, 0.2)
place(sfx, braam((55.0, 82.4, 110.0, 130.8)), 60.2, 0.16)
for at in (64.7, 71.7, 79.7):
    place(sfx, whoosh(0.9), at, 0.12, pan=rng.uniform(-0.4, 0.4))
# the title
place(sfx, riser(2.3), 85.8, 0.22)
place(sfx, whoosh(1.4, rev=True), 86.7, 0.18)
place(sfx, impact(3.2), 88.1, 0.26)
place(sfx, braam((65.4, 98.0, 130.8, 164.8), 7.5), 88.1, 0.24)

# ---------------------------------------------------------------- 4. mix and master
mix = (score + bed_modem) * duck + sfx + voice
fade = int(0.9 * SR)
mix[:, -fade:] *= np.linspace(1, 0, fade) ** 1.5
mix = loud(mix, -14.0)
mix = Pedalboard([Limiter(-2.5, 120)])(mix.astype(np.float32), SR).astype(np.float64) * 10 ** (-3.7 / 20)  # the limiter adds make-up gain; land at about -15 LUFS, peaks under -1 dBFS
sf.write(OUT / "act1_voice.wav", voice.T.astype(np.float32), SR)
sf.write(OUT / "act1_mix.wav", mix.T.astype(np.float32), SR)
print(f"mix: {meter.integrated_loudness(mix.T):.1f} LUFS, peak {20 * np.log10(np.abs(mix).max()):.1f} dBFS")

film = PKG / "Act_I_The_Search.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", str(film), "-i", str(OUT / "act1_mix.wav"), "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT / "Act_I_The_Search_cinematic.mp4")])
print("film:", OUT / "Act_I_The_Search_cinematic.mp4")
