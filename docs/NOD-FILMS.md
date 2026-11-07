# Nod films: production record (7 Nov 2026, v2)

Three vertical films (1080 x 1920, H.264, 30 fps, AAC 48 kHz) plus website assets.

| File | Length | Story |
|---|---|---|
| `media/out/nod-everyday-final.mp4` | 12.1 s | "Bins out tonight." Typed on Nod, screen sleeps. "One less thing on your mind." |
| `media/out/nod-product-final.mp4` | 14.7 s | Hero on a table ("Less screen."), close-up of the real keyboard, three proposed colours, "Less screen. More life." |
| `media/out/nod-launch-final.mp4` | 21.2 s | Everyday moment, then the device, colours and close-up, ending on "One less thing on your mind." and the follow-the-build card |
| `media/out/nod-thumbnail.jpg` | | Vertical thumbnail |
| `media/stills/` | | Orange, cream and mint top-down stills, tilted concept still, label-free exploded view (Flow references) |
| `site/media/` | | 720p web encodes (0.9–1.8 MB), posters, `nod-exploded.webp`, `nod-og.jpg` |
| `media/films/captions/*.srt` | | On-screen text as subtitles (no speech in the films) |

## What changed in v2, and why

The owner judged v1 not production-ready: the device looked wrong, the exploded case looked like flat sheets, the films felt like slides and the copy was generic. Two independent reviews ran, then critiqued each other: a Claude Sonnet creative director (`docs/audits/NOD-CREATIVE-DIRECTION.md`) and DeepSeek via OpenRouter (`docs/audits/NOD-DEEPSEEK-AUDIT.md`, $0.0068 in total). Adopted:

- **Device rebuilt from the official M5Stack photos.** Two-tone grey body, raised screen block, white legend strips over black pill keys, coloured fn, Aa, opt and esc chips, both screws, the label panel and the Stamp board.
  - **Overlay gate:** the render laid 50% over the official top view lines up within about 1 mm. Reproduce it with the "bare" scene in `stills`; the recipe is in `media/refs/m5stack-official/SOURCE.txt`.
  - The photos themselves are M5Stack copyright and are kept out of git.
- **Real thickness everywhere** (stacked CSS 3D layers).
  - The case: 19.6 mm device + 2 mm case.
  - The exploded view: front frame with a 5 mm skirt, the device's two-tone body, back tray with 2.4 mm walls, snap tabs, vents and a USB-C cut-out, matching `hardware/case/nod_case.scad`.
- **No slides.** Title, "uses", "vision" and "size" cards are cut. Every shot is footage or a lit tabletop, with hard cuts and a camera move in every shot.
- **Few words, one sentence per line**, 96–112 px.
- **Honesty, once and readable.** "Concept film. Generated scene." / "Concept render. Proposed printed case." at the start (36 px), "Screen simulated" on the typing shot, "Proposed cases · not printed yet" on colours, and the end card.
- **No fake confirmation.** The "Saved to Notes" tick is gone. The screen shows typing only, then sleeps.
- **Sound on beats only.** Key clicks while typing, one soft note on the end card, room tone. Cuts are silent.

Rejected (with reasons in the audits): Flow shot count of three (one is enough), "sound on every cut", the handwritten note (the note is typed on Nod so the story connects), and DeepSeek's key sizes and raised-block position (both contradicted by the official photos). The three-colour beat is kept because the owner's brief asks for it.

## Source audit (unchanged from v1)

One Google Flow clip, `media/source/flow-original-01.mp4` (8.04 s, 720p). Only shot A (hallway, 0–2.08 s) is used: graded, upscaled, slowed to 3.2 s. Shots B, C and D and the portrait still showed the wrong hardware and are not used. The hallway footage carries 720p detail.

## Claims

- **Generated:** the man in the hallway.
- **Concept renders:** all device shots, labelled as such.
- **Real:** the Cardputer ADV and its published size; the case CAD (not printed).
- **Shown:** typing a short note (typed notes are in firmware v1.5, not yet confirmed on the device), the three proposed colours.
- **Not shown or claimed:** confirmations, reminders, voice, prices, dates, orders, UK manufacture.

## Toolchain

HyperFrames 0.9.20 (Apache-2.0) + GSAP 3.14.2 (vendored, free licence) + FFmpeg.

Researched and not installed: brag/brag-slim, Remotion (company licence above 3 staff), Remocn, Cinetic, Motion Skills, Motion Canvas, Editly. They duplicate HyperFrames or target software launches, and the gap was direction and footage, not tooling. LosslessCut is recommended for trimming real device footage once it exists. Full comparison: `docs/audits/NOD-CREATIVE-DIRECTION.md` §B.

## Rebuild

```bash
bash media/films/render.sh   # build.mjs → 3 renders → mastering → site/media web versions, posters, stills, exploded, og image
```

- **Scene list and timings:** `media/films/build.mjs` (durations only; everything else is derived).
- **Device, case and scene designs:** `media/films/shared/nod.js` and `nod.css`.
- **Generated project folders** are git-ignored. To edit in Studio: `cd media/films/launch && npx hyperframes@0.9.20 preview`.
- **Quality gates run:**
  - `hyperframes check` passes on all three films.
  - Real-time playback was captured in a 390 px browser, and every frame is readable.
  - `node --test site/tests/site.test.mjs` passes 10/10.

## The one Google Flow shot worth generating (optional, pending Maz)

It would add a real-looking hand. The films stand without it.

- **Model:** Veo 3.1 Fast (or Lite) · **Mode:** Ingredients to Video · **Duration:** 8 s · **Aspect:** 9:16
- **References:** `media/stills/nod-original-orange.png` and `media/flow-refs/F1-character-ref-hallway-first.png`
- **Prompt:**

  > Close-up on an oak hallway table in soft morning light. A man's hand in a navy wool coat sleeve picks up the small orange device from the reference image, exactly as shown: a landscape pocket device 84 by 54 millimetres and about 20 millimetres thick, in a rounded orange case. It has a small dark screen left of centre, a white module window on the right, and below them four rows of fourteen small black pill-shaped keys, each row under a white strip of printed letters. He types a few keys with his thumb, puts it down and his hand leaves the frame. Shallow depth of field, slow push-in, natural motion, five fingers, no readable text on the screen, no D-pad, no round game buttons, no logos.

- **Reject the result if:** the screen is wider than about 35% of the device, there's a D-pad or round game buttons, there are fewer than four key rows, or the keys aren't black pills under white strips.
- **After:** put the clip in `media/source/`, add a footage scene in `build.mjs` after the hallway shot, then run `render.sh`.

## Social description

> Ever get to the front door and remember the bins? Nod is a small pocket device being designed in the UK: type it, put it away, get on with your evening. Less screen. More life. Early concept, built in the open: nod-kickstarter.vercel.app
