# Part 04: Checkpoint 2, one self-contained HTML

`Checkpoint2.html` (about 5 MB): thirteen scenes on the Checkpoint 1 deck engine, same look and controls.

| # | Scene | Media |
|---:|---|---|
| 0 | Why it matters: 250,000+ authorities, ≈ €2 trillion a year; finding calls is easy, deciding is where firms lose money | three big numbers, EC source |
| 1 | What the data showed: 7 of 14 advanced tenders were not biddable | live-run table |
| 2 | Each bid is a distribution (4,000 scenarios, two profiles) | range chart |
| 3 | Choose the portfolio (127 portfolios, exact) | comparison table |
| 4 | The portfolio console, live | the real console inside the slide, scripted walkthrough |
| 5 | Evaluation: 0.20 → 1.00 on non-biddable records | evaluator table, fixed / open |
| 6 | ROI: break-even month 7, +65% / +161% | 36-month chart, Monte Carlo range |
| 7 | Twelve risks, two already happened | risk table |
| 8 | EU AI Act: not prohibited, not high-risk, two duties | classification ladder |
| 9 | GDPR: proceed with conditions | three cards |
| 10 | POC → pilot → deployment, success criteria, price | timeline |
| 11 | Built to grow: seven planned agents (legal, feasibility, PMO, recruiting, finance, strategy and R&D, public affairs) plug into the same pipeline | today's ten agents, eight dashed cards |
| 12 | Recommendation: pilot under four conditions; thank you | Walid as an AI agent (mini-me robot) |

Start card, three ways to run it:

* **Present live**: no narration, captions off, you advance with →. Scripts are in Notes (N). In scene 4 click Run demo, or use the console yourself; Next ▶ moves on.
* **Play with narration**: an AI rehearsal voice reads the scripts (labelled on every slide), with exact subtitles; each slide moves on when the voice ends, and the console walkthrough follows the narration clock.
* **Load my recordings**: select `c2-00` … `c2-12` (m4a, mp3 or wav) and they replace the AI voice; timings and subtitles follow your files.

Files: `checkpoint2_slides.js` (content), `../../version_b_scripts.json` (scripts), `CHECKPOINT2_SCRIPTS.md` (for rehearsal and recording), `make_narration.py` (Piper voice, sentence-timed cues into `voice/`), `fonts/` (the console's fonts, OFL), `build_checkpoint2.py`.

```bash
python3 make_narration.py <piper voices folder>        # only after changing a script
python3 build_checkpoint2.py <Checkpoint 1 source folder> <out folder> --face <face.jpg from ../03_team build>
```

Numbers come from the repository: `data/live_run_2026_08_12`, the decision engine, `evaluation/results/offline_experiment.md`, `analysis/roi_results.json`, `roi_risk_assessment.md`, `eu_ai_act_compliance.md`, `gdpr_documentation.md`, `strategic_plan.md`. The evaluation is the offline run of the LangSmith dataset and evaluators (7 Oct 2026); once the experiment is uploaded to LangSmith, replace the subtitle of scene 5 or add the compare-view screenshot.

## Narration in Walid's own voice (AI clone, at his request)

`voice_clone.py` converts the sentence-timed narration into Walid's voice with kNN-VC (WavLM-Large features, HiFi-GAN vocoder; github.com/bshall/knn-vc), matching every 20 ms frame against 19 minutes of his Checkpoint 1 recordings. Words and timing stay those of the script, so the subtitles still fit; the voice is his. Output in `voice_walid/`. Build with `--clone voice_walid`: the start button reads "Play in my voice (AI clone)" and every slide carries the label "AI voice clone of the presenter".

```bash
python3 voice_clone.py <knn-vc repo> <folder of his Checkpoint 1 audio as 16 kHz wav> voice_walid
python3 build_checkpoint2.py <CP1 source> <out> --face <face.jpg> --clone voice_walid
```
