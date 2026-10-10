# Part 01: Act I "The Search", with a cinematic voice-over

Walid's opening film (100 s, picture unchanged) gets a told story and a film-style sound mix:

* **Voices** (AI-generated offline with Piper, labelled in the deck): the grandson asks, the grandfather remembers (warm, slower, a little reverb for the memory, 0:00–0:44), and a deep storyteller takes over for the present and the title (0:44–1:40). The words follow the film's script and its burnt-in captions.
* **Music and modem**: the film's own score and the dial-up recording, ducked by 9 dB whenever someone speaks; the modem gets a slight telephone band so it sits in the memory.
* **Sound design**: park wind and birds; a tape-rewind and hit into the flashback; a clock under "Still connecting"; a hit and shimmer on CONNECTED; whooshes on the cuts; a riser, impact and braam when the agent arrives; a riser, sub boom and braam under the title.
* **Master**: about −15 LUFS, peaks below −3 dBFS, close to the Checkpoint 1 recordings (−16.5 LUFS) so the hand-over is smooth.

```bash
python3 cinematic_sound.py <Act_I_The_Search package folder> <piper voices folder> <out folder>
```

Writes `Act_I_The_Search_cinematic.mp4` (same picture, new sound), `act1_mix.wav` and `act1_voice.wav`. Timing and wording of each line are in `CUES` at the top of the script; voices in `ROLES`.

To play the film before Checkpoint 1 in one file:

```bash
python3 ../02_checkpoint1/build_checkpoint1.py <CP1 source folder> <out folder> --film <out folder>/Act_I_The_Search_cinematic.mp4
```
