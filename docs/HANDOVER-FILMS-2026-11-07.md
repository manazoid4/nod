# Nod films handover (7 Nov 2026, paused at owner request: Claude usage at 70%)

**State:** PR #34 (`site/launch-films`, head `4706f8d`) is open and NOT merged. CI is green (Site Quality, nod CI, Vercel preview; MAZ Pocket build passed on the previous commit). Nothing is live yet. The final Sonnet review verdict is **HOLD**, with 5 small fixes below.

Rebuild everything with `bash media/films/render.sh` (needs node, ffmpeg, npx). Code: `media/films/shared/nod.js` and `nod.css`; scene list in `media/films/build.mjs`. Record: `docs/NOD-FILMS.md`. Reviews: `docs/audits/`.

## Fixes before merge (for an outsourced worker; each is local and small)

1. **Simulated screen without a label.** The `hero` and `macro` scenes show "Hold to talk / Save Today PC" with no label. In `nod.js`, add `add(s, "tag-sim", "Screen simulated");` to `S.hero` and `S.macro`, the same as in `S.type`.
2. **Homepage.**
   - `site/index.html` H1 "Ask. Listen. Nod." promises talking. **Owner decided (7 Nov): keep "Ask. Listen. Nod."** Do not change the H1.
   - Change the software card text to "A typed-note feature is in the firmware. Device test pending."
3. **Exploded image alt text** claims snap tabs, vents, a USB-C cut-out and a skirt. Check them against `hardware/case/nod_case.scad` (snaps: `use_snaps`, vents: `use_vents`, frame skirt). Keep the true ones; add "concept" to the alt text.
4. **Overlaps in the `colours` scene.** "Mint." touches the mint case, and the pill sits on the orange case's keys. In `S.colours`, lower the device `top` values by about 60 px, scale `mm` down about 8%, and move `.tag-sim` to `bottom: 200px`.
5. **Small print and end card.**
   - Raise `.honest` and the end-card fine print to at least 36 px at 1080 width. They are 36 px in CSS but read as about 24 px; check them on the render.
   - In `build.mjs`, set the product `end` duration from 3.9 to 2.6.

Then:
1. `bash media/films/render.sh`
2. `node --test site/tests/site.test.mjs`
3. Push, wait for CI, merge PR #34, and verify https://nod-kickstarter.vercel.app/ serves `/media/nod-everyday.mp4`.
4. Update `unified-memory-database/projects/nod/STATUS.md`. A worktree already exists at `C:\Users\Maz\repos\umd-nod-films`, branch `nod/films-2026-11-07`, with no edits yet.

## Optional

One Google Flow shot (a real-looking hand on the device): exact prompt in `docs/NOD-FILMS.md`.

## Cost so far

OpenRouter (DeepSeek) $0.0068. No other paid generation.
