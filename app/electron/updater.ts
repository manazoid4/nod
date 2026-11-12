// Quiet app updates, Apple style: check GitHub Releases, download in the background,
// then one "Restart to update" action. Nothing installs without the user's click (or on quit).
import { EventEmitter } from 'node:events';
import type { UpdateStatus } from '../shared/types';

export interface UpdaterLike extends EventEmitter {
  autoDownload: boolean;
  autoInstallOnAppQuit: boolean;
  checkForUpdates(): Promise<unknown>;
  quitAndInstall(isSilent?: boolean, isForceRunAfter?: boolean): void;
}

const CHECK_EVERY_MS = 4 * 60 * 60 * 1000;

export function createAppUpdater(updater: UpdaterLike, onChange: (s: UpdateStatus) => void, enabled: boolean) {
  let status: UpdateStatus = { state: enabled ? 'idle' : 'disabled', progress: 0, version: '' };
  const set = (patch: Partial<UpdateStatus>) => {
    status = { ...status, ...patch };
    onChange(status);
  };
  updater.autoDownload = true;
  updater.autoInstallOnAppQuit = true;
  updater.on('checking-for-update', () => status.state !== 'ready' && set({ state: 'checking' }));
  updater.on('update-available', (info: { version?: string }) => set({ state: 'downloading', progress: 0, version: info?.version ?? '' }));
  updater.on('update-not-available', () => set({ state: 'idle', progress: 0 }));
  updater.on('download-progress', (p: { percent?: number }) => set({ state: 'downloading', progress: Math.round(p?.percent ?? 0) }));
  updater.on('update-downloaded', (info: { version?: string }) => set({ state: 'ready', progress: 100, version: info?.version ?? status.version }));
  // Offline or no release yet: stay calm, try again next interval.
  updater.on('error', () => status.state !== 'ready' && set({ state: 'error' }));

  const check = async () => {
    if (!enabled || status.state === 'ready' || status.state === 'downloading') return status;
    try {
      await updater.checkForUpdates();
    } catch {
      set({ state: 'error' });
    }
    return status;
  };
  let timer: ReturnType<typeof setInterval> | undefined;
  return {
    status: () => status,
    check,
    install: () => {
      if (status.state !== 'ready') return false;
      updater.quitAndInstall(true, true); // silent: no installer wizard, then reopen Piblo
      return true;
    },
    start: () => {
      if (!enabled || timer) return;
      void check();
      timer = setInterval(() => void check(), CHECK_EVERY_MS);
    },
    stop: () => timer && clearInterval(timer),
  };
}
