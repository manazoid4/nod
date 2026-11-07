# Piblo: Google Flow (Veo) prompts for concept visuals

Status: DRAFT prompts. Nothing here has been run. Outputs must be checked by the owner before use.

## Rules for every clip

- Label: every output carries the on-screen or caption text **"Concept render — not final hardware"**. Burn it in (bottom left, 36 px at 1080 wide) and repeat it in the caption wherever the clip is posted.
- Never present output as real footage of the Piblo prototype. Real footage is in `real-footage-shotlist.md`.
- No real person's likeness. Use an unnamed adult seen from behind, in silhouette or by hands only. No celebrity or recognisable face.
- No location that identifies a UK town: no street signs, shop names, landmarks, number plates, accents of place in text. Keep rooms and streets generic.
- No readable text on the device screen except the talk circle. No logos. No brand names.
- No price, date or claim text in the picture.
- Palette: warm cream `#FFF4E0`, mint, tomato-orange, sun-yellow, and one blue circle (the "talk circle") on the device screen. The site uses the same family (`site/tokens.css`).
- Check the device shape every time (see "Reject if" below). Earlier generations got the hardware wrong (`docs/NOD-FILMS.md`).

## The device, in words (paste into any prompt that shows it)

A landscape pocket device about 84 by 54 millimetres and 20 millimetres thick, in a rounded orange case. A small dark screen sits left of centre, above four rows of fourteen small black pill-shaped keys, each row under a white strip of printed letters. A white module window sits to the right of the screen. USB-C port on one short edge. No D-pad. No round game buttons. No logos.

## Reject a result if

- The screen is wider than about 35% of the device face.
- There is a D-pad, round game buttons or fewer than four key rows.
- Keys are not black pills under white strips.
- A face is clear or recognisable, or any text names a place.
- The hand has the wrong number of fingers.
- Any readable brand name or logo appears.

## Reference images

All from the repo. Attach in Flow "Ingredients to Video".

| File | Use |
|---|---|
| `media/stills/nod-original-orange.png` | Orange device, the main reference |
| `media/stills/nod-classic-cream.png` | Cream colourway |
| `media/stills/nod-mint.png` | Mint colourway |
| `media/stills/nod-concept-still.png` | Tilted view |
| `media/stills/nod-exploded-bare-full.png` | Layers and case (also `site/media/nod-exploded.webp`) |
| `site/media/nod-product-poster.jpg` | Table scene framing and light |
| `site/media/nod-everyday-poster.jpg` | Hallway grade (re-use only the light and colour, not the man) |

Note: the files still say "nod". The talk-circle Home is not in these stills (it is on an unmerged branch). Describe it in the prompt and check the result.

---

## 1. Hero lifestyle loop (website hero, campaign opener)

- **Purpose:** a calm, warm loop for the top of the campaign page and site, to replace the generated-man hallway film as the hero. Shows the idea (put it down, get on with life) without a face.
- **Reference images:** `media/stills/nod-original-orange.png`, `site/media/nod-product-poster.jpg`
- **Framing and aspect:** 16:9 landscape (also generate 9:16 for social). Slow push-in, shallow depth of field.
- **Duration:** 8 s, designed to loop (end where it starts).
- **Style:** warm cream room, soft morning window light, mint cup, a tomato-orange cushion, sun-yellow flowers in the background. Natural, unhurried.
- **Prompt:**

> Warm morning light on a pale oak table in a generic cream-coloured living room. The small orange pocket device from the reference image sits on the table, exactly as shown: a landscape pocket device 84 by 54 millimetres and about 20 millimetres thick, in a rounded orange case, a small dark screen left of centre above four rows of fourteen small black pill-shaped keys under white printed strips. A hand with five fingers, seen from the wrist down, places a mint-green mug next to it and leaves the frame. In the background, out of focus, a person's silhouette walks away towards a window. Slow gentle push-in, shallow depth of field, soft natural motion, calm mood, loops seamlessly. The device screen shows only a soft blue circle on a dark background. No readable text, no logos, no faces.

- **Negative prompt:** face, recognisable person, readable text, logos, brand names, D-pad, round game buttons, extra keys, street sign, landmark, shop front, phone showing an app, glitch, flicker, extra fingers.
- **Label:** "Concept render — not final hardware"

## 2. Desk scene with the blue talk circle

- **Purpose:** shows the planned Home screen idea (hold a key, talk) in context. Used on the site "How it works" section and in the campaign "In testing" area, clearly as a concept of the interface.
- **Reference images:** `media/stills/nod-original-orange.png`, `media/stills/nod-concept-still.png`
- **Framing and aspect:** 16:9, medium close-up from slightly above and to the side of a desk. One slow lateral camera move.
- **Duration:** 8 s.
- **Style:** cream desk, a small plant, a closed laptop in soft focus, one sun-yellow notebook. The blue talk circle on the device screen gently pulses.
- **Prompt:**

> Close-up on a tidy cream-coloured desk with a closed grey laptop softly out of focus and a small green plant. The small orange pocket device from the reference image sits in the foreground, exactly as shown: a landscape pocket device in a rounded orange case, a small dark screen above four rows of fourteen small black pill-shaped keys under white strips. On the screen is one large flat blue circle on a dark background that gently pulses like a calm breathing light, with no text. A hand with five fingers rests a thumb on one key, then lifts away. Slow lateral camera slide, soft daylight, shallow depth of field, warm cream, mint and sun-yellow palette, quiet mood.

- **Negative prompt:** readable text on screen, logos, brand names, face, window view that shows a town, D-pad, round buttons, lit keyboard glow, sci-fi interface, hologram, extra devices, extra fingers, camera shake.
- **Label:** "Concept render — not final hardware. Interface is a concept."

## 3. Product turntable

- **Purpose:** a clean 360-degree product-style loop to replace the CSS-drawn device in the product film and press kit.
- **Reference images:** `media/stills/nod-original-orange.png`, `media/stills/nod-classic-cream.png`, `media/stills/nod-mint.png`
- **Framing and aspect:** 1:1 square (also 16:9). Locked camera, object rotates a full turn on a plain surface.
- **Duration:** 8 s, seamless loop.
- **Style:** seamless warm cream backdrop, soft studio light, one soft shadow. Orange first. Generate cream and mint as separate clips, one colour per clip.
- **Prompt:**

> A single small orange pocket device from the reference image rotates slowly through one full turn on a seamless warm cream surface, exactly as shown: a landscape pocket device 84 by 54 millimetres and about 20 millimetres thick, rounded orange case, small dark screen left of centre, white module window to the right, four rows of fourteen small black pill-shaped keys under white printed strips, USB-C port on one short edge. Locked-off camera at a slight downward angle, soft studio lighting, gentle shadow, smooth constant rotation, clean product-reel look, no hands, no props, no text.

- **Negative prompt:** D-pad, round game buttons, logos, brand names, readable text, extra ports, changing shape, morphing keys, hands, background clutter, reflections of people, flicker.
- **Label:** "Concept render — not final hardware. Case not printed."

## 4. Packaging reveal

- **Purpose:** an idea of the unboxing for the campaign "What you would get" section. Only use if the owner decides a boxed kit is a real reward. Until then it is exploration.
- **Reference images:** `media/stills/nod-original-orange.png`, `media/stills/nod-mint.png`
- **Framing and aspect:** 16:9, top-down on a table, then a slow lift of the lid.
- **Duration:** 8 s.
- **Style:** plain unbranded kraft-and-cream box with a mint ribbon band, a sun-yellow quick-start card with no readable text, tissue paper. Warm daylight.
- **Prompt:**

> Top-down view on a pale oak table. A small plain cream cardboard box with a mint paper band and no printing. Two hands, seen from the wrist down with five fingers each, lift the lid. Inside, on cream tissue paper, lies the small orange pocket device from the reference image, exactly as shown: a landscape pocket device in a rounded orange case with a small dark screen above four rows of fourteen small black pill-shaped keys under white strips, next to a short white USB-C cable coiled neatly and a plain sun-yellow card with blank lines instead of text. Slow steady camera, soft daylight, calm mood.

- **Negative prompt:** printed text, logos, brand names, barcodes, certification marks, recycling symbols, prices, faces, D-pad, round game buttons, extra devices, clutter.
- **Label:** "Concept render — not final hardware. Packaging not designed."

## 5. Concept silhouettes: Flip and Slide (clearly labelled)

- **Purpose:** show the two form ideas as slow rotating concepts for the "Future directions" section. Keep the claim that they are drawings of ideas, not prototypes.
- **Reference images:** `media/stills/nod-original-orange.png` for the base shape. `media/marketing/out/` social image (it already draws Flip and Slide as labelled concepts).
- **Framing and aspect:** 1:1, two clips (one Flip, one Slide). Locked camera, object animates once.
- **Duration:** 6 s each.
- **Style:** same cream backdrop as the turntable. Matte orange.
- **Prompt (Flip):**

> On a seamless warm cream surface, a small orange pocket device with a hinged screen section. It starts closed, a compact rounded orange block, then the top half swings open on a hinge to reveal four rows of small black pill-shaped keys beneath a small dark screen. One smooth opening, then a pause. Locked-off camera, soft studio light, no hands, no text, no logos.

- **Prompt (Slide):**

> On a seamless warm cream surface, a small orange pocket device with a sliding upper section. It starts as a compact block with a small dark screen, then the upper section slides up smoothly to reveal four rows of small black pill-shaped keys beneath it. One smooth slide, then a pause. Locked-off camera, soft studio light, no hands, no text, no logos.

- **Negative prompt:** logos, readable text, brand names, phone shapes, laptop shapes, D-pad, round buttons, multiple devices, flicker, morphing.
- **Label:** "Concept render — not final hardware. Design idea only." These are not in any reward and not prototyped.

## 6. "Bins out tonight" hands-only replacement scene

- **Purpose:** the one optional shot already described in `docs/NOD-FILMS.md`, kept hands-only so the generated man and his likeness can be dropped. Adds a real-looking hand to the everyday film.
- **Reference images:** `media/stills/nod-original-orange.png`, `site/media/nod-everyday-poster.jpg` (light and grade only)
- **Framing and aspect:** 9:16 vertical, close-up on a hallway table. Slow push-in.
- **Duration:** 8 s.
- **Style:** morning hallway, oak table, cream wall, a mint scarf, a sun-yellow door in soft focus. Generic home, no house numbers.
- **Prompt:**

> Close-up on an oak hallway table in soft morning light in a generic home. A hand in a navy wool coat sleeve, five fingers, picks up the small orange device from the reference image, exactly as shown: a landscape pocket device 84 by 54 millimetres and about 20 millimetres thick, in a rounded orange case. It has a small dark screen left of centre, a white module window on the right, and below them four rows of fourteen small black pill-shaped keys, each row under a white strip of printed letters. The thumb types a few keys, the hand puts the device down and leaves the frame. Shallow depth of field, slow push-in, natural motion, no face, no readable text on the screen, no D-pad, no round game buttons, no logos.

- **Negative prompt:** face, readable text, logos, house numbers, street view, D-pad, round game buttons, fewer than four key rows, extra fingers.
- **Label:** "Concept render — not final hardware. Screen simulated."

---

## After generation

1. Check the "Reject if" list. Regenerate rather than fix in the edit.
2. Add the label and the caption label.
3. Log the prompt, model, date and chosen take in the repo next to the file. Honest provenance matters if Kickstarter reviewers ask.
4. Do not mix concept clips into the real-footage section of the campaign page.
