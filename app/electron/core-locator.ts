// Finds where Nod Core lives on this PC and discovers its token. Pure functions with injected fs,
// so they are unit-testable. The app is local and trusted: it reads the token from Core's own .env,
// so the owner never has to copy it by hand.
import path from 'node:path';

export interface FsLike {
  exists(p: string): boolean;
  read(p: string): string | null;
}

export const DEFAULT_PORT = 8787;

export function parseEnv(text: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq < 1) continue;
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) val = val.slice(1, -1);
    out[key] = val;
  }
  return out;
}

const PLACEHOLDER_TOKEN = 'change-me-before-first-run';

/** Returns the usable token from a .env text, or '' when missing/placeholder. */
export function tokenFromEnv(text: string | null): string {
  if (!text) return '';
  const t = parseEnv(text).MAZ_TOKEN ?? '';
  return t && t !== PLACEHOLDER_TOKEN ? t : '';
}

export interface LocateInput {
  env: Record<string, string | undefined>;
  resourcesPath: string; // process.resourcesPath when packaged
  devHostDir: string; // repo host/ folder for `npm run dev`
  fs: FsLike;
}

export interface CoreLocation {
  installDir: string;
  /** Directory containing the mazhost package to run (install dir, bundled copy, or repo host/). */
  sourceDir: string | null;
  python: string | null;
  envFile: string | null;
  bundledDir: string | null;
}

export function locateCore({ env, resourcesPath, devHostDir, fs }: LocateInput): CoreLocation {
  // Piblo Core lives in %LOCALAPPDATA%\Piblo\Core (run by the "Piblo Core" logon task). Never the MazRouter "MAZ Core" folder.
  const installDir = env.PIBLO_CORE_DIR || env.NOD_CORE_DIR || path.join(env.LOCALAPPDATA || '', 'Piblo', 'Core');
  const bundled = [path.join(resourcesPath, 'core'), devHostDir].find((d) => d && fs.exists(path.join(d, 'mazhost', '__main__.py'))) ?? null;
  const sourceDir = fs.exists(path.join(installDir, 'mazhost', '__main__.py')) ? installDir : bundled;
  const python =
    [path.join(installDir, '.venv', 'Scripts', 'pythonw.exe'), path.join(installDir, '.venv', 'Scripts', 'python.exe')].find((p) => fs.exists(p)) ?? null;
  const envPath = path.join(installDir, '.env');
  return { installDir, sourceDir, python, envFile: fs.exists(envPath) ? envPath : null, bundledDir: bundled };
}

/**
 * Which files of the bundled Core may be copied into the install dir.
 * User state (root `data/`, logs, .env, .venv) is never overwritten, but seed data shipped
 * inside the package (`mazhost/data/...`) must be copied or Core 500s on /features and /templates.
 */
export function isCoreCopyable(relativePath: string): boolean {
  const parts = relativePath.split(/[\\/]+/).filter((p) => p && p !== '.');
  if (parts.length === 0) return true;
  const name = parts[parts.length - 1];
  if (name === '.env') return false;
  if (parts.length === 1 && name === 'data') return false; // root holds live user data
  // Cruft and virtualenvs are skipped at any depth.
  return !parts.some((p) => ['.venv', '__pycache__', 'logs', 'tests'].includes(p));
}

export function discoverToken(loc: CoreLocation, fs: FsLike, env: Record<string, string | undefined> = {}): string {
  if (env.NOD_TOKEN) return env.NOD_TOKEN;
  return loc.envFile ? tokenFromEnv(fs.read(loc.envFile)) : '';
}

export function discoverPort(loc: CoreLocation, fs: FsLike, env: Record<string, string | undefined> = {}): number {
  const fromEnv = Number(env.NOD_CORE_PORT);
  if (fromEnv > 0) return fromEnv;
  const p = loc.envFile ? Number(parseEnv(fs.read(loc.envFile) ?? '').MAZ_PORT) : 0;
  return p > 0 && p < 65536 ? p : DEFAULT_PORT;
}
