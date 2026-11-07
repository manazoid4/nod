// Drives the real Electron app (built output) with the mock Core and saves 1280x800 screenshots to docs/screenshots.
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
  const userData = fs.mkdtempSync(path.join(os.tmpdir(), 'nod-ud-'));
  const app = await electron.launch({ args: [root, `--user-data-dir=${userData}`], env: { ...process.env, ...env } });
  const page = await app.firstWindow();
  await app.evaluate(({ BrowserWindow, nativeTheme }) => {
    nativeTheme.themeSource = 'light';
    BrowserWindow.getAllWindows()[0].setContentSize(1280, 800);
  });
  await page.waitForLoadState('domcontentloaded');
  await page.setViewportSize({ width: 1280, height: 800 }).catch(() => {});
  return { app, page };
}
const shot = (page, name) => page.screenshot({ path: path.join(out, name + '.png') });

// 1. Core not installed (no mock, empty Core dir): the clean "Not connected" state
{
  const empty = fs.mkdtempSync(path.join(os.tmpdir(), 'nod-empty-'));
  const { app, page } = await launch({ NOD_CORE_DIR: empty, NOD_CORE_PORT: '18999' });
  await page.getByText('Skip for now').click();
  await page.waitForSelector('.gate h1:not(:has-text("Looking"))', { timeout: 20000 });
  await shot(page, '00-core-not-installed');
  await app.close();
}

// 2. Onboarding with the device offline, then online
{
  const m = await startMock({ port: 18788, deviceOnline: false });
  const { app, page } = await launch({ NOD_CORE_DIR: m.dir, NOD_CORE_PORT: String(m.port) });
  await page.waitForSelector('.step');
  await shot(page, '01-onboarding-connect-offline');
  await app.close();
  m.close();
}
{
  const m = await startMock({ port: 18789 });
  const { app, page } = await launch({ NOD_CORE_DIR: m.dir, NOD_CORE_PORT: String(m.port) });
  await page.waitForSelector('.step.active');
  await shot(page, '02-onboarding-first-action');
  await page.getByRole('button', { name: /Send "Hello"/ }).click();
  await page.waitForSelector('.step.done >> text=See the result', { timeout: 8000 });
  await shot(page, '03-onboarding-result');
  await page.getByRole('button', { name: 'Open Nod Core' }).click();
  await page.waitForTimeout(3600);

  // 3. Every section
  for (const [i, name, file] of [[1, 'My Nod', '10-my-nod'], [2, 'Ask', '11-ask'], [3, 'Memory', '12-memory'], [4, 'Actions', '13-actions'], [5, 'Settings', '14-settings']]) {
    await page.keyboard.press(`Control+${i}`);
    await page.waitForSelector(`h1:has-text("${name}")`);
    if (name === 'Ask') {
      await page.getByLabel('Message').fill('What should I focus on today?');
      await page.getByRole('button', { name: 'Send' }).click();
      await page.waitForSelector('.bubble:not(.me)');
    }
    await page.waitForTimeout(1500);
    await shot(page, file);
  }
  await app.close();
  m.close();
}
console.log('screenshots saved to', out);
