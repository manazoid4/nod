import { EventEmitter } from 'node:events';
import { describe, expect, it, vi } from 'vitest';
import { createAppUpdater, type UpdaterLike } from '../electron/updater';

function fake() {
  const u = new EventEmitter() as UpdaterLike;
  u.autoDownload = false;
  u.autoInstallOnAppQuit = false;
  u.checkForUpdates = vi.fn(async () => undefined);
  u.quitAndInstall = vi.fn();
  return u;
}

describe('app updater', () => {
  it('downloads quietly then waits for one click to restart', async () => {
    const u = fake();
    const seen: string[] = [];
    const up = createAppUpdater(u, (s) => seen.push(s.state), true);
    expect(u.autoDownload).toBe(true);
    expect(up.install()).toBe(false);
    await up.check();
    u.emit('checking-for-update');
    u.emit('update-available', { version: '0.2.0' });
    u.emit('download-progress', { percent: 41.6 });
    expect(up.status()).toMatchObject({ state: 'downloading', progress: 42, version: '0.2.0' });
    u.emit('update-downloaded', { version: '0.2.0' });
    expect(up.status().state).toBe('ready');
    await up.check();
    expect(u.checkForUpdates).toHaveBeenCalledTimes(1); // no re-check once ready
    expect(up.install()).toBe(true);
    expect(u.quitAndInstall).toHaveBeenCalledWith(false, true);
    expect(seen).toEqual(['checking', 'downloading', 'downloading', 'ready']);
  });

  it('stays calm offline and is off in dev builds', async () => {
    const u = fake();
    u.checkForUpdates = vi.fn(async () => { throw new Error('offline'); });
    const up = createAppUpdater(u, () => {}, true);
    await up.check();
    expect(up.status().state).toBe('error');
    u.emit('update-not-available');
    expect(up.status().state).toBe('idle');

    const dev = createAppUpdater(fake(), () => {}, false);
    expect(dev.status().state).toBe('disabled');
    await dev.check();
    expect(dev.install()).toBe(false);
  });
});
