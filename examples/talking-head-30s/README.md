# Talking head · 30s

A 30-second vertical (1080×1920) talking-head video built entirely with HyperFrames
from data that already ships in this repository:

- **A-roll** — the presenter take used by the `overlay-montage-prod` producer
  regression fixture (`packages/producer/tests/overlay-montage-prod/src/index.html`).
- **Transcript** — that fixture's word-level whisper transcript, saved here as
  `transcript.json` (source timings).
- **Texture** — `grain-overlay` and `vignette` from the registry
  (`hyperframes add grain-overlay`, `hyperframes add vignette`), pasted inline.

## What the composition does

- Cuts the 42s take down to 29s of speech with 4 jump cuts placed on silences
  (five `<video>` + five `<audio>` clips sharing one source via `data-media-start`),
  alternating framing on every cut plus two digital punch-ins inside longer segments.
- Remaps every transcript word through the cuts and drives karaoke captions from it
  (one group visible at a time, hard kill at group end, accent on key words).
- A step panel with accent-wipe transitions: hook → step 01 (account chips tick off)
  → step 02 (five-day tracker fills on "first five days") → step 03 → closing lines
  that light up as they are spoken.
- Progress bar + step tracker, then a recap end card and fade to black at 30s.

| Out time    | Source time | Beat                                               |
| ----------- | ----------- | -------------------------------------------------- |
| 0.00–3.80   | 0.15–3.95   | Hook: "Welcome to your first week"                 |
| 3.80–14.15  | 4.50–14.85  | Step 01: accounts                                  |
| 14.15–22.37 | 15.30–23.52 | Step 02: compliance training                       |
| 22.38–25.46 | 23.97–27.05 | Step 03: one-on-one                                |
| 25.46–29.00 | 38.82–42.36 | "Don't sit on questions. Ask early and ask often." |
| 28.68–30.00 | —           | Recap end card, fade to black                      |

Every overlay cue in the script is anchored to a word index in `WORDS`
(`at(32)` = "Slack,"), so re-cutting only means regenerating the word list.

> **Why five clips, not more:** with six or more `<video>` elements the render deadlocks
> at the first captured frame (Chrome caps a host at six concurrent connections and each
> video holds one against the engine's local file server). Five renders cleanly.

Type: Instrument Serif (statements), Bricolage Grotesque 800 (captions), JetBrains Mono
(metadata). The two Google Fonts (SIL OFL) are vendored in `fonts/`.

## Run it

The source take has a keyframe only every 10s, which makes Chrome stall when it seeks
seven clips of it. `fetch:media` re-encodes it with a 1s GOP (the fix the HyperFrames
compiler suggests in its `sparse keyframes` warning).

```bash
npm run fetch:media   # downloads the take and re-encodes it to aroll.mp4 (git-ignored)
npm run check         # lint + validate + inspect
npm run dev           # studio preview
npm run render        # MP4
```
