// Drives the real Electron app (built output) against the mock and saves the Stage 2 screenshots
// to docs/screenshots, at 1280x800 and 900x700.
// Needs `npm run build:main && npm run build:renderer` first. Run: npm run screenshots
import { _electron as electron } from 'playwright-core';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { startMock } from './mock-core.mjs';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'docs', 'screenshots');
fs.mkdirSync(out, { recursive: true });

async function launch(env) {
  const userData = fs.mkdtempSync(path.join(os.tmpdir(), 'piblo-ud-'));
  const app = await electron.launch({ args: [root, `--user-data-dir=${userData}`], env: { ...process.env, ...env } });
  const page = await app.firstWindow();
  await page.waitForLoadState('domcontentloaded');
  return { app, page };
}

async function size(app, page, width, height) {
  await app.evaluate(({ BrowserWindow }, s) => BrowserWindow.getAllWindows()[0].setContentSize(s.width, s.height), { width, height });
  await page.setViewportSize({ width, height }).catch(() => {});
  await page.waitForTimeout(400);
}

const shot = (page, name) => page.screenshot({ path: path.join(out, name + '.png') });

// ---- 1. Onboarding, with Piblo asking to connect ----
{
  const m = await startMock({ port: 18788 });
  const { app, page } = await launch({ NOD_CORE_DIR: m.dir, NOD_CORE_PORT: String(m.port) });
  await page.waitForSelector('.pair-card', { timeout: 30_000 });
  await page.waitForTimeout(1200);
  await size(app, page, 1280, 800);
  await shot(page, '01-onboarding-wants-to-connect-1280');
  await size(app, page, 900, 700);
  await shot(page, '01-onboarding-wants-to-connect-900');

  // Allow: the card goes, then the person opens Live View.
  await size(app, page, 1280, 800);
  await page.getByRole('button', { name: 'Allow' }).click();
  await page.getByRole('button', { name: 'Open Live View' }).click({ timeout: 15_000 });
  await page.waitForSelector('h1:has-text("Live View")', { timeout: 15_000 });
  await page.waitForSelector('img.screen', { timeout: 15_000 });
  await page.waitForTimeout(1500);
  await shot(page, '02-live-view-1280');
  await size(app, page, 900, 700);
  await page.waitForTimeout(1200);
  await shot(page, '02-live-view-900');

  // Every section, at both sizes.
  await size(app, page, 1280, 800);
  for (const [i, name, file] of [
    [1, 'Home', '03-home'],
    [3, 'Ask', '05-ask'],
    [4, 'Memory', '06-memory'],
    [5, 'Actions', '07-actions'],
    [6, 'Settings', '08-settings'],
  ]) {
    await page.keyboard.press(`Control+${i}`);
    await page.waitForSelector(`h1:has-text("${name}")`);
    await page.waitForTimeout(900);
    await shot(page, `${file}-1280`);
    if (name === 'Home' || name === 'Settings') {
      await size(app, page, 900, 700);
      await page.waitForTimeout(600);
      await shot(page, `${file}-900`);
      await size(app, page, 1280, 800);
    }
  }

  // Piblo Dev tabs + Command Palette at 1280x800
  await page.keyboard.press('Control+7');
  await page.waitForSelector('h1:has-text("Piblo Dev")');
  await page.waitForTimeout(800);
  await shot(page, '10-piblo-dev-today-1280');

  for (const [tabName, fileName] of [
    ['Checklists', '11-piblo-dev-checklists-1280'],
    ['Content Studio', '12-piblo-dev-content-1280'],
    ['Agents', '13-piblo-dev-agents-1280'],
    ['Builds', '14-piblo-dev-builds-1280'],
  ]) {
    await page.getByRole('tab', { name: tabName }).click();
    await page.waitForTimeout(600);
    await shot(page, fileName);
  }

  await page.keyboard.press('Control+k');
  await page.waitForSelector('[role="dialog"][aria-label="Jump anywhere"]');
  await page.waitForTimeout(400);
  await shot(page, '15-command-palette-1280');

  await app.close();
  m.close();
}

// ---- 2. Piblo present but unreachable: Live View shows the friendly 503 text ----
{
  const m = await startMock({ port: 18789, deviceOnline: false });
  const fs2 = fs.mkdtempSync(path.join(os.tmpdir(), 'piblo-ud-'));
  fs.writeFileSync(path.join(fs2, 'settings.json'), JSON.stringify({ closeToTray: true, startWithWindows: false, onboardingDone: true }));
  const app = await electron.launch({ args: [root, `--user-data-dir=${fs2}`], env: { ...process.env, NOD_CORE_DIR: m.dir, NOD_CORE_PORT: String(m.port) } });
  const page = await app.firstWindow();
  await page.waitForLoadState('domcontentloaded');
  await page.waitForSelector('h1:has-text("Home")', { timeout: 30_000 });
  await page.keyboard.press('Control+2');
  await page.waitForSelector('h1:has-text("Live View")');
  await page.waitForFunction(() => document.querySelector('.screen-msg')?.textContent?.includes("Piblo isn't reachable"), null, { timeout: 25_000 });
  await size(app, page, 1280, 800);
  await page.waitForTimeout(800);
  await shot(page, '09-live-view-unreachable-1280');
  await app.close();
  m.close();
}

console.log('screenshots saved to', out);
