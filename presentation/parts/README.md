# The final presentation, built from four parts

`EU_Tender_Final_Presentation.html` (about 29 MB, everything inside): one Start click plays

| Part | What | Length |
|---|---|---:|
| 01 | Act I "The Search": the film with cinematic voice-over and sound (`01_film_act1`) | 1:40 |
| 02 | Checkpoint 1 as recorded: 6 whole slides, original recordings (`02_checkpoint1`) | 5:56 at the 15-minute pace |
| 03 | Meet the team: "Ten of Me. Zero Guesswork." (`03_team`) | 1:33 |
| 04 | Checkpoint 2: 13 scenes with the portfolio console and the growth roadmap (`04_checkpoint2`) | 5:22 narrated (AI clone of Walid's voice) · 6:25 live |

Start card: **Start the whole presentation** (14:31, all automatic) · **natural speech speed** (16:46) · **Live Checkpoint 2** (film, Checkpoint 1 and the team play by themselves, then Walid presents; → advances, scripts in Notes, Run demo in the console).

Moving around: → on the last Checkpoint 1 slide starts the team; ← on the team's first scene returns; the team's end starts Checkpoint 2. Space or P pauses, C captions, N notes, F full screen.

Build (after building parts 01, 03 and 04):

```bash
python3 03_team/build_team.py <m13.jpg> 03_team/voices <team out>
python3 04_checkpoint2/build_checkpoint2.py <CP1 source> <c2 out> --face <team out>/face.jpg --clone 04_checkpoint2/voice_walid
python3 02_checkpoint1/build_checkpoint1.py <CP1 source> <final out> --film <Act_I_The_Search_cinematic.mp4> \
        --team <team out>/team_embed.json --c2 <c2 out>/checkpoint2_embed.json
```

To stay under 30 MB the merged build encodes the film at CRF 31, the presenter videos at 480 px CRF 33, the evidence recording at CRF 35 and the Checkpoint 2 voice at 48 kbit/s.
