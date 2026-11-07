# Nod films: production record (7 Nov 2026)

Three vertical films (1080 x 1920, H.264, 30 fps, AAC 48 kHz) and website assets, built from one Google Flow clip plus accurate concept renders.

| File | Length | What it is |
|---|---|---|
| `media/out/nod-everyday-final.mp4` | 14.9 s | "One less thing on your mind." Everyday moment, save a thought, back to the day |
| `media/out/nod-product-final.mp4` | 18.6 s | "Less screen. More life." Product, what makes a Nod (exploded), three colours, real size |
| `media/out/nod-launch-final.mp4` | 26.5 s | Problem → what Nod is for → save a thought → product → colours → vision → brand + follow CTA |
| `media/out/nod-thumbnail.jpg` | | Vertical social thumbnail ("Meet nod.") |
| `media/stills/*.png` | | Clean concept stills: orange, cream, mint, tilted "Saved to Notes", exploded (with and without labels) |
| `site/media/` | | 720p web encodes (1.2–2.1 MB), posters, `nod-exploded.webp`, `nod-og.jpg` link preview |
| `media/films/captions/*.srt` | | On-screen text as subtitle files (the films have no speech) |

## Source audit (Google Flow clip `media/source/flow-original-01.mp4`, 8.04 s, 720 x 1280, 24 fps)

Both "attached videos" were the same file (identical MD5), so there was one source.

| Shot | Time | Verdict | Why |
|---|---|---|---|
| A: man in hallway with keys, pauses at the table | 0.00–2.08 | **Kept** (graded, upscaled, slowed to fill) | Natural, no device in frame, a relatable "about to forget" beat |
| B: close-up, hand taps device | 2.13–4.00 | **Replaced** | Device is wrong: screen on the right, chunky toy keys, no Cardputer layout. Cropping it out would hide the device dishonestly |
| C: three colourways on a table | 4.00–5.96 | **Replaced** | Oversized screen, invented D-pad and buttons, far fewer than 56 keys |
| D: end card | 5.96–8.04 | **Replaced** | Same inaccurate device, truncated hex label "#EE5A3", design-file colour callouts |
| Portrait still (`flow-still-portrait-REJECTED.png`) | | **Rejected** | Tall calculator shape, oversized screen: not a Cardputer ADV |

Replacement: an HTML/CSS render of the Cardputer ADV in the proposed case, built from `hardware/case/DIMENSIONS.md` (84 x 54 mm body, 2 mm case wall, 24.9 x 15.5 mm screen window 8.85 mm left of centre, 4 x 14 keys at 5.8 x 7.5 mm pitch, Stamp window on the right, mic hole). Three colourways share the same geometry by construction (one function, one colour variable). The exploded view uses the real window cut-outs from the case SCAD.

Honest limits: the hallway footage is 720p upscaled to 1080p, so it carries 720p detail. The renders are stylised (CSS, not ray-traced), and the case looks smoother than a real FDM print would.

## What is generated, what is real, what is claimed

- **Generated (Google Flow):** the man in the hallway. Labelled on screen "Concept film · generated scene".
- **Concept renders:** every device shot. Labelled on screen "Concept render", "screen simulated", "case not yet printed / fit-tested".
- **Real:** the Cardputer ADV hardware and its published dimensions; the case design files in `hardware/case/` (not yet printed).
- **Claims shown:** saving a typed note ("Saved to Notes", which matches the notes feature in v1.5, not yet confirmed on the device), three proposed colours, the real size. No prices, dates, orders, reminders, wake-word or "AI" claims. The "uses" scene ("Remember the thing…") is labelled "What we are building towards · in development".
- **Not claimed:** the films never show a real hand on a real device. That needs real test footage (`docs/NOD-FILM-PLAN.md`).

## Toolchain (chosen, and why)

| Tool | Licence | Use |
|---|---|---|
| **HyperFrames 0.9.20** (`npx hyperframes`, heygen-com/hyperframes) | Apache-2.0 | HTML → MP4 renderer: seekable GSAP timeline, `check` (lint, contrast, layout, reading-time), `snapshot` |
| **GSAP 3.14.2** (vendored in `media/films/shared/`) | GreenSock standard licence (free, commercial use allowed) | Animation |
| **FFmpeg** (scoop) | LGPL/GPL | Scene detection, grade/upscale of shot A, synthesised sound, mastering, web encodes |

Not used: **Remotion** (its licence needs a paid company licence above a small team size, and HyperFrames already does the job); LosslessCut, auto-editor and PySceneDetect (FFmpeg's `select=gt(scene,…)` found the 3 cuts; nothing to trim by silence). No new installs: everything runs through `npx` and the existing FFmpeg.

Sound is fully synthesised (`media/films/shared/make-sfx.sh`): soft key clicks, a two-note "saved" chime, a warm room-tone bed, plus the hallway clip's own ambience. No music licence needed. Mastered with +6 dB and a −1.5 dBTP limiter (loudness normalisation would pump the room tone).

## Rebuild

```bash
bash media/films/shared/make-sfx.sh   # only if sounds change
bash media/films/render.sh            # node build.mjs + 3 renders + mastering → media/out/
```

- Scenes and timings: `media/films/build.mjs` (durations only; starts, footage clips and sound cues are derived).
- Device and scene designs: `media/films/shared/nod.js` and `nod.css`.
- Generated project folders (`product/`, `everyday/`, `launch/`, `stills/`) are git-ignored and rebuilt by `build.mjs`. Open one in HyperFrames Studio with `cd media/films/launch && npx hyperframes@0.9.20 preview`.
- Web versions: see the FFmpeg block in the 7 Nov handover (720 x 1280, CRF 26, AAC 96k, faststart).

Quality gates run: `hyperframes check` passes on all three films (only warnings left are footnotes crossing during 0.35 s cross-fades); frames reviewed at 1–2 fps across each film; audio peaks at −6.3 dB with no clipping; `node --test site/tests/site.test.mjs` passes 10/10, including the new film-honesty test.

## Google Flow: optional upgrades (pending Maz)

The films are complete without these. Each one replaces a stand-in with better footage.

**Shot F3: he actually leaves** (replaces the reused hallway frames after "Then let it go.")
- Model: Veo 3.1 Fast (Lite is fine) · Mode: **Frames to Video** · Duration: 8 s · Aspect 9:16
- Start frame: `media/flow-refs/F3-start-frame-hallway-last.png`
- Prompt: `The same man in a navy wool coat glances at the note on the table, nods to himself, slips the keys into his coat pocket, turns and walks calmly down the hallway and out of the front door, which closes softly behind him. Static camera at chest height, soft overcast daylight from the door, muted warm colours, natural unhurried movement, realistic hands, no text, no logos, no devices visible.`

**Shot F1: a real-looking hand on an accurate Nod** (could replace the render-only typing beat)
- Model: Veo 3.1 Fast · Mode: **Ingredients to Video** (reference images) · Duration: 8 s · Aspect 9:16
- References: `media/stills/nod-original-orange.png` and `media/flow-refs/F1-character-ref-hallway-first.png`
- Prompt: `Close-up on an oak kitchen counter in soft morning light. A man's hand in a navy wool coat sleeve picks up the small orange device from the reference image, exactly as shown: a landscape 84 by 54 millimetre pocket device with a small screen left of centre, a dark square window on the right, and a full four-row keyboard of 56 tiny cream keys on a dark plate. He presses a few keys with his thumb, puts it down and his hand leaves the frame. Shallow depth of field, slow push-in, natural motion, five fingers, no text overlays, no extra buttons, no D-pad.`
- Reject the result if: the screen is bigger than about a third of the width, any D-pad or round game buttons appear, or the keyboard has fewer than four rows.

After a Flow result: drop it in `media/source/`, add a footage scene in `build.mjs`, re-run `render.sh`.

## Social description

> Ever get to the front door and forget the thing? Nod is a small pocket device we're designing in the UK: tell it, and get on with your day. Less screen. More life. Early concept, built in the open. Follow the build: nod-kickstarter.vercel.app
