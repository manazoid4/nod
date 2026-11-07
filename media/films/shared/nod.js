/* Nod films: device renderer + scene builders. One GSAP timeline per film, fully seekable (no clocks, no randomness).
   Device geometry: hardware/case/DIMENSIONS.md (Cardputer ADV 84 x 54 mm, 56 keys, 240 x 135 screen). */
(function () {
  const ROWS = [
    ["`","1","2","3","4","5","6","7","8","9","0","-","=","del"],
    ["tab","q","w","e","r","t","y","u","i","o","p","[","]","\\"],
    ["fn","shift","a","s","d","f","g","h","j","k","l",";","'","ok"],
    ["ctrl","opt","alt","z","x","c","v","b","n","m",",",".","/","space"],
  ];
  const isDark = k => k.length > 1;
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  // on-device print and the 240x135 screen are shown at true scale: texture, not reading text
  const texture = root => root.querySelectorAll(".leg, .mark, .ui, .ui *").forEach(n => n.setAttribute("data-layout-ignore", ""));
  const keyMap = root => Object.fromEntries([...root.querySelectorAll(".key")].map(k => [k.dataset.k, k]));
  const mmv = n => `calc(var(--mm) * ${n})`;

  function keyboard(win) {
    ROWS.forEach((row, r) => row.forEach((k, c) => {
      const x = 0.8 + c * 5.8, y = 1.0 + r * 7.5;
      const leg = el("span", "leg", k === "space" ? "spc" : k);
      leg.style.left = mmv(x); leg.style.top = mmv(y);
      const key = el("i", "key" + (isDark(k) ? " dark" : ""));
      key.dataset.k = k; key.style.left = mmv(x + 0.95); key.style.top = mmv(y + 2.3);
      win.append(leg, key);
    }));
  }

  function screenUI(state) {
    const ui = el("div", "ui");
    ui.innerHTML =
      '<div class="bar"><span>nod</span><span>CONCEPT</span></div>' +
      '<div class="home"><span class="ring"></span><span class="circle"></span><div class="say">Hold to talk</div><div class="chips"><span>Save</span><span>Today</span><span>PC</span></div></div>' +
      '<div class="type" style="opacity:0"><div class="hint">SAVE A THOUGHT</div><div class="txt"><span class="t"></span><span class="caret"></span></div></div>' +
      '<div class="saved" style="opacity:0"><span class="tick"></span><div class="t1">Saved to Notes</div><div class="t2">bins out tonight</div></div>';
    if (state === "saved") { ui.querySelector(".home").style.opacity = 0; ui.querySelector(".saved").style.opacity = 1; }
    return ui;
  }

  // Assembled device in its proposed case. colour: "" (orange) | "cream" | "mint"
  function device(colour, mm, state) {
    const d = el("div", "dev " + (colour || ""));
    d.style.setProperty("--mm", mm + "px");
    const sw = el("div", "win screen-win"), lcd = el("div", "lcd"), lin = el("div", "lcd-in");
    lin.append(screenUI(state)); lcd.append(lin); sw.append(lcd, el("div", "glare"));
    const st = el("div", "win stamp-win", '<i class="btn"></i><i class="led"></i>');
    const kb = el("div", "win kb-win"); keyboard(kb);
    d.append(el("div", "mark", "nod"), el("span", "mic"), sw, st, kb);
    const sweep = el("div", "sweep", "<i data-layout-ignore=\"\"></i>"); d.append(sweep);
    texture(d); return d;
  }

  // Exploded parts: printed front frame (SVG with real window cut-outs), Cardputer ADV body, printed back shell
  function framePart(colour, mm) {
    const fill = { "": "#ee5a36", cream: "#f4e6cc", mint: "#8fdcb8" }[colour || ""];
    const rr = (x, y, w, h, r) => `M${x + r},${y}h${w - 2 * r}a${r},${r} 0 0 1 ${r},${r}v${h - 2 * r}a${r},${r} 0 0 1 -${r},${r}h-${w - 2 * r}a${r},${r} 0 0 1 -${r},-${r}v-${h - 2 * r}a${r},${r} 0 0 1 ${r},-${r}z`;
    const p = rr(0, 0, 88, 58, 4.5) + rr(22.7, 4.7, 24.9, 15.5, 1.3) + rr(60.5, 4.5, 21.5, 16.5, 1.3) + rr(2.6, 23.6, 82.8, 32.2, 2);
    const w = el("div", "part");
    w.innerHTML = `<svg viewBox="0 0 88 58" width="${88 * mm}" height="${58 * mm}" style="display:block;overflow:visible"><path d="${p}" fill="${fill}" fill-rule="evenodd" stroke="rgba(42,26,18,.25)" stroke-width=".25"/><text x="6" y="13" font-family="Bricolage Grotesque" font-weight="700" font-size="5" fill="rgba(42,26,18,.28)" data-layout-ignore="">nod</text></svg>`;
    return w;
  }
  function bodyPart(mm) {
    const d = el("div", "dev"); d.style.setProperty("--mm", mm + "px");
    d.style.setProperty("--case", "#3b3633"); d.style.setProperty("--case-hi", "#55504c"); d.style.setProperty("--case-lo", "#1f1b19");
    d.style.width = mmv(84); d.style.height = mmv(54); d.style.borderRadius = mmv(2.6);
    const sw = el("div", "win screen-win"), lcd = el("div", "lcd"), lin = el("div", "lcd-in");
    sw.style.left = mmv(20.7); sw.style.top = mmv(2.7);
    lin.append(screenUI()); lcd.append(lin); sw.append(lcd, el("div", "glare"));
    const st = el("div", "win stamp-win", '<i class="btn"></i><i class="led"></i>'); st.style.left = mmv(58.5); st.style.top = mmv(2.5);
    const kb = el("div", "win kb-win"); kb.style.left = mmv(0.6); kb.style.top = mmv(21.6); keyboard(kb);
    d.append(sw, st, kb); texture(d); return d;
  }
  function backPart(colour, mm) {
    const d = el("div", "dev " + (colour || "")); d.style.setProperty("--mm", mm + "px"); d.style.setProperty("--edge", mmv(3.2));
    return d;
  }

  // ---------------- scenes ----------------
  const S = {};
  function scene(cls) { const s = el("section", "scene " + (cls || "")); document.getElementById("stage").append(s); return s; }
  function fade(tl, s, t, d, opts) {
    const i = opts.fadeIn ?? 0.35, o = opts.fadeOut ?? 0.35;
    // true cross-fade: fade in over the outgoing scene's fade-out, so no blank frame between scenes
    if (i) tl.fromTo(s, { opacity: 0 }, { opacity: 1, duration: i, ease: "none" }, Math.max(0, t - i)); else tl.set(s, { opacity: 1 }, t);
    if (!opts.last) tl.to(s, { opacity: 0, duration: o || 0.001, ease: "none" }, t + d - (o || 0.001));
  }
  function rise(tl, nodes, t, stagger) { tl.fromTo(nodes, { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: "power3.out", stagger: stagger || 0.12 }, t); }
  function swap(tl, a, b, t) { tl.to(a, { opacity: 0, y: -20, duration: 0.3, ease: "power2.in" }, t); tl.fromTo(b, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, t + 0.25); }
  const add = (s, cls, html, top) => { const n = el("div", cls, cls.startsWith("label") ? "<span>" + html + "</span>" : html); if (top != null) n.style.top = top + "px"; s.append(n); return n; };

  // Footage overlay: captions on top of the static <video> declared in the film's HTML
  S.footage = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "scrim-top"), el("div", "scrim-bottom"));
    const caps = (o.captions || []).map(c => add(s, "cap", c.text));
    caps.forEach((c, i) => { const ct = o.captions[i]; if (i === 0) rise(tl, c, t + ct.at); else swap(tl, caps[i - 1], c, t + ct.at); });
    add(s, "label on-dark", o.label || "Concept film · generated scene");
    fade(tl, s, t, d, o);
  };

  // Typing a thought into Nod and saving it (simulated screen)
  S.save = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"), el("div", "grain"));
    const h1 = add(s, "headline", "Tell nod.", 300), h2 = add(s, "headline", "Then let it go.", 300);
    h2.style.opacity = 0;
    const stage = add(s, "devstage", "", 760), tilt = el("div", "devtilt"), dev = device("", 10.4);
    tilt.append(dev); stage.append(tilt);
    add(s, "label", "Concept render · screen simulated · case not yet printed");
    fade(tl, s, t, d, o);
    rise(tl, h1, t + 0.25);
    tl.fromTo(tilt, { rotationX: 34, y: 160, opacity: 0 }, { rotationX: 16, y: 0, opacity: 1, duration: 1.0, ease: "power3.out" }, t + 0.1);
    const ui = dev.querySelector(".ui"), home = ui.querySelector(".home"), type = ui.querySelector(".type"), saved = ui.querySelector(".saved"), out = ui.querySelector(".type .t");
    const text = "bins out tonight", T = t + 1.2, times = [0, .09, .21, .30, .46, .55, .63, .74, .86, .98, 1.07, 1.16, 1.29, 1.37, 1.48, 1.62];
    tl.to(home, { opacity: 0, duration: 0.15 }, T - 0.2); tl.to(type, { opacity: 1, duration: 0.15 }, T - 0.15);
    out.innerHTML = [...text].map(ch => `<span style="display:none">${ch === " " ? "&nbsp;" : ch}</span>`).join("");
    const spans = out.children;
    const keys = keyMap(dev);
    [...text].forEach((ch, i) => {
      tl.set(spans[i], { display: "inline" }, T + times[i]);
      const key = keys[ch === " " ? "space" : ch];
      if (key) tl.fromTo(key, { y: 0, filter: "brightness(1)" }, { y: 2.5, filter: "brightness(.82)", duration: 0.05, yoyo: true, repeat: 1, ease: "power1.out" }, T + times[i]);
    });
    const okKey = keys.ok;
    tl.fromTo(okKey, { y: 0 }, { y: 2.5, duration: 0.06, yoyo: true, repeat: 1 }, T + 1.85);
    tl.to(type, { opacity: 0, duration: 0.15 }, T + 1.9); tl.to(saved, { opacity: 1, duration: 0.2 }, T + 1.95);
    tl.fromTo(saved.querySelector(".tick"), { scale: 0.4 }, { scale: 1, duration: 0.45, ease: "back.out(2.2)" }, T + 1.95);
    swap(tl, h1, h2, T + 2.2);
    // camera: push into the 240x135 screen so the typing reads on a phone, pull back once saved
    tl.to(tilt, { scale: 2.3, x: 212, y: 330, duration: 0.8, ease: "power2.inOut" }, T - 0.55);
    tl.to(tilt, { scale: 1.04, x: 0, y: 0, duration: 0.8, ease: "power2.inOut" }, T + 2.35);
  };

  // Hero: the orange Nod, slow turn with a soft light sweep
  S.hero = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"), el("div", "grain"));
    const h = add(s, "headline", o.title || "Meet nod.", 330), sub = add(s, "sub", o.sub || "A small helper for everyday things.", 470);
    const stage = add(s, "devstage", "", 760), tilt = el("div", "devtilt"), dev = device("", 10.4, o.state);
    tilt.append(dev); stage.append(tilt);
    add(s, "label", "Concept render · proposed printed case");
    fade(tl, s, t, d, o);
    const first = o.fadeIn === 0;
    tl.fromTo(tilt, { rotationX: first ? 24 : 38, rotationZ: first ? -5 : -9, y: first ? 30 : 90, opacity: first ? 1 : 0 }, { rotationX: 14, rotationZ: -2, y: 0, opacity: 1, duration: 1.4, ease: "power3.out" }, t);
    tl.to(tilt, { rotationZ: 1.5, rotationX: 10, duration: d - 1.4, ease: "sine.inOut" }, t + 1.4);
    tl.fromTo(dev.querySelector(".sweep i"), { xPercent: -150 }, { xPercent: 450, duration: 1.6, ease: "power2.inOut" }, t + 1.0);
    if (!first) rise(tl, [h, sub], t + 0.35, 0.15);
  };

  // Three colourways, identical geometry
  S.colours = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"), el("div", "grain"));
    const h = add(s, "headline", "Three colours.<span class=\"line\">One shape.</span>", 230);
    const items = [["", "Nod Original", "Orange"], ["cream", "Nod Classic", "Cream"], ["mint", "Nod Mint", "Mint"]];
    const nodes = items.map(([c, name, sub], i) => {
      const stage = add(s, "devstage", "", 520 + i * 365); stage.style.justifyContent = "flex-start"; stage.style.paddingLeft = "70px";
      const tilt = el("div", "devtilt"); tilt.append(device(c, 6.3)); stage.append(tilt);
      const n = add(s, "cname", `${name}<small>${sub}</small>`, 600 + i * 365); n.style.left = "690px";
      return [tilt, n];
    });
    add(s, "label", "Proposed printed cases · not yet fit-tested");
    fade(tl, s, t, d, o);
    rise(tl, h, t - 0.15);
    nodes.forEach(([tilt, n], i) => {
      tl.fromTo(tilt, { x: -700, rotationZ: -10, rotationX: 20 }, { x: 0, rotationZ: -4, rotationX: 12, duration: 0.9, ease: "power4.out" }, t + 0.35 + i * 0.22);
      tl.fromTo(n, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, t + 0.75 + i * 0.22);
    });
  };

  // Clean product still (reference image for Google Flow and website posters): no text
  S.still = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"));
    const stage = add(s, "devstage", "", o.top || 640), tilt = el("div", "devtilt"); tilt.append(device(o.colour || "", o.mm || 11, o.state)); stage.append(tilt);
    tilt.style.transform = "rotateX(" + (o.tilt ?? 0) + "deg)";
    fade(tl, s, t, d, { fadeIn: 0, fadeOut: 0, last: o.last });
  };

  // Exploded build: printed front, real Cardputer ADV, printed back
  S.exploded = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"), el("div", "grain"));
    const h = add(s, "headline", "What makes a nod.", 210);
    const mm = 5.4, layers = [
      [framePart("", mm), "Printed case front", "Prints at home. Concept, not yet fit-tested."],
      [bodyPart(mm), "Cardputer ADV", "Real, off-the-shelf hardware by M5Stack."],
      [backPart("", mm), "Printed case back", "Same shape in orange, cream or mint."],
    ];
    const rest = [800, 850, 900], open = [470, 860, 1250];
    const parts = layers.map(([node, title, note], i) => {
      const wrap = add(s, "devstage", "", rest[i]); wrap.style.zIndex = 3 - i; wrap.style.justifyContent = "flex-start"; wrap.style.paddingLeft = "70px";
      const iso = el("div", "devtilt"); iso.style.transform = "rotateX(56deg) rotateZ(-32deg)"; iso.append(node); wrap.append(iso);
      const lab = add(s, "cname", `${title}<small>${note}</small>`, open[i] + 70); lab.style.left = "640px"; lab.style.right = "50px"; lab.style.fontSize = "42px";
      return [wrap, lab, i];
    });
    const pill = add(s, "pill", "<span>+ free, open-source Nod software</span>", 1580);
    add(s, "label", "Exploded concept render");
    if (o.bare) { // clean image for the website: parts only, centred
      [h, pill, ...s.querySelectorAll(".cname, .label")].forEach(n => n.remove());
      parts.forEach(([wrap]) => { wrap.style.justifyContent = "center"; wrap.style.paddingLeft = "0"; });
    }
    fade(tl, s, t, d, o);
    rise(tl, h, t - 0.15);
    parts.forEach(([wrap, lab, i]) => {
      tl.fromTo(wrap, { y: 0 }, { y: open[i] - rest[i], duration: 1.1, ease: "power3.inOut" }, t + 0.7);
      tl.fromTo(lab, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, t + 1.1 + i * 0.15);
    });
    tl.fromTo(pill, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, t + 1.7);
  };

  // Real size
  S.size = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"), el("div", "grain"));
    const h = add(s, "headline", "Pocket-sized.<span class=\"line\">Real keys.</span>", 300);
    const sub = add(s, "sub", "A small screen you don't scroll.", 560);
    const mm = 8.4, stage = add(s, "devstage", "", 900), tilt = el("div", "devtilt"); tilt.append(device("mint", mm, "saved")); stage.append(tilt);
    const w = 88 * mm, left = (1080 - w) / 2;
    const dx = add(s, "dim", '<span style="left:50%;top:-56px;transform:translateX(-50%)">84 mm</span>', 860); Object.assign(dx.style, { left: left + "px", width: w + "px", borderTopWidth: "3px" });
    const dy = add(s, "dim", '<span style="left:22px;top:50%;transform:translateY(-50%)">54 mm</span>', 900); Object.assign(dy.style, { left: (left + w + 34) + "px", height: (58 * mm) + "px", borderLeftWidth: "3px" });
    add(s, "label", "Real device size");
    fade(tl, s, t, d, o);
    rise(tl, [h, sub], t + 0.2);
    tl.fromTo(tilt, { scale: 0.9, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.9, ease: "power3.out" }, t + 0.1);
    tl.fromTo([dx, dy], { opacity: 0 }, { opacity: 1, duration: 0.5 }, t + 0.9);
  };

  // Everyday uses: the intended simplicity (in development)
  S.uses = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"), el("div", "grain"));
    const lines = ["Remember the thing.", "Catch the idea.", "Ask a quick question.", "Put the phone down."];
    const box = add(s, "uses");
    lines.forEach((txt, i) => {
      const u = el("div", "u", txt); u.style.top = (i * 250) + "px"; u.style.color = ["#2a1a12", "#b3301a", "#0d6e4f", "#2a1a12"][i]; box.append(u);
      tl.fromTo(u, { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, t + 0.15 + i * 0.42);
    });
    add(s, "label", "What we are building towards · in development");
    fade(tl, s, t, d, o);
  };

  // Vision line
  S.vision = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"), el("div", "grain"));
    const h = add(s, "headline", "Starting small.<span class=\"line\">Getting better</span><span class=\"line\">together.</span>", 640);
    const dots = add(s, "dots", '<i style="background:#ee5a36"></i><i style="background:#f4e6cc"></i><i style="background:#8fdcb8"></i>', 1120);
    add(s, "label", "Built in the open with early supporters");
    fade(tl, s, t, d, o);
    rise(tl, h, t - 0.15);
    tl.fromTo(dots.children, { scale: 0 }, { scale: 1, duration: 0.5, ease: "back.out(2)", stagger: 0.12 }, t + 0.8);
  };

  // End card
  S.end = (tl, t, d, o) => {
    const s = scene(); s.append(el("div", "paper-bg"), el("div", "grain"));
    const logo = add(s, "logo", '<span class="dot"></span><span>nod</span>', 600);
    const line = add(s, "headline", o.line || "Less screen. More life.", 900); line.style.fontSize = "84px";
    const nodes = [logo, line];
    if (o.cta) { const p = add(s, "pill", `<span>${o.cta}</span>`, 1130); nodes.push(p); }
    const f = add(s, "fine", "Designed in the UK by Maz Works<span class=\"line\">Prototype in development</span>", 1520);
    nodes.push(f);
    fade(tl, s, t, d, o);
    tl.fromTo(logo, { scale: 0.85, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.7, ease: "back.out(1.8)" }, t - 0.1);
    rise(tl, nodes.slice(1), t + 0.4, 0.15);
  };

  window.NodFilm = {
    device,
    build(id, scenes) {
      const tl = gsap.timeline({ paused: true });
      scenes.forEach(sc => S[sc.type](tl, sc.t, sc.d, sc));
      window.__timelines[id] = tl;
      return tl;
    },
  };
})();
