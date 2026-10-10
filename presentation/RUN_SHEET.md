# Run sheet: Saturday 10 October 2026, 15:55

File: `EU_Tender_Final_Presentation.html` (GitHub Release asset). Chrome, one screen, sound on.

## Choose the mode

| Mode | Button | Length | You |
|---|---|---:|---|
| Full autoplay | Start the whole presentation | 14:31 | Watch; step in only for questions |
| Live Checkpoint 2 (if you want to speak) | Live Checkpoint 2 | 15:33 planned | Parts 1–3 play; from Checkpoint 2 you speak, → advances, N shows your script |
| Natural speed | Start at natural speech speed | 16:46 | Rehearsal only: too long for the slot |

Live and over time? Skip *Twelve risks* (−20 s) and keep the console demo short (Run demo, then Next after the approval).

## Timeline (full autoplay)

| Clock | Part |
|---:|---|
| 0:00 | Act I *The Search* (film, 1:40). Space pauses, → skips |
| 1:40 | Checkpoint 1: title · four steps · architecture · full autonomous run · problem solving · achievements |
| 7:36 | Meet the team: *Ten of Me. Zero Guesswork.* (ten agents, then the human) |
| 9:09 | Checkpoint 2: market · what the data showed · distributions · portfolio · console · evaluation · ROI · risks · AI Act · GDPR · go to market · built to grow · recommendation |
| 14:31 | "Presentation complete": invite questions |

## Pre-flight (by 15:30)

- [ ] Full run once on this Mac, in Chrome, with sound (the automated tests could not play MP4 or AAC).
- [ ] Mac volume about 60%; notifications off; browser zoom 100%; F for full screen after Start.
- [ ] Fallbacks on the desktop: `Checkpoint2.html`, `Team_scene.html`, `Act_I_The_Search_cinematic.mp4`, and the Firebase Checkpoint 1 deck (eu-tender-presentation.firebaseapp.com).
- [ ] Repository open in a tab: github.com/Walid-Barakat/eu-tender-autonomous-agent-2
- [ ] `PYTHONPATH=src pytest -q` shows 22 passed (if asked to show the code running).
- [ ] Credentials from the earlier shared archive rotated.

## If something fails

| Problem | Do |
|---|---|
| No sound on a slide | Click the narration button at the bottom right, or press P twice |
| The film stalls | → skips to Checkpoint 1 |
| The team scene stalls | → moves to the next agent; → on the last one starts Checkpoint 2 |
| The console does not respond | Next ▶; the portfolio slide before it has the numbers |
| The whole file misbehaves | Open the part files on the desktop in order |

## Likely questions

| Question | Answer |
|---|---|
| "Is that your voice in Checkpoint 2?" | It is an AI clone of my voice, made from my Checkpoint 1 recordings, and every slide says so. Live mode uses no synthetic voice. |
| "Are the agents really talking?" | The lines are scripted from what each stage does and spoken by labelled synthetic voices. The agents themselves run in the pipeline shown in Checkpoint 1. |
| "Is the Monte Carlo just made-up numbers?" | The structure is standard; the centre values are the Checkpoint 1 rules and are uncalibrated. That is why every run shows two profiles and why the pilot records outcomes. |
| "Why exact optimisation?" | Seven candidates means 127 portfolios, milliseconds to check. Above 20 candidates the code falls back to a greedy search and says so. |
| "Is this high-risk under the AI Act?" | No: it scores organisations, not people, and is not a safety component of energy infrastructure. Ranking people, for example in a recruiting agent, would change that, so it needs re-classification first. |
| "How does it grow?" | Every agent has one job and a typed contract. New agents (legal, feasibility, PMO, recruiting, finance, strategy and R&D, public affairs) plug into the same pipeline and the same evaluation; the human keeps the decision. |
| "What is the business model?" | A managed service: about €10.8k setup and €1,200 a month per client, target contribution about €9k per client per year. The pilot tests those targets. |
| "What would make you stop the pilot?" | Fewer than 15 hours a month saved in months 2–3 (15–22 hours extends the pilot by a month), or any recommendation on a non-biddable tender after one fix cycle. |
