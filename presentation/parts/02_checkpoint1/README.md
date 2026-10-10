# Part 02: Checkpoint 1 as recorded

One self-contained HTML file: `Checkpoint1_as_recorded.html` (about 26 MB). Open it in Chrome or Safari, click Start, and it plays by itself.

## Selected slides (whole slides, nothing cut)

| Order | Original slide | Content | Recording | 15-minute pace | Natural |
|---:|---:|---|---|---:|---:|
| 1 | 1 | Title and self-introduction | presenter video | 0:49 | 1:08 |
| 2 | 3 | Discover, Understand, Assess, Decide | presenter video | 0:54 | 1:15 |
| 3 | 4 | Hybrid architecture (n8n + Python), with the focus path | presenter video | 0:49 | 1:08 |
| 4 | 10 | Full autonomous run, with the complete 1:54 recording | narration | 1:31 | 1:54 |
| 5 | 16 | Hurdles and problem solving | narration | 0:48 | 1:16 |
| 6 | 18 | Achievements: 25 → 14 → 11, submission package | presenter video | 1:05 | 1:30 |
| | | **Total** | | **5:56** | **8:11** |

Each slide keeps its complete original recording, its complete subtitle track, its script (Notes) and its evidence. The 15-minute pace is the original deck's own paced mode (speech 1.4× or 1.6×, evidence 1.25×); natural speed plays everything at 1.0×.

## What is inside the file

* The original renderer (`presentation.html`, `.css`, `.js`) inlined, with three small changes: each presenter window keeps the position it had on its original slide; a slide never advances while its recording is still speaking; at the end the page posts `{source: "checkpoint1", event: "complete"}` to a parent page, and it accepts `{target: "checkpoint1", command: "start", mode}` or `?autostart=paced`, for the merged presentation.
* All media as base64, turned into blob URLs when a slide needs them. The presenter videos (640 px wide, they play in a small window) and the evidence recording (1280 px) are re-encoded at full length; narration audio and images are unchanged.

## Rebuild

```bash
python3 build_checkpoint1.py <EU_Tender_Autoplay_Presentation_v8_Source_Interactive_v11 folder> <out folder>
```

Change `SELECTED` in the script to choose other slides.

## With the opening film

`--film <Act_I_The_Search_cinematic.mp4>` writes `Film_and_Checkpoint1.html` (about 29 MB): Start plays Act I full screen, then Checkpoint 1 begins by itself. During the film: Space pauses, → or Esc skips, "Skip film" in the corner. `?film=0` starts straight with Checkpoint 1. To stay under 30 MB the presenter videos are 480 px wide in this build.

## With the team scene

`--team <team_embed.json>` (written by `../03_team/build_team.py`) adds Part 03 after Checkpoint 1 and writes `Film_Checkpoint1_Team.html` (about 29 MB, 9:08 at the 15-minute pace). When the last Checkpoint 1 slide ends, the agents' scene fades in and plays by itself. It runs in a shadow root, so its styles and fonts do not touch the deck. On the last slide, → or Next also starts it; ← on the team's first scene goes back to Checkpoint 1.
