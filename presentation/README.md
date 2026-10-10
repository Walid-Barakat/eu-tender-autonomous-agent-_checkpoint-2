# Final presentation: EU Tender Autonomous AI Agent

**EU Energy Funding and Tender: Autonomous Energy-Tender Intelligence System**
Dr.-Ing. Walid Barakat · i@work · Principal Consultant for AI-Energy Systems and Sustainable AI Infrastructure
Capstone final presentation, 10 October 2026

One self-contained HTML file plays the whole talk: open it in Chrome, click Start. No server, no internet, no other files.

| # | Part | What the audience sees | Length |
|---:|---|---|---:|
| 1 | Act I · *The Search* | Film: a grandson asks how anyone found anything before AI; dial-up, the search era, the arrival of the research agent. Cinematic voice-over and sound design | 1:40 |
| 2 | Checkpoint 1, as recorded | 6 of the 19 Checkpoint 1 slides, each with its complete original recording, subtitles and evidence (title, problem, architecture, full autonomous run, problem solving, achievements) | 5:56 at the 15-minute pace |
| 3 | Meet the team: *Ten of Me. Zero Guesswork.* | Ten mini-me agents with Walid's face introduce their position, role, function and input → output; the human bid authority closes | 1:33 |
| 4 | Checkpoint 2 | 13 scenes: the €2 trillion market, what the data showed, 4,000-scenario distributions, portfolio optimisation, the portfolio console live, evaluation, ROI, risks, EU AI Act, GDPR, go to market, *Built to grow* (seven planned agent roles), recommendation | 5:22 narrated · 6:25 live |

**Start card:** *Start the whole presentation* (14:31, all automatic) · *Start at natural speech speed* (16:46) · *Live Checkpoint 2* (parts 1–3 play by themselves, then Walid presents; 15:33 planned).

**Controls:** → / ← move; Space or P pauses everything; C captions; N script notes; F full screen. During the film, → or Esc skips it. On the last Checkpoint 1 slide → starts the team; ← on the team's first scene returns. In the console scene, *Run demo* plays the scripted walkthrough; *Next ▶* moves on.

## Where the files are

| File | Where | Size |
|---|---|---:|
| `EU_Tender_Final_Presentation.html` (all four parts) | GitHub Release asset (too large for the web uploader) | 29 MB |
| `Act_I_The_Search_cinematic.mp4` (the film alone) | GitHub Release asset | 14 MB |
| `dist/Checkpoint2.html` (part 4 alone, with live / narrated / own-recordings modes) | this folder | 5.5 MB |
| `dist/Team_scene.html` (part 3 alone) | this folder | 1.3 MB |
| `dist/CHECKPOINT2_SCRIPTS.md` (scripts c2-00 … c2-12, for rehearsal or recording) | this folder | |
| `RUN_SHEET.md` (on the day: timing, pre-flight, fallbacks, likely questions) | this folder | |

## How it is built

Four parts, each with its own build script and README, merged by `parts/02_checkpoint1/build_checkpoint1.py`:

| Folder | Builds | Inputs not in the repository |
|---|---|---|
| `parts/01_film_act1/` | `cinematic_sound.py`: voice-over, sound design and mix onto the film | the *Act I: The Search* package (film, score, modem sound); Piper voices |
| `parts/02_checkpoint1/` | `build_checkpoint1.py`: Checkpoint 1 slides with full recordings; with `--film --team --c2` the final file | the Checkpoint 1 deck source (`EU_Tender_Autoplay_Presentation_v8_Source_Interactive_v11`) |
| `parts/03_team/` | `make_voices.py`, `build_team.py`: the agents' scene and `team_embed.json` | the cartoon `m13.jpg` (face crop); Piper voices for re-voicing |
| `parts/04_checkpoint2/` | `make_narration.py`, `voice_clone.py`, `build_checkpoint2.py`: Checkpoint 2 and `checkpoint2_embed.json` | Piper voices; kNN-VC weights; Walid's Checkpoint 1 audio (for the clone) |

`parts/README.md` has the full build chain. Piper voices: github.com/rhasspy/piper/releases (v0.0.2). kNN-VC: github.com/bshall/knn-vc (WavLM-Large and the prematched HiFi-GAN, from its releases). Fonts are OFL (Inter, Oswald, Space Grotesk, JetBrains Mono, Cinzel). The recorded voices in `parts/03_team/voices` and `parts/04_checkpoint2/voice*` are committed, so a rebuild needs neither Piper nor kNN-VC.

## Transparency

* The agents' voices, the film's voices and the Checkpoint 2 rehearsal voice are AI-generated (Piper) and labelled on screen.
* The Checkpoint 2 narration is an **AI voice clone of Walid's own voice**, made at his request from his Checkpoint 1 recordings (kNN-VC). Every slide that uses it carries the label "AI voice clone of the presenter". The live mode has no synthetic voice at all.
* *Built to grow* is a roadmap: the seven agent roles are planned, not built. Person-level matching (recruiting) would make the system high-risk under the EU AI Act and needs re-classification first.
* Numbers on the slides come from the repository: `data/live_run_2026_08_12`, `src/tender_agent/decision_engine`, `evaluation/results/offline_experiment.md`, `analysis/roi_results.json`, `roi_risk_assessment.md`, `eu_ai_act_compliance.md`, `gdpr_documentation.md`, `strategic_plan.md`. The market figures are the European Commission's (public procurement page).

## Earlier approach (kept for reference)

`final_presentation.src.js`, `build_presentation.py`, `install_presentation.py`, `preview.html`, `media-final/`, `version_b_scripts.json` and `VERSION_B_RECORDING_SCRIPTS.md` are the earlier overlay for the Firebase deck (Versions A and B). The final presentation is built from `parts/`; `version_b_scripts.json` still holds the Checkpoint 2 scripts it reads.
