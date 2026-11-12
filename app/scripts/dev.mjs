// npm run dev        -> Vite + Electron against the real Core (found automatically)
// npm run dev:mock   -> same, but against scripts/mock-core.mjs (no Python or hardware needed)
import { spawn } from 'node:child_process';
import { createServer } from 'vite';
import electron from 'electron';
import { startMock } from './mock-core.mjs';

const env = { ...process.env };
if (process.argv.includes('--mock')) {
  const m = await startMock();
  env.NOD_CORE_DIR = m.dir;
  env.NOD_CORE_PORT = String(m.port);
  console.log(`Using mock Core on port ${m.port}`);
}

await import('./build-main.mjs');
const server = await createServer();
await server.listen();
env.NOD_DEV_URL = 'http://localhost:5173/';
const child = spawn(electron, ['.'], { env, stdio: 'inherit' });
child.on('exit', async () => {
  await server.close();
  process.exit(0);
});
