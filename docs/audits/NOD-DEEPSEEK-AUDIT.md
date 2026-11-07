# Independent audit by DeepSeek via OpenRouter (7 Nov 2026)

Runner: `node run.mjs` (local; key from env). Requested model `deepseek/deepseek-v4-flash-0731:free` is not listed on OpenRouter today; used `deepseek/deepseek-v4-flash-0731` (same model, paid tier, text-only) for hardware/print/tools and `deepseek/deepseek-v4.1-flash` (image input) for the visual audit. Total cost reported by OpenRouter: $0.00430. Time 34 s.

Images sent: 1-official-top.jpg, 2-official-side.jpg, 3-nod-render-assembled.jpg, 4-nod-render-exploded.jpg, 5-nod-colours-frame.jpg, 6-nod-launch-every-2s.jpg, 7-case-cad-exploded.jpg.

## 1. Visual-quality audit (deepseek/deepseek-v4.1-flash)

# Nod Visual Audit — Renders 3–6 vs. Ground Truth 1–2 & CAD 7

## 1. Hardware inaccuracies (renders 3–6)

**Screen.** Nod's screen is ~40% of body width, centred. Ground truth: 1.14" 16:9 = **25.2 × 14.2 mm = 30% × 26% of 84 × 54**. Left edge sits at ~22% (18.5 mm), vertically centred in the 24 mm top block. Fix: `width:30%; height:26%; left:22%; top:8%` of the 84×54 frame; bezel 1.5 mm dark #0A0A0A, not the current oversized black slab.

**Stamp module.** Rendered as a flat dark rectangle with a green dot. Real part is a **raised 25 mm-wide block (30% of width) on the +X end**, 3.6 mm proud of the deck, showing green PCB, CE/FCC/STAMPS3A silkscreen, and a metal shield can. Fix: layered div with `box-shadow: 0 3.6px 0 #1A1A1A, 0 6px 8px rgba(0,0,0,.35)` plus 4–6 px micro-text labels.

**Two-tone body.** Nod is monochrome. Real device: **light grey top (16 mm deck + screen block) over dark charcoal base (3.6 mm)**. Fix: split body into two stacked divs with a 0.4 mm seam line at y=16 mm.

**Raised end block.** Missing. The +X end is 19.6 mm vs 16 mm deck. Fix: add a 3.6 mm step on the right 30% in all 3/4 views.

**Keys.** Nod shows white rounded pills on black. Real: **black #1A1A1A keycaps, 5.8 × 7.5 mm pitch, 1.2 mm radius, dished top, white 4 px legends**, with coloured modifier legends (orange esc, green opt, blue Aa, orange fn). Fix: 14 × 4 grid, `gap:0`, keycap `width:5.8mm; height:7.5mm; border-radius:1.2mm`, legends at 4 px Manrope.

**Legend strips.** Entirely absent. Fix: add per-key text.

**Screws.** Two visible screws on the top block (near screen and Stamp). Fix: 2 mm circles, #8A8A8A, at (24 mm, 6 mm) and (62 mm, 6 mm).

**Ports.** USB-C + 3.5 mm jack on +X end; Grove on −X; microSD + power switch on screen-end edge. None rendered. Fix: 8.5 × 3.2 mm USB-C slot, 6 mm jack circle, 10 × 4 mm Grove notch, 12 × 2 mm microSD slot.

**Mic.** Real mic hole is left of the screen block, ~3 mm. Nod's dot is misplaced and too small.

**Thickness.** Renders read as a flat slab. Fix: show 19.6 mm in 3/4 views with `perspective: 800px; rotateX(12deg) rotateY(-18deg)`.

## 2. Why the exploded case reads as flat sheets

Parts 4 and 7 are zero-thickness rounded rectangles with a drop shadow — no extrusion, no wall, no mating features. To read as FDM:

- **Extrude 2.4 mm walls**: draw the front frame as a perimeter band 2.4 mm wide with an inner recessed lip (0.30 mm clearance) that receives the back shell.
- **Snap tabs**: 0.4 mm bumps on the inner wall, matching recesses on the shell — show as small trapezoids with a highlight edge.
- **Port cut-outs**: USB-C, jack, Grove, microSD, power — each must show the 2.4 mm wall depth as a visible inner face, not a hole in paper.
- **Layer lines**: 0.2 mm horizontal striations on vertical faces (repeating-linear-gradient at 8% opacity).
- **Chamfers**: 0.5 mm on all outer edges; 0.2 mm on inner.
- **Shadows**: contact shadow between frame and shell, ambient occlusion inside the lip, soft cast shadow on the ground plane.
- **2.5D**: use SVG isometric projection or CSS `rotateX(55deg) rotateZ(-45deg)` with layered `box-shadow` stacks to fake extrusion; never a single flat fill.

## 3. Why film frames feel like slides

Static centred compositions, flat ambient light, no camera movement, uniform type scale, grid layout, everything on one plane.

1. **Lighting**: add a directional key at 45°, soft fill, rim light on the device edge; warm window practical for live-action. Kill the flat ambient.
2. **Depth**: shallow DOF — blur background 8–12 px, keep device sharp; add foreground hand/desk edge for layering.
3. **Camera moves**: 2–3% slow push-in over 3 s, parallax between device and background, subtle handheld drift. No static frames.
4. **Composition**: rule of thirds, off-centre device, negative space for text, diagonal desk lines. Break the grid.
5. **Typography**: headline 8–10% of frame height, body 2–3%, clear hierarchy. Currently all text floats at similar size.
6. **Pacing**: 2–3 s per beat, cut on motion, vary shot length (1 s / 3 s / 5 s), match cuts. Currently uniform 2 s.

## 4. Top 8 fixes, ranked

1. **Screen size/position** — 30% width, left 22%, top 8%. Biggest accuracy gap.
2. **Two-tone body + raised end block** — light top 16 mm, dark base 3.6 mm, right block 19.6 mm.
3. **Stamp module as raised block** — 25 mm wide, 3.6 mm proud, PCB + cert markings.
4. **Keys** — black 5.8 × 7.5 mm keycaps, white legends, coloured modifiers.
5. **Extrude case parts** — 2.4 mm walls, lips, snap tabs, port cut-outs, layer lines.
6. **Ports/screws/mic** — USB-C, jack, Grove, microSD, 2 screws, mic hole.
7. **Lighting + DOF in film frames** — key/rim/fill, background blur, foreground layers.
8. **Camera moves + type hierarchy** — push-in, parallax, 8–10% headlines, varied pacing.

## 2. Hardware sourcing, print feasibility, claims, tools (deepseek/deepseek-v4-flash-0731)

null


## 2b. Rerun: hardware, print feasibility, claims + critique of the creative plan (deepseek/deepseek-v4-flash-0731, $0.00246, finish: stop)

The first text call returned empty content (its output budget went on reasoning), so it was rerun with a larger budget.

# Part 1 — Hardware & production audit

## A. UK buyers: where and what risks

- **Genuine sources:** M5Stack's official store (m5stack.com) ships to the UK; expect import VAT and 1–2 week delivery. UK resellers such as **The Pi Hut** and **Pimoroni** have carried M5Stack lines — verify against M5Stack's own reseller list before buying. I could **not verify** a single dedicated UK distributor from memory; check.
- **Genuine ADV** = model code **K132-ADV** on the box/PCB. Risks:
  - **Older v1.1 Cardputer stock** lacks the 3.5 mm jack and IMU. Ask the seller for a photo of the top/screw-end edge showing the jack before paying.
  - **Battery changed 1750 → 1500 mAh in July 2026** — if true, current stock is lighter. I cannot confirm that date from memory; check M5Stack's product changelog. If you buy from old stock, you get 1750 mAh; after that date, expect 1500.
  - Clones/refurbs on marketplaces use ESP32-S3 with less flash, broken USB, or non-genuine keyboards.
- **Genuine check:** K132-ADV code, jack present, 56 keys, 84 × 54 × 19.6 mm dimensions.

## B. Home FDM feasibility — numbers

Design targets: wall 2.4, clr 0.30, clr_z 0.30, joint_gap 0.18, snap_depth 0.40, lip_h 0.7.

- **2.4 mm wall with a 0.4 mm nozzle** = 6 perimeters. Fine for PLA and PETG.
- **0.30 mm clearance:** at 0.2 mm layer height, acceptable for PLA. PETG fuses and squishes more — plan **0.40 mm horizontal** for PETG, or drop to 0.15 mm layers.
- **joint_gap 0.18 mm:** tight. Expect interference; ream or set 0.25–0.30.
- **snap_depth 0.40 mm:** a gentle snap. With a 2.4 mm wall the arm is stiff, so it will feel rigid, not brittle. Snap bumps need chamfers on both sides.
- **Orientation:** flat on the bed, keyboard up. Back shell's lanyard tab needs a small support. The 5 mm skirt over the shell is a **45–60° chamfer**, printable if tapered — a square skirt will fail.
- **Bridging:** the keyboard window is 56 small holes at 5.8 × 7.5 mm pitch — no long bridges, fine.
- **Rim stiffness:** the raised screen/Stamp end (19.6 mm) is the crack-risk zone; add fillets inside the lip.
- **Caliper first:** device width (84.0), height of the raised block, key pitch, the Stamp module's position in the top-right, and the switch/microSD cutouts on the screen-edge end.
- **5-step fit-test plan:**
  1. Print 20 mm clearance coupons with 0.25 / 0.30 / 0.40 mm gaps; measure slip.
  2. Print back shell only; insert device; check the raised end and switch cutout.
  3. Print front frame only; check key window, skirt, and press every key.
  4. Print one snap pair; 10 insert/remove cycles.
  5. Full assembly with M2 screws; check microSD and Grove access.

## C. Safe marketing phrasing

- Case: *"Proposed 3D-printable case design. Not yet printed or fit-tested."*
- Screen: *"Concept render — screen shown is illustrative, not real."*
- Avoid "fits", "works with", or "for the Cardputer" as if validated. Say "drawn to published dimensions."

---

# Part 2 — Creative plan critique

**Strong:** the "being built to" language; killing the fake "Saved to Notes" green tick; cutting the title-card slides; moving the exploded view to the website; hard cuts + camera moves; explicit rejection criteria for the Flow shots; honesty label at start and end.

**Wrong / risky:**

1. **The plan breaks its own honesty rule.** The rewrite says "open on a 1.2 s small caption", but the Video 1 table has no caption at 0.0–0.8. The end card alone isn't enough.
2. **The AI clip count is wrong.** The hallway shot is already generated; the combined launch uses **4 AI clips** (hallway + 3 new Flow shots), not 3. "One generated clip" is already inaccurate — fix the honesty wording before anyone else does.
3. **Flow cost: compute is cheap, time is not.** If Fast-tier pricing follows 2025 patterns, 3 × 8 s ≈ **$3–4 of raw compute**. But the hand-with-Nod shot will be rejected repeatedly — exact 84 × 54 proportions, 4 × 14 keys, no readable text, five fingers. Expect **20–50 takes**, roughly **$10–25** in compute plus a day of contact-sheet review. The "screen bigger than a third of width" rejection is near-impossible: the real screen is ~30% of device width.
4. **"A sound event on every cut" is a slide-deck rule.** It's exactly how the original film got its chimey PowerPoint feel. Use sounds on the beats that matter (phone thud, first key click, door latch) and cut in air.
5. **Video 2's handwritten hallway note contradicts the product.** Nod's demo is *typed* notes; a handwritten note severs the connection between the two videos.
6. **The 2 s "three cases" beat** is a slide wearing a costume — it shows three products the project doesn't have. Cut it; list colours in the end-card copy.
7. **Key clicks over a render/Flow hand are still fake** until real clicks are recorded. Book that with the hardware audit.

**My 5 changes:**

1. **Keep the existing hallway clip.** Don't regenerate it. Spend the generation budget on one shot: hand with Nod.
2. **Source the phone-trap shot from stock or film it locally.** A real hand, a real phone, 60 minutes. That removes one AI shot and gives the film a genuinely non-generated anchor. The combined film then has 2 AI clips, both labelled.
3. **Replace "sound on every cut" with beat-based sound:** silent cuts, then the first key click, then the door latch, then held room tone.
4. **Make the hallway note a typed note** — same typeface, wiped in after the key clicks — so Video 2 connects to the device.
5. **Add the start caption to the tables** and cut the "three proposed cases" beat entirely. Also verify that "Veo 3.1 Fast" is the actual current API name — I couldn't confirm it.
