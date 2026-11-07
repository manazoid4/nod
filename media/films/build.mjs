// Generates the three HyperFrames projects (product, everyday, launch) from one scene list each.
// Usage: node media/films/build.mjs   then   bash media/films/render.sh
import { mkdirSync, writeFileSync, cpSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const SHOT_A = "assets/shotA-hallway.mp4"; // generated Google Flow footage, 2.08 s, graded and upscaled from 720p

// Scenes are listed with durations only; start times, footage clips and sound cues are derived.
// Footage (one 2.08 s generated shot) overlaps 0.35 s into neighbours so cross-fades never show an empty frame.
const SRC_LEN = 2.06, XF = 0.35;
const CAP_OPEN = [{ at: 0.15, text: "Wait. What was I meant to remember?" }];
const CAP_BACK = [{ at: 0.1, text: "Out the door. Nothing nagging." }];
function film(list) {
  let t = 0, n = 0; const scenes = [], videos = [], sfx = [];
  list.forEach((sc, i) => {
    const s = { ...sc, t: +t.toFixed(2) };
    if (i === 0) s.fadeIn = 0;
    if (i === list.length - 1) s.last = true;
    if (s.type === "footage") {
      const start = i === 0 ? 0 : t - XF, dur = s.d + (i === 0 ? XF : 2 * XF);
      videos.push({ id: "hall" + ++n, start: +start.toFixed(2), dur: +dur.toFixed(2), rate: +Math.min(1, SRC_LEN / dur).toFixed(3), mediaStart: 0, zoom: n > 1 ? 1.14 : 1 });
    }
    if (s.type === "save") sfx.push(["typing", t + 1.2], ["chime", t + 3.15]);
    if (s.type === "end") sfx.push(["chime", t + 0.2, 0.55]);
    scenes.push(s); t += s.d;
  });
  return { duration: +t.toFixed(2), scenes, videos, sfx };
}

const films = {
  everyday: film([
    { type: "footage", d: 2.9, captions: CAP_OPEN },
    { type: "save", d: 5.4 },
    { type: "footage", d: 2.2, captions: CAP_BACK },
    { type: "end", d: 4.4, line: "One less thing on your mind." },
  ]),
  product: film([
    { type: "hero", d: 3.2 },
    { type: "exploded", d: 5.0 },
    { type: "colours", d: 3.4 },
    { type: "size", d: 2.8 },
    { type: "end", d: 4.2, line: "Less screen. More life." },
  ]),
  stills: film([
    { type: "still", d: 1, colour: "", tilt: 0 },
    { type: "still", d: 1, colour: "cream", tilt: 0 },
    { type: "still", d: 1, colour: "mint", tilt: 0 },
    { type: "still", d: 1, colour: "", tilt: 22, state: "saved" },
    { type: "exploded", d: 3, bare: true },
  ]),
  launch: film([
    { type: "footage", d: 2.9, captions: CAP_OPEN },
    { type: "uses", d: 3.2 },
    { type: "save", d: 5.4 },
    { type: "footage", d: 2.2, captions: CAP_BACK },
    { type: "hero", d: 2.6, title: "Meet nod.", sub: "Less screen. More life." },
    { type: "colours", d: 3.4 },
    { type: "vision", d: 2.4 },
    { type: "end", d: 4.4, line: "One less thing on your mind.", cta: "Follow the build · nod-kickstarter.vercel.app" },
  ]),
};

const page = (name, f) => `<!doctype html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920">
<title>Nod · ${name}</title>
<link rel="stylesheet" href="assets/nod.css">
<script src="assets/gsap.min.js"></script>
<script src="assets/nod.js"></script>
</head>
<body>
<div id="root" data-composition-id="nod-${name}" data-start="0" data-width="1080" data-height="1920" data-duration="${f.duration}">
${f.videos.map(v => `  <div class="vwrap" id="${v.id}-wrap"${v.zoom !== 1 ? ` style="transform:scale(${v.zoom});transform-origin:50% 30%"` : ""}><video id="${v.id}" src="${SHOT_A}" data-start="${v.start}" data-duration="${v.dur}" data-media-start="${v.mediaStart}" data-playback-rate="${v.rate}" data-has-audio="true" data-volume="2.5" playsinline></video></div>`).join("\n")}
  <div id="stage"></div>
  <audio id="room" src="assets/room.wav" data-start="0" data-duration="${f.duration}" data-volume="0.6"></audio>
${f.sfx.map(([s, t, vol], i) => `  <audio id="sfx-${s}-${i}" src="assets/${s}.wav" data-start="${t.toFixed(2)}" data-volume="${vol ?? (s === "typing" ? 0.45 : 1)}"></audio>`).join("\n")}
</div>
<script>
NodFilm.build("nod-${name}", ${JSON.stringify(f.scenes)});
</script>
</body>
</html>
`;

for (const [name, f] of Object.entries(films)) {
  const dir = join(here, name), assets = join(dir, "assets");
  mkdirSync(assets, { recursive: true });
  cpSync(join(here, "shared"), assets, { recursive: true, filter: s => !s.endsWith(".sh") });
  cpSync(join(here, "..", "source", "shotA-hallway.mp4"), join(assets, "shotA-hallway.mp4"));
  writeFileSync(join(dir, "index.html"), page(name, f));
  console.log("wrote", name, readdirSync(assets).length, "assets");
}
