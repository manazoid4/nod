import { _electron as electron } from 'playwright-core';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const app = await electron.launch({ args: [root, `--user-data-dir=${process.argv[2]}`], env: process.env });
try {
  await app.firstWindow();
  await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].show());
  await new Promise((resolve) => app.on('close', resolve));
} finally {
  await app.close().catch(() => {});
}
