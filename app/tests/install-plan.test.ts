import { describe, expect, it } from 'vitest';
import { findCoreTask, isSafeTaskName, planInstall } from '../electron/install-plan';

describe('install plan', () => {
  it('reuses the nod-core scheduled task and skips the Startup-folder installer', () => {
    expect(planInstall(['OneDrive Standalone Update', 'nod-core'])).toEqual({ kind: 'reuse-task', task: 'nod-core' });
  });
  it('recognises older "MAZ Core" tasks', () => {
    expect(findCoreTask(['MAZ Core'])).toBe('MAZ Core');
    expect(findCoreTask(['MAZ Core Autostart'])).toBe('MAZ Core Autostart');
    expect(findCoreTask(['maz-core'])).toBe('maz-core');
  });
  it('prefers nod-core when both exist', () => {
    expect(findCoreTask(['MAZ Core', 'Nod-Core'])).toBe('Nod-Core');
  });
  it('falls back to the installer when no Core task exists', () => {
    expect(planInstall([])).toEqual({ kind: 'run-installer' });
    expect(planInstall(['MAZ Corner Shop', 'Updater'])).toEqual({ kind: 'run-installer' });
  });
  it('only passes plain task names to schtasks', () => {
    expect(isSafeTaskName('nod-core')).toBe(true);
    expect(isSafeTaskName('MAZ Core')).toBe(true);
    expect(isSafeTaskName('x" & calc & "')).toBe(false);
  });
});
