import { describe, expect, it } from 'vitest';
import { discoverPort, discoverToken, locateCore, parseEnv, tokenFromEnv, type FsLike } from '../electron/core-locator';

const mkFs = (files: Record<string, string>): FsLike => ({
  exists: (p) => p in files,
  read: (p) => files[p] ?? null,
});
const sep = (p: string) => p.replace(/\//g, '\\');

describe('token discovery', () => {
  it('parses .env and ignores comments, blanks and quotes', () => {
    expect(parseEnv('# c\n\nMAZ_TOKEN="abc123"\r\nMAZ_PORT=9000\nbad line\n')).toEqual({ MAZ_TOKEN: 'abc123', MAZ_PORT: '9000' });
  });
  it('rejects the placeholder token and missing files', () => {
    expect(tokenFromEnv('MAZ_TOKEN=change-me-before-first-run')).toBe('');
    expect(tokenFromEnv(null)).toBe('');
    expect(tokenFromEnv('MAZ_TOKEN=real-token')).toBe('real-token');
  });
  it('finds the token in the install dir .env without any manual copy', () => {
    const env = { LOCALAPPDATA: 'C:\\Users\\u\\AppData\\Local' };
    const dir = 'C:\\Users\\u\\AppData\\Local\\MAZ Core';
    const fs = mkFs({ [`${dir}\\.env`]: 'MAZ_TOKEN=tok-1\nMAZ_PORT=8800' });
    const loc = locateCore({ env, resourcesPath: 'R', devHostDir: 'D', fs });
    expect(loc.installDir).toBe(dir);
    expect(discoverToken(loc, fs)).toBe('tok-1');
    expect(discoverPort(loc, fs)).toBe(8800);
  });
  it('NOD_TOKEN, NOD_CORE_PORT and NOD_CORE_DIR override discovery', () => {
    const fs = mkFs({});
    const loc = locateCore({ env: { NOD_CORE_DIR: 'X' }, resourcesPath: 'R', devHostDir: 'D', fs });
    expect(loc.installDir).toBe('X');
    expect(discoverToken(loc, fs, { NOD_TOKEN: 'abc' })).toBe('abc');
    expect(discoverPort(loc, fs, { NOD_CORE_PORT: '9911' })).toBe(9911);
    expect(discoverPort(loc, fs)).toBe(8787);
  });
});

describe('locateCore', () => {
  it('reports no python and falls back to bundled source when Core is not installed', () => {
    const bundled = sep('R/core/mazhost/__main__.py');
    const fs = mkFs({ [bundled]: '' });
    const loc = locateCore({ env: { LOCALAPPDATA: 'L' }, resourcesPath: 'R', devHostDir: 'D', fs });
    expect(loc.python).toBeNull();
    expect(loc.sourceDir).toBe(sep('R/core'));
    expect(loc.envFile).toBeNull();
  });
  it('prefers the installed copy and pythonw', () => {
    const d = sep('L/MAZ Core');
    const fs = mkFs({ [`${d}\\mazhost\\__main__.py`]: '', [`${d}\\.venv\\Scripts\\pythonw.exe`]: '', [`${d}\\.venv\\Scripts\\python.exe`]: '', [`${d}\\.env`]: 'MAZ_TOKEN=t' });
    const loc = locateCore({ env: { LOCALAPPDATA: 'L' }, resourcesPath: 'R', devHostDir: 'D', fs });
    expect(loc.sourceDir).toBe(d);
    expect(loc.python).toBe(`${d}\\.venv\\Scripts\\pythonw.exe`);
    expect(loc.envFile).toBe(`${d}\\.env`);
  });
});
