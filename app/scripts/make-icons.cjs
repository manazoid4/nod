// Renders the placeholder app icon (tomato tile + "N") to build/icon.png, build/tray.png and build/icon.ico.
// Run: npx electron scripts/make-icons.cjs   (the final brand mark replaces build/icon.svg later)
const { app, BrowserWindow } = require('electron');
const fs = require('node:fs');
const path = require('node:path');

const out = path.join(__dirname, '..', 'build');
const svg = fs.readFileSync(path.join(out, 'icon.svg'), 'utf8');

function ico(pngs) {
  const head = Buffer.alloc(6 + 16 * pngs.length);
  head.writeUInt16LE(0, 0);
  head.writeUInt16LE(1, 2);
  head.writeUInt16LE(pngs.length, 4);
  let offset = head.length;
  pngs.forEach(({ size, buf }, i) => {
    const o = 6 + i * 16;
    head[o] = size >= 256 ? 0 : size;
    head[o + 1] = size >= 256 ? 0 : size;
    head.writeUInt16LE(1, o + 4);
    head.writeUInt16LE(32, o + 6);
    head.writeUInt32LE(buf.length, o + 8);
    head.writeUInt32LE(offset, o + 12);
    offset += buf.length;
  });
  return Buffer.concat([head, ...pngs.map((p) => p.buf)]);
}

app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: 256, height: 256, show: false, transparent: true, frame: false, webPreferences: { offscreen: true } });
  await win.loadURL('data:text/html,' + encodeURIComponent(`<body style="margin:0;background:transparent">${svg}</body>`));
  await new Promise((r) => setTimeout(r, 300));
  const img = await win.webContents.capturePage({ x: 0, y: 0, width: 256, height: 256 });
  fs.writeFileSync(path.join(out, 'icon.png'), img.toPNG());
  fs.writeFileSync(path.join(out, 'tray.png'), img.resize({ width: 32, height: 32, quality: 'best' }).toPNG());
  const sizes = [256, 64, 48, 32, 16];
  fs.writeFileSync(path.join(out, 'icon.ico'), ico(sizes.map((size) => ({ size, buf: img.resize({ width: size, height: size, quality: 'best' }).toPNG() }))));
  app.quit();
});
