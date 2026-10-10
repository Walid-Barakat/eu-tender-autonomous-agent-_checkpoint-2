# Part 01 · The film: "From Dial-Up to Decision"

107 seconds, 1920×1080, 25 fps, with an original synthesised score and the dial-up recording.

| File | Role |
|---|---|
| `timeline.json` | Every scene: image, framing, colour grade, camera move, caption, and the sound cues |
| `movie.html` | The renderer. Opens as a player (`movie.html`), or renders single frames for capture (`?capture=1`) |
| `soundtrack.py` | Synthesises the score from the timeline and mixes in `src/dialup.mp3` → `soundtrack.m4a` |
| `capture.js` | Renders all frames with Playwright and encodes `movie.mp4` with the soundtrack |
| `src/` | The fifteen images `m01.jpg` … `m15.jpg` and `dialup.mp3` (not in Git: third-party screenshots and logos) |

Rebuild after changing the timeline:

```bash
python3 -m http.server 8770 &           # movie.html loads timeline.json over HTTP
python3 soundtrack.py                   # soundtrack.wav and soundtrack.m4a
node capture.js movie.mp4               # needs Playwright with Chromium
```
