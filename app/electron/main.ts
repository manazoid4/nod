import { app, BrowserWindow, Menu, Tray, ipcMain, nativeImage, nativeTheme, shell } from 'electron';
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import type { AppSettings, EnvKey } from '../shared/types';
import { createApiClient } from './api-client';
import { discoverPort, discoverToken, locateCore, type FsLike } from './core-locator';
import { applyEnvEdit, validateEnvEdit, viewEnv } from './env-file';
import { CoreSidecar } from './sidecar';

const realFs: FsLike = {
  exists: (p) => fs.existsSync(p),
  read: (p) => {
    try {
      return fs.readFileSync(p, 'utf8');
    } catch {
      return null;
    }
  },
};

const isDev = !app.isPackaged;
const startHidden = process.argv.includes('--hidden');
const colors = {
  light: { bg: '#fff4e0', fg: '#2a1a12' },
  dark: { bg: '#1d1b19', fg: '#f1ebe2' },
};

// ---- settings (tiny JSON in userData) ----
const settingsFile = () => path.join(app.getPath('userData'), 'settings.json');
const defaults: AppSettings = { closeToTray: true, startWithWindows: false, onboardingDone: false };
function loadSettings(): AppSettings {
  try {
    return { ...defaults, ...JSON.parse(fs.readFileSync(settingsFile(), 'utf8')) };
  } catch {
    return { ...defaults };
  }
}
let settings = defaults;

// ---- Core wiring ----
const locate = () =>
  locateCore({ env: process.env, resourcesPath: process.resourcesPath ?? '', devHostDir: path.resolve(__dirname, '..', '..', '..', 'host'), fs: realFs });
const port = () => discoverPort(locate(), realFs, process.env);
const token = () => discoverToken(locate(), realFs, process.env);
const api = createApiClient({ baseUrl: () => `http://127.0.0.1:${port()}`, token, refreshToken: token });

const logFile = () => path.join(locate().installDir, 'logs', 'core.log');
function logTail(): string {
  try {
    return fs.readFileSync(logFile(), 'utf8').trim().split(/\r?\n/).slice(-4).join(' | ').slice(-400);
  } catch {
    return '';
  }
}

const sidecar = new CoreSidecar({
  probe: () => api.probe(),
  locate,
  hasToken: () => token() !== '',
  port,
  spawn: (python, args, opts) => spawn(python, args, { ...opts, windowsHide: true, stdio: 'ignore' }),
  hasSystemPython: () => {
    for (const [cmd, args] of [['py', ['-3', '-c', 'print(1)']], ['python', ['-c', 'print(1)']]] as const) {
      const r = spawnSync(cmd, [...args], { timeout: 4000, windowsHide: true, encoding: 'utf8' });
      if (r.status === 0 && r.stdout.trim() === '1') return true;
    }
    return false;
  },
  sleep: (ms) => new Promise((r) => setTimeout(r, ms)),
  logTail,
  baseEnv: process.env,
});

// ---- window + tray ----
let win: BrowserWindow | null = null;
let tray: Tray | null = null;
let quitting = false;

function theme() {
  return nativeTheme.shouldUseDarkColors ? colors.dark : colors.light;
}

function createWindow(): BrowserWindow {
  const t = theme();
  const w = new BrowserWindow({
    width: 1180,
    height: 760,
    minWidth: 960,
    minHeight: 620,
    show: false,
    backgroundColor: t.bg,
    title: 'Nod Core',
    icon: path.join(__dirname, '..', '..', 'build', 'icon.png'),
    titleBarStyle: 'hidden',
    titleBarOverlay: { color: t.bg, symbolColor: t.fg, height: 44 },
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      additionalArguments: [`--nod-version=${app.getVersion()}`],
    },
  });
  w.setMenuBarVisibility(false);
  w.once('ready-to-show', () => {
    if (!startHidden) w.show();
  });
  w.on('close', (e) => {
    if (!quitting && settings.closeToTray) {
      e.preventDefault();
      w.hide();
    }
  });
  w.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:\/\//.test(url)) void shell.openExternal(url);
    return { action: 'deny' };
  });
  w.webContents.on('will-navigate', (e, url) => {
    if (!url.startsWith('http://localhost:5173') && !url.startsWith('file://')) e.preventDefault();
  });
  const dev = process.env.NOD_DEV_URL;
  if (dev) void w.loadURL(dev);
  else void w.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  return w;
}

function showWindow() {
  if (!win || win.isDestroyed()) win = createWindow();
  if (win.isMinimized()) win.restore();
  win.show();
  win.focus();
}

function createTray() {
  const img = nativeImage.createFromPath(path.join(__dirname, '..', '..', 'build', 'tray.png'));
  tray = new Tray(img);
  tray.setToolTip('Nod Core');
  tray.setContextMenu(
    Menu.buildFromTemplate([
      { label: 'Open Nod Core', click: showWindow },
      { type: 'separator' },
      { label: 'Quit', click: () => { quitting = true; app.quit(); } },
    ]),
  );
  tray.on('click', showWindow);
}

function applyLoginItem() {
  if (isDev) return;
  app.setLoginItemSettings({ openAtLogin: settings.startWithWindows, args: ['--hidden'] });
}

// ---- IPC ----
function setupIpc() {
  ipcMain.handle('core:state', () => sidecar.state);
  ipcMain.handle('core:ensure', () => sidecar.ensure());
  ipcMain.handle('core:restart', () => sidecar.restart());
  ipcMain.handle('core:open-logs', async () => {
    const f = logFile();
    if (fs.existsSync(f)) await shell.openPath(f);
    else await shell.openPath(locate().installDir);
  });
  ipcMain.handle('core:install', () => installCore());
  ipcMain.handle('api:request', (_e, method: string, p: string, body?: unknown) => {
    if (typeof p !== 'string' || !p.startsWith('/') || p.includes('..')) return { ok: false, status: 0, code: 'bad-request', message: 'Bad path.' };
    return api.request(method, p, body);
  });
  ipcMain.handle('api:screen', () => api.bytes('/core/cardputer/screen'));
  ipcMain.handle('api:audio', (_e, p: string, body: unknown) => (p === '/voices/preview' || p === '/say' ? api.bytes(p, 'POST', body) : { ok: false, status: 0, code: 'bad-request', message: 'Not allowed.' }));
  ipcMain.handle('device:pair', () => pairDevice());
  ipcMain.handle('settings:get', () => settings);
  ipcMain.handle('settings:set', (_e, patch: Partial<AppSettings>) => {
    const next = { ...settings };
    for (const k of Object.keys(defaults) as (keyof AppSettings)[]) if (typeof patch[k] === 'boolean') next[k] = patch[k] as boolean;
    settings = next;
    fs.mkdirSync(path.dirname(settingsFile()), { recursive: true });
    fs.writeFileSync(settingsFile(), JSON.stringify(settings));
    applyLoginItem();
    return settings;
  });
  ipcMain.handle('env:get', () => viewEnv(locate().envFile ? realFs.read(locate().envFile!) : null));
  ipcMain.handle('env:set', (_e, key: EnvKey, value: string) => {
    const loc = locate();
    const bad = validateEnvEdit(key, value);
    if (bad) return { ok: false, message: bad };
    if (!loc.envFile) return { ok: false, message: 'Core has no settings file yet. Set up Core first.' };
    fs.copyFileSync(loc.envFile, loc.envFile + '.nod-backup');
    fs.writeFileSync(loc.envFile, applyEnvEdit(realFs.read(loc.envFile) ?? '', key, value));
    return { ok: true, message: sidecar.isManaged ? 'Saved. Restart Core to apply.' : 'Saved. Restart Core (or sign out and in) to apply.' };
  });
  ipcMain.handle('shell:open-external', (_e, url: string) => (/^https?:\/\//.test(url) ? shell.openExternal(url) : undefined));
}

/** Copy the bundled host into the install dir (never touching .env or .venv) and run the existing installer in a visible console. */
async function installCore(): Promise<{ ok: boolean; message: string }> {
  const loc = locate();
  if (!loc.bundledDir) return { ok: false, message: 'This build does not include the Core files.' };
  try {
    fs.mkdirSync(loc.installDir, { recursive: true });
    if (path.resolve(loc.bundledDir) !== path.resolve(loc.installDir)) {
      fs.cpSync(loc.bundledDir, loc.installDir, {
        recursive: true,
        filter: (src) => !/[\\/](\.env|\.venv|__pycache__|tests|logs|data)([\\/]|$)/.test(src.slice(loc.bundledDir!.length)),
      });
      const ver = path.join(loc.bundledDir, 'VERSION');
      if (fs.existsSync(ver)) fs.copyFileSync(ver, path.join(loc.installDir, 'VERSION'));
    }
    const ps1 = path.join(loc.installDir, 'install-core.ps1');
    spawn('powershell.exe', ['-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-NoExit', '-File', ps1, '-NoBrowser'], {
      cwd: loc.installDir,
      detached: true,
      stdio: 'ignore',
    }).unref();
    return { ok: true, message: 'Setup is running in a separate window. When it says READY, come back and choose Check again.' };
  } catch (e) {
    return { ok: false, message: `Setup could not start: ${(e as Error).message}` };
  }
}

/** USB pairing reuses the existing pair.ps1 (Core address + token go to the device over USB serial). */
function pairDevice(): Promise<{ ok: boolean; message: string }> {
  const loc = locate();
  const ps1 = path.join(loc.installDir, 'pair.ps1');
  if (!fs.existsSync(ps1)) return Promise.resolve({ ok: false, message: 'Core is not set up yet, so there is nothing to pair.' });
  return new Promise((resolve) => {
    const child = spawn('powershell.exe', ['-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps1, '-Quiet'], { cwd: loc.installDir, windowsHide: true });
    let out = '';
    child.stdout.on('data', (d) => (out += d));
    child.stderr.on('data', (d) => (out += d));
    const timer = setTimeout(() => child.kill(), 30_000);
    child.on('close', (code) => {
      clearTimeout(timer);
      if (code === 0) return resolve({ ok: true, message: 'Your Nod is paired with this PC.' });
      const text = out.trim();
      resolve({
        ok: false,
        message: /not found over USB/i.test(text) ? 'Plug your Nod into this PC with a USB cable, then try again.' : text.split(/\r?\n/).filter(Boolean).slice(-1)[0]?.slice(0, 220) || 'Pairing did not finish.',
      });
    });
    child.on('error', (e) => resolve({ ok: false, message: e.message }));
  });
}

// ---- lifecycle ----
if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on('second-instance', showWindow);
  app.setAppUserModelId('uk.nod.core');
  void app.whenReady().then(() => {
    settings = loadSettings();
    Menu.setApplicationMenu(null);
    setupIpc();
    sidecar.on('state', (s) => win?.webContents.send('core:state-changed', s));
    nativeTheme.themeSource = 'light'; // brand is cream-based; no dark theme yet
    nativeTheme.on('updated', () => win?.setTitleBarOverlay({ color: theme().bg, symbolColor: theme().fg, height: 44 }));
    win = createWindow();
    createTray();
    applyLoginItem();
    void sidecar.ensure();
  });
  app.on('before-quit', () => {
    quitting = true;
    sidecar.stop();
  });
  app.on('window-all-closed', () => {
    if (quitting || !settings.closeToTray) app.quit();
  });
}
