// Generates the three HyperFrames projects (product, everyday, launch) from one scene list each.
// Usage: node media/films/build.mjs   then   bash media/films/render.sh
import { mkdirSync, writeFileSync, cpSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const SHOT_A = "assets/shotA-hallway.mp4"; // generated Google Flow footage, 2.08 s, graded and upscaled from 720p

// Scenes are listed with durations only; start times, footage clips and sound cues are derived.
// Hard cuts (no dissolves). Sound sits on beats: the key clicks and one soft note on the end card.
const SRC_LEN = 2.06;
const OPEN = { type: "footage", d: 3.2, captions: [{ at: 0.9, text: "Bins out tonight." }], honest: "Concept film. Generated scene." };
function film(list) {
  let t = 0, n = 0; const scenes = [], videos = [], sfx = [];
  list.forEach((sc, i) => {
    const s = { ...sc, t: +t.toFixed(2) };
    if (i === list.length - 1) s.last = true;
    if (s.type === "footage") videos.push({ id: "hall" + ++n, start: +t.toFixed(2), dur: s.d, rate: +Math.min(1, SRC_LEN / s.d).toFixed(3), mediaStart: 0, zoom: 1 });
    if (s.type === "type") sfx.push(["typing", t + 0.9, 0.5]);
    if (s.type === "end") sfx.push(["chime", t + 0.1, 0.4]);
    scenes.push(s); t += s.d;
  });
  return { duration: +t.toFixed(2), scenes, videos, sfx };
}

const films = {
  everyday: film([
    OPEN,
    { type: "type", d: 5.0, sleep: true },
    { type: "end", d: 3.9, line: "One less thing on your mind." },
  ]),
  product: film([
    { type: "hero", d: 4.2, line: "Less screen.", lineAt: 1.6, honest: "Concept render. Proposed printed case." },
    { type: "macro", d: 3.2, line: "Real keys. Small screen." },
    { type: "colours", d: 3.4 },
    { type: "end", d: 2.6, line: "Less screen. More life." },
  ]),
  stills: film([
    { type: "still", d: 1, colour: "", tilt: 0 },
    { type: "still", d: 1, colour: "cream", tilt: 0 },
    { type: "still", d: 1, colour: "mint", tilt: 0 },
    { type: "still", d: 1, colour: "", tilt: 30 },
    { type: "exploded", d: 3 },
    { type: "bare", d: 1 },
  ]),
  launch: film([
    OPEN,
    { type: "type", d: 4.6, sleep: true },
    { type: "hero", d: 3.6, line: "Less screen. More life.", lineAt: 0.8 },
    { type: "colours", d: 3.0 },
    { type: "macro", d: 2.6, line: "Real keys. Small screen." },
    { type: "end", d: 4.2, line: "One less thing on your mind.", cta: "Follow the build · piblo.co.uk" },
  ]),
};

const page = (name, f) => `<!doctype html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920">
<title>Piblo · ${name}</title>
<link rel="stylesheet" href="assets/piblo.css">
<script src="assets/gsap.min.js"></script>
<script src="assets/piblo.js"></script>
</head>
<body>
<div id="root" data-composition-id="piblo-${name}" data-start="0" data-width="1080" data-height="1920" data-duration="${f.duration}">
${f.videos.map(v => `  <div class="vwrap" id="${v.id}-wrap"${v.zoom !== 1 ? ` style="transform:scale(${v.zoom});transform-origin:50% 30%"` : ""}><video id="${v.id}" src="${SHOT_A}" data-start="${v.start}" data-duration="${v.dur}" data-media-start="${v.mediaStart}" data-playback-rate="${v.rate}" data-has-audio="true" data-volume="2.5" playsinline></video></div>`).join("\n")}
  <div id="stage"></div>
  <audio id="room" src="assets/room.wav" data-start="0" data-duration="${f.duration}" data-volume="0.6"></audio>
${f.sfx.map(([s, t, vol], i) => `  <audio id="sfx-${s}-${i}" src="assets/${s}.wav" data-start="${t.toFixed(2)}" data-volume="${vol ?? (s === "typing" ? 0.45 : 1)}"></audio>`).join("\n")}
</div>
<script>
PibloFilm.build("piblo-${name}", ${JSON.stringify(f.scenes)});
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
