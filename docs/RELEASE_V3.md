# Complete package version 3: Checkpoint 2 and the final presentation

Branch `checkpoint-2`, 10 October 2026. Everything in version 2 is unchanged; version 3 only adds.

## What is new

| Area | Added | Details |
|---|---|---|
| Stage 10 decision engine | hard gates, 4,000-scenario Monte Carlo per bid, exact portfolio optimiser, proposal outlines, CLI, `POST /decision-engine/run`, n8n Stage 10 workflow | `docs/CHECKPOINT_2.md` |
| Lightweight UI | `ui/tender_portfolio_console.html`: the 14 live-run tenders, two profiles, sliders, re-optimisation, approval step | same results as Python on 108 settings |
| Evaluation | 23-example dataset, two targets, seven evaluators, LangSmith runner with offline mode | `evaluation/langsmith.md`, `evaluation/results/offline_experiment.md` |
| Business case and compliance | ROI model and Monte Carlo, risk register, EU AI Act classification, GDPR documentation, strategic plan | `analysis/`, `roi_risk_assessment.md`, `eu_ai_act_compliance.md`, `gdpr_documentation.md`, `strategic_plan.md` |
| Final presentation | four-part build (film, Checkpoint 1 as recorded, ten mini-me agents, Checkpoint 2) merged into one self-contained autoplay HTML | `presentation/README.md`, `presentation/RUN_SHEET.md` |
| Growth roadmap | *Built to grow*: legal & compliance, feasibility & project evaluation, PMO & project delivery, recruiting & outsourcing, finance & controlling, corporate strategy & innovation / R&D, governance & public affairs agents on the same contract | Checkpoint 2 slide 12; `docs/FUTURE_DEVELOPMENT_STAGES.md` |

Verification: `PYTHONPATH=src pytest -q` → 22 passed. No API key, token or shared secret in the repository or its history (pattern scan of every commit); `.env` is ignored and only `.env.example` with empty values is tracked.

## Release assets (attach to the GitHub release, not to the repository)

| File | Size | Why not in the repository |
|---|---:|---|
| `EU_Tender_Final_Presentation.html` | 29 MB | over the 25 MB limit of GitHub's web uploader, and a binary that changes with every rebuild |
| `Act_I_The_Search_cinematic.mp4` | 14 MB | video |
| `Checkpoint2_voice_clone_c2-00_to_c2-12.zip` | 3 MB | optional; the same files are in `presentation/parts/04_checkpoint2/voice_walid/` |

## Publish

**A. With git (recommended).** In your local clone:

```bash
git fetch origin
git fetch ./eu-tender-autonomous-agent-2_checkpoint-2.bundle checkpoint-2:checkpoint-2
git checkout checkpoint-2
git push -u origin checkpoint-2
gh pr create --base main --head checkpoint-2 --title "Checkpoint 2 and final presentation" --body-file docs/RELEASE_V3.md
# after merging:
gh release create v3.0 --target main --title "Checkpoint 2 and final presentation" --notes-file docs/RELEASE_V3.md \
  EU_Tender_Final_Presentation.html Act_I_The_Search_cinematic.mp4
```

The bundle contains only the 20 commits after `origin/main` (`43210d7`); verify it with `git bundle verify <file>`. It was tested on a fresh clone of the GitHub repository.

**B. With the GitHub website.** Unzip `…_changed-files.zip` and upload its folders with *Add file → Upload files* on a new branch (`checkpoint-2`). The web uploader takes at most 100 files per upload, so upload in two or three batches (for example `presentation/`, then `src/`, `tests/`, `evaluation/`, `analysis/`, `ui/`, `workflows/`, then the rest), then open a pull request. Create the release under *Releases → Draft a new release* and attach the assets above.

**Optional: GitHub Pages.** The final HTML is self-contained, so it can be served as a page: put a copy as `docs/presentation/index.html` on a `gh-pages` branch, or link the release asset. A public page also makes the AI voice clone public; decide that deliberately.

## Before making the repository or release public

- Rotate every credential that was ever in the earlier shared archive.
- The Checkpoint 2 narration (`voice_walid/`, and inside the final HTML) is an AI clone of Walid's voice. It is labelled, but once public anyone can download it. Keep the release private, or publish only the live-mode file, if that matters.
- `Projects_ Evidences_ (Screenshots & Screenrocordings )/` is already on `main`; it is listed in `.gitignore` but tracked. Check that no screenshot shows a key, a token or a personal email address.
