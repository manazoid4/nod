/* Piblo films: device renderer + scene builders. One GSAP timeline per film, fully seekable (no clocks, no randomness).
   Device: measured from the official M5Stack Cardputer ADV photos and drawing (media/refs/m5stack-official, hardware/case/DIMENSIONS.md). */
(function () {
  // ---------- Cardputer ADV, measured from the official M5Stack top view (docs.m5stack.com, 7 Nov 2026) ----------
  // Device coordinates in mm: x 0..84 from the Grove (-X) end, y 0..54 from the screen end. Case adds 2 mm a side.
  // Raised screen block y 0..20.5; keyboard deck below it: 4 white legend strips, each over a row of 14 black pill keys.
  const ROWS = [
    ["esc","1","2","3","4","5","6","7","8","9","0","-","=","del"],
    ["tab","q","w","e","r","t","y","u","i","o","p","[","]","\\"],
    ["fn","Aa","a","s","d","f","g","h","j","k","l",";","'","ok"],
    ["ctrl","opt","alt","z","x","c","v","b","n","m",",",".","/","space"],
  ];
  const CHIP = { esc: "#ee6a2c", del: "#141414", tab: "#d9d9d9", fn: "#ee6a2c", Aa: "#2f6db3", ok: "#141414", ctrl: "#d9d9d9", opt: "#35c48f", alt: "#d9d9d9" };
  const ARROW = { ";": "▲", ",": "◀", ".": "▼", "/": "▶" };
  const KX = c => 4.3 + c * 5.78, ROW_Y = r => 21.3 + r * 7.5;
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  // on-device print and the 240x135 screen are shown at true scale: texture, not reading text
  const texture = root => root.querySelectorAll(".lg, .lg *, .ui, .ui *, .mark").forEach(n => n.setAttribute("data-layout-ignore", ""));
  const keyMap = root => Object.fromEntries([...root.querySelectorAll(".key")].map(k => [k.dataset.k, k]));
  const mmv = n => `calc(var(--mm) * ${n})`;
  const box = (cls, x, y, w, h, html) => { const n = el("div", cls, html); Object.assign(n.style, { left: mmv(x), top: mmv(y), width: mmv(w), height: mmv(h) }); return n; };
  const rr = (x, y, w, h, r) => `M${x + r},${y}h${w - 2 * r}a${r},${r} 0 0 1 ${r},${r}v${h - 2 * r}a${r},${r} 0 0 1 -${r},${r}h-${w - 2 * r}a${r},${r} 0 0 1 -${r},-${r}v-${h - 2 * r}a${r},${r} 0 0 1 ${r},-${r}z`;
  const CASE = { "": ["#ee5a36", "#ff8a63", "#c43e1e"], cream: ["#f3e4c8", "#fffaf0", "#cdb791"], mint: ["#8fdcb8", "#c4f0da", "#55a883"] };

  function screenUI(state) {
    const ui = el("div", "ui");
    ui.innerHTML =
      '<div class="bar"><span>piblo</span><span>CONCEPT</span></div>' +
      '<div class="home"><span class="ring"></span><span class="circle"></span><div class="say">Hold to talk</div><div class="chips"><span>Save</span><span>Today</span><span>PC</span></div></div>' +
      '<div class="type" style="opacity:0"><div class="hint">NOTE</div><div class="txt"><span class="t"></span><span class="caret"></span></div></div>' +
      '<div class="saved" style="opacity:0"><span class="tick"></span><div class="t1">Kept for later</div><div class="t2">bins out tonight</div></div>';
    if (state === "saved") { ui.querySelector(".home").style.opacity = 0; ui.querySelector(".saved").style.opacity = 1; }
    return ui;
  }

  // The bare device top face (84 x 54 mm).
  function face(mm, state) {
    const f = el("div", "face"); f.style.setProperty("--mm", mm + "px");
    f.append(box("kbdeck", 0, 20.5, 84, 33.5));
    f.append(box("label", 1.1, 1.3, 17.7, 14.1, "<i></i><i></i><i></i><i></i>"));
    const bez = box("bezel", 20.4, 2.2, 25.4, 15.2), lcd = box("lcd", 1.55, 1.33, 22.3, 12.54), lin = el("div", "lcd-in");
    lin.append(screenUI(state)); lcd.append(lin); bez.append(lcd, el("div", "glare")); f.append(bez);
    f.append(box("screw", 11.9, 15.8, 2.6, 2.6), box("screw", 53.0, 15.8, 2.6, 2.6));
    const stamp = box("stamp", 57.4, 0.9, 26.3, 18.1);
    const dots = ["#e8433a", "#2f6db3", "#35c48f", "#f5c33b", "#1d1d1d", "#e8433a", "#2f6db3", "#1d1d1d"];
    for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) if ((r * 7 + c * 3) % 4) { const ch = box("chip", 1.4 + c * 2.1, 1.4 + r * 3.9, 1.5, 0.9 + (c % 2) * 0.5); ch.style.background = dots[(r + c) % dots.length]; stamp.append(ch); }
    stamp.append(box("btn", 15.6, 6.6, 4.2, 4.2), box("ant", 21.0, 1.2, 4.2, 15.6));
    f.append(stamp);
    ROWS.forEach((row, r) => {
      f.append(box("strip", 1.1, ROW_Y(r), 81.6, 3.0));
      row.forEach((k, c) => {
        const x = KX(c), y = ROW_Y(r);
        const label = k === "space" ? "␣" : k.length === 1 ? k.toUpperCase() : k;
        const lg = box("lg" + (CHIP[k] ? " chip" : ""), x - 2.4, y + 0.35, 4.8, 2.3, ARROW[k] ? `${label}<b>${ARROW[k]}</b>` : label);
        if (CHIP[k]) { lg.style.background = CHIP[k]; lg.style.color = ["#d9d9d9"].includes(CHIP[k]) ? "#222" : "#fff"; }
        const key = box("key", x - 2.0, y + 3.75, 4.0, 2.6); key.dataset.k = k;
        f.append(lg, key);
      });
    });
    texture(f); return f;
  }

  // Stack N flat layers under a top surface to give a part real thickness (CSS 3D, used inside a preserve-3d parent).
  function stack(parent, make, n, stepPx) {
    for (let i = n; i >= 1; i--) { const L = make(i / n); L.style.transform = `translateZ(${-i * stepPx}px)`; parent.append(L); }
  }
  const shade = (hex, k) => { const n = parseInt(hex.slice(1), 16), f = c => Math.round(c * k); return `rgb(${f(n >> 16)},${f((n >> 8) & 255)},${f(n & 255)})`; };
  const svgPart = (mm, d, fill, extra = "") => {
    const s = el("div", "layer"); s.innerHTML = `<svg viewBox="0 0 88 58" width="${88 * mm}" height="${58 * mm}" style="display:block;overflow:visible"><path d="${d}" fill="${fill}" fill-rule="evenodd"/>${extra}</svg>`; return s;
  };
  const FRAME_HOLES = rr(22.7, 4.7, 24.9, 15.5, 1.3) + rr(60.5, 4.5, 21.5, 16.5, 1.3) + rr(2.6, 23.6, 82.8, 32.2, 2) + rr(10.1, 19.8, 1, 1, 0.5);

  // Assembled: device face seen through the printed front frame, with real case thickness below.
  function device(colour, mm, state, opts = {}) {
    const [base, hi, lo] = CASE[colour || ""];
    const d = el("div", "dev3"); d.style.setProperty("--mm", mm + "px");
    Object.assign(d.style, { width: mmv(88), height: mmv(58) });
    const step = mm * 0.5, thick = Math.round(21.6 / 0.5); // 19.6 mm device + 2 mm case
    if (opts.depth !== false) stack(d, k => { const L = box("slab", 0, 0, 88, 58); L.style.background = shade(lo, 0.95 - 0.25 * k); return L; }, Math.min(thick, 30), step * thick / Math.min(thick, 30));
    const top = el("div", "dtop"); Object.assign(top.style, { width: mmv(88), height: mmv(58) });
    const fc = face(mm, state); fc.style.left = mmv(2); fc.style.top = mmv(2); top.append(fc);
    const fr = svgPart(mm, rr(0, 0, 88, 58, 4.5) + FRAME_HOLES, `url(#g-${colour || "o"})`,
      `<defs><linearGradient id="g-${colour || "o"}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${hi}"/><stop offset=".45" stop-color="${base}"/><stop offset="1" stop-color="${lo}"/></linearGradient></defs>` +
      `<path d="${rr(0.3, 0.3, 87.4, 57.4, 4.3)}" fill="none" stroke="rgba(255,255,255,.35)" stroke-width=".35"/>` +
      `<text class="mark" x="6.2" y="14" font-family="Bricolage Grotesque" font-weight="700" font-size="5" fill="${lo}" opacity=".75">piblo</text>`);
    fr.classList.add("frame");
    top.append(fr);
    // shadows the frame edge casts into each window, and the 3.6 mm drop from the screen block to the keyboard deck
    top.append(box("win", 22.7, 4.7, 24.9, 15.5), box("win", 60.5, 4.5, 21.5, 16.5), box("win kbw", 2.6, 23.6, 82.8, 32.2));
    top.append(el("div", "lines"), el("div", "sweep", '<i data-layout-ignore=""></i>'));
    d.append(top);
    texture(d); return d;
  }

  // Exploded parts with real thickness: front frame (plate + skirt), the Cardputer ADV (two-tone), back shell (floor + walls, snaps, vents, port cut-out)
  const sized = (n, mm) => { n.style.setProperty("--mm", mm + "px"); n.style.width = 88 * mm + "px"; n.style.height = 58 * mm + "px"; return n; };
  function framePart(colour, mm) {
    const [base, hi, lo] = CASE[colour || ""], p = sized(el("div", "part3"), mm), step = mm * 0.5;
    const skirt = rr(0, 0, 88, 58, 4.5) + rr(1.2, 1.2, 85.6, 55.6, 3.6);
    stack(p, k => svgPart(mm, skirt, shade(lo, 1 - 0.3 * k)), 10, step);           // 5 mm skirt that slides over the shell
    const top = svgPart(mm, rr(0, 0, 88, 58, 4.5) + FRAME_HOLES, base,
      `<path d="${rr(22.2, 4.2, 25.9, 16.5, 1.6)}" fill="none" stroke="${hi}" stroke-width=".5"/>` +
      `<text class="mark" x="6.2" y="14" font-family="Bricolage Grotesque" font-weight="700" font-size="5" fill="${lo}">piblo</text>`);
    p.append(top); texture(p); return p;
  }
  function bodyPart(mm) {
    const p = sized(el("div", "part3"), mm), step = mm * 0.5;
    stack(p, k => { const L = box("slab", 2, 2, 84, 54); L.style.borderRadius = mmv(2.4); L.style.background = k > 0.25 ? shade("#5a5b5e", 1 - 0.2 * k) : shade("#c9cacc", 1 - 0.3 * k); return L; }, 28, step * 1.4);
    const fc = face(mm); fc.style.left = mmv(2); fc.style.top = mmv(2); p.append(fc); return p;
  }
  function backPart(colour, mm) {
    const [base, hi, lo] = CASE[colour || ""], p = sized(el("div", "part3"), mm), step = mm * 0.5;
    const floor = svgPart(mm, rr(0, 0, 88, 58, 4.5), shade(base, 0.92),
      [0, 1, 2, 3, 4].map(i => `<rect x="${30 + i * 6}" y="22" width="2.2" height="14" rx="1.1" fill="${shade(lo, 0.7)}"/>`).join("") +
      `<text class="mark" x="44" y="47" text-anchor="middle" font-family="Bricolage Grotesque" font-weight="700" font-size="6" fill="${lo}" opacity=".8">piblo</text>`);
    floor.style.transform = `translateZ(${-24 * step}px)`;
    p.append(floor);
    const wall = rr(0, 0, 88, 58, 4.5) + rr(2.4, 2.4, 83.2, 53.2, 3.2);
    const notched = wall + `M86.5,16 h3 v11 h-3 z`; // USB-C / speaker cut-out on the +X end
    stack(p, k => svgPart(mm, k < 0.35 ? notched : wall, shade(lo, 1.02 - 0.3 * k)), 23, step);
    const lip = svgPart(mm, wall, base,
      [[20, 2.4], [62, 2.4], [20, 55], [62, 55]].map(([x, y]) => `<rect x="${x}" y="${y - (y > 30 ? 1.2 : 0)}" width="6" height="1.2" rx=".4" fill="${hi}"/>`).join("") +
      `<rect x="86.5" y="16" width="3" height="11" fill="none"/>`);
    p.append(lip); texture(p); return p;
  }

  // ---------------- scenes ----------------
  // Picture-led: every shot is a lit tabletop or footage, hard cuts, a camera move in every shot, few words.
  const S = {};
  function scene(cls) { const s = el("section", "scene " + (cls || "")); document.getElementById("stage").append(s); return s; }
  // hard cut in and out (the edit is the transition); optional short dip only for the end card
  function cut(tl, s, t, d, o) {
    tl.set(s, { opacity: 1 }, t);
    if (!o.last) tl.set(s, { opacity: 0 }, t + d);
  }
  // one sentence per line, so lines never break mid-phrase
  const lines = t => /<|^[^.]*\.?$/.test(t) ? t : t.split(/(?<=\.) /).map(x => "<span class=\"line\">" + x + "</span>").join("");
  console.assert(lines("Less screen. More life.") === '<span class="line">Less screen.</span><span class="line">More life.</span>', "lines() splits at full stops only");
  const add = (s, cls, html, top) => { const n = el("div", cls, /^(line-|endline|cap)/.test(cls) ? lines(html) : html); if (top != null) n.style.top = top + "px"; s.append(n); return n; };
  function words(tl, n, t) { tl.fromTo(n, { y: 34, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, t); }

  // Tabletop set: warm wall, soft window light, a linen-cream table plane, contact shadow under the product
  function set(s) {
    s.append(el("div", "wall"), el("div", "table"), el("div", "window-light"), el("div", "grain"));
  }
  // Place a device lying on the table, seen from about 35 degrees above
  function onTable(s, node, top, opts = {}) {
    const stage = add(s, "devstage", "", top), tilt = el("div", "devtilt");
    const shadow = el("div", "contact"); tilt.append(shadow, node); stage.append(tilt);
    tilt.style.transform = `rotateX(${opts.rx ?? 52}deg) rotateZ(${opts.rz ?? -14}deg)`;
    return tilt;
  }

  // Opening/closing honesty line, once, large enough to read (36 px)
  const honesty = (s, text, dark) => add(s, "honest" + (dark ? " on-dark" : ""), text);

  // Footage with one left-aligned line in the empty part of the frame
  S.footage = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "scrim-top"));
    (o.captions || []).forEach(c => { const n = add(s, "cap", c.text); words(tl, n, t + c.at); });
    if (o.honest) { const h = honesty(s, o.honest, true); tl.fromTo(h, { opacity: 0 }, { opacity: 1, duration: 0.3 }, t + 0.1); tl.to(h, { opacity: 0, duration: 0.3 }, t + 1.9); }
    cut(tl, s, t, d, o);
  };

  // Typing a note on the device (screen simulated, no "saved" confirmation shown)
  S.type = (tl, t, d, o) => {
    const s = scene(); set(s);
    const dev = device(o.colour || "", 10.6);
    const tilt = onTable(s, dev, 560, { rx: 40, rz: -6 });
    add(s, "tag-sim", "Screen simulated");
    cut(tl, s, t, d, o);
    // camera: slow push towards the screen while typing
    tl.fromTo(tilt, { scale: 1.0, x: 0, y: 40 }, { scale: 2.2, x: 210, y: 330, duration: d * 0.8, ease: "power2.inOut" }, t);
    const ui = dev.querySelector(".ui"), home = ui.querySelector(".home"), type = ui.querySelector(".type"), out = ui.querySelector(".type .t");
    const text = o.text || "bins out tonight", T = t + 0.9, times = [0, .09, .21, .30, .46, .55, .63, .74, .86, .98, 1.07, 1.16, 1.29, 1.37, 1.48, 1.62];
    tl.set(home, { opacity: 0 }, T - 0.25); tl.set(type, { opacity: 1 }, T - 0.25);
    out.innerHTML = [...text].map(ch => `<span style="display:none">${ch === " " ? "&nbsp;" : ch}</span>`).join("");
    const keys = keyMap(dev);
    [...text].forEach((ch, i) => {
      tl.set(out.children[i], { display: "inline" }, T + times[i]);
      const key = keys[ch === " " ? "space" : ch];
      if (key) tl.fromTo(key, { y: 0, filter: "brightness(1)" }, { y: 1.6, filter: "brightness(1.9)", duration: 0.05, yoyo: true, repeat: 1, ease: "power1.out" }, T + times[i]);
    });
    if (o.sleep) { // device goes back to sleep: screen dims, you put it down and get on
      tl.to(dev.querySelector(".lcd"), { filter: "brightness(0.15)", duration: 0.5, ease: "power2.in" }, t + d - 0.9);
    }
  };

  // Hero product shot: orbit on the table, light sweep, one line
  S.hero = (tl, t, d, o) => {
    const s = scene(); set(s);
    const dev = device("", 10.4);
    const tilt = onTable(s, dev, 820);
    add(s, "tag-sim", "Screen simulated");
    if (o.line) { const n = add(s, "line-top", o.line); words(tl, n, t + (o.lineAt ?? 1.2)); }
    if (o.honest) { const h = honesty(s, o.honest); tl.fromTo(h, { opacity: 0 }, { opacity: 1, duration: 0.3 }, t + 0.1); tl.to(h, { opacity: 0, duration: 0.3 }, t + 2.0); }
    cut(tl, s, t, d, o);
    tl.fromTo(tilt, { rotationZ: -22, rotationX: 56, scale: 0.94 }, { rotationZ: -6, rotationX: 46, scale: 1.04, duration: d, ease: "sine.inOut" }, t);
    tl.fromTo(dev.querySelector(".sweep i"), { xPercent: -150 }, { xPercent: 450, duration: 1.8, ease: "power2.inOut" }, t + 0.4);
  };

  // Three proposed cases on the table, staggered in depth, slow lateral move
  S.colours = (tl, t, d, o) => {
    const s = scene(); set(s);
    const spots = [["mint", 460, -150, 5.7], ["cream", 800, 160, 6.3], ["", 1160, -60, 7.0]];
    const tilts = spots.map(([c, top, x, mm]) => { const tt = onTable(s, device(c, mm, null, {}), top, { rx: 52, rz: -16 }); tt.parentNode.style.left = x + "px"; return tt; });
    const n = add(s, "line-top", o.line || "Orange. Cream. Mint.");
    add(s, "tag-sim", "Proposed cases · not printed yet");
    cut(tl, s, t, d, o);
    words(tl, n, t + 0.3);
    tilts.forEach((tt, i) => tl.fromTo(tt.parentNode, { x: 60 - i * 20 }, { x: -60 + i * 20, duration: d, ease: "none" }, t));
  };

  // Macro: the real keyboard and screen, close
  S.macro = (tl, t, d, o) => {
    const s = scene(); set(s);
    const dev = device("", 17);
    const tilt = onTable(s, dev, 720, { rx: 34, rz: -10 });
    add(s, "tag-sim", "Screen simulated");
    if (o.line) { const n = add(s, "line-top", o.line); words(tl, n, t + 0.3); }
    cut(tl, s, t, d, o);
    tl.fromTo(tilt, { x: 200, y: 60 }, { x: -90, y: 0, duration: d, ease: "sine.inOut" }, t);
  };

  // Overlay gate: the bare device face at 10 px/mm, top-left at (120, 600), to compare with the official top view
  S.bare = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "plain"));
    const f = face(10); f.style.left = "120px"; f.style.top = "600px"; s.append(f);
    cut(tl, s, t, d, o);
  };

  // Clean product still (reference image for Google Flow and website posters): no text
  S.still = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "plain"));
    const stage = add(s, "devstage", "", o.top || 640), tilt = el("div", "devtilt"); tilt.append(device(o.colour || "", o.mm || 11, o.state, { depth: o.tilt ? true : false })); stage.append(tilt);
    tilt.style.transform = "rotateX(" + (o.tilt ?? 0) + "deg)";
    cut(tl, s, t, d, o);
  };

  // Exploded build (website image): printed front frame, the Cardputer ADV, printed back shell, each with real thickness
  S.exploded = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "plain"));
    const mm = o.mm || 7.2, parts = [framePart("", mm), bodyPart(mm), backPart("", mm)], tops = o.tops || [330, 780, 1260];
    parts.forEach((p, i) => {
      const stage = add(s, "devstage", "", tops[i]); stage.style.zIndex = 3 - i;
      const iso = el("div", "devtilt"); iso.style.transform = "rotateX(58deg) rotateZ(-34deg)"; iso.append(p); stage.append(iso);
    });
    cut(tl, s, t, d, o);
  };

  // End card
  S.end = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "plain"));
    const logo = add(s, "logo", '<span class="dot"></span><span>piblo</span>', 640);
    const line = add(s, "endline", o.line || "Less screen. More life.", 920);
    const nodes = [line];
    if (o.cta) nodes.push(add(s, "cta", o.cta, 1150));
    nodes.push(add(s, "honest end", "Designed in the UK by Maz Works.<span class=\"line\">Concept film. Prototype in development.</span>", 1480));
    cut(tl, s, t, d, o);
    tl.fromTo(logo, { scale: 0.9, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.6, ease: "expo.out" }, t);
    nodes.forEach((n, i) => words(tl, n, t + 0.35 + i * 0.15));
  };

  window.PibloFilm = {
    device,
    build(id, scenes) {
      const tl = gsap.timeline({ paused: true });
      scenes.forEach(sc => S[sc.type](tl, sc.t, sc.d, sc));
      window.__timelines[id] = tl;
      return tl;
    },
  };
})();
