# Part 03: Meet the team, "Ten of Me. Zero Guesswork."

One self-contained HTML file, `Team_scene.html` (about 1.3 MB): fonts, Walid's face, and all voices are inside. Click Start and it plays by itself in about 1:31.

## Scenes

1. **The squad**: title card and team photo, ten mini-me robots (A01–A05 in front, A06–A10 behind) and "+ one human with the final say". Narrator line.
2. **A01 … A10**: each agent steps in with its prop, the pipeline track at the top lights its position, and a card shows position (after / before), name, role, stage, function, and input → output. The agent introduces itself; antenna, head and sound rings follow the voice level.
3. **The human decides**: the full track ends at the gold HUMAN node; Dr.-Ing. Walid Barakat, bid authority.

Controls: Space or P pause, ← → previous or next, click a face on the track to jump, C captions, V voices, F full screen. At the end the page posts `{source: "team", event: "complete"}` to a parent page; it accepts `{target: "team", command: "start"}` or `?autostart=1`, for the merged presentation.

## Files

| File | Purpose |
|---|---|
| `team.json` | Title, narrator lines, the ten agents (position, role, stage, function, input → output, spoken line, voice) and the human |
| `make_voices.py` | Synthesises the voices offline with Piper (AI-generated, labelled on screen); writes `voices/` |
| `voices/` | The generated MP3s and their durations, so a rebuild does not need Piper |
| `team_template.html` | The scene engine and layout |
| `build_team.py` | Crops the face disc from the cartoon (m13.jpg), takes robot colours and props from `../../art/art.js`, embeds everything |

```bash
python3 make_voices.py <piper voices folder> voices      # only after changing a line or a voice
python3 build_team.py <path to m13.jpg> voices <out folder>
```

To change an agent's voice, set `"voice"` in `team.json` to `libritts:<speaker 0–903>`, `ryan` or `lessac` and run both commands.
