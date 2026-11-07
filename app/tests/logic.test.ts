import { describe, expect, it } from 'vitest';
import type { CoreState } from '../shared/types';
import { applyEnvEdit, validateEnvEdit, viewEnv } from '../electron/env-file';
import { decodeRgb565, devicePill, keyAction, onboardingSteps, SCREEN_H, SCREEN_W, type DeviceInfo } from '../src/lib/logic';

const core = (phase: CoreState['phase']): CoreState => ({ phase, managed: false, message: '', installDir: 'I', port: 8787, hasToken: true });

describe('rgb565', () => {
  it('rejects wrong-sized frames and decodes colours', () => {
    expect(decodeRgb565(new Uint8Array(10))).toBeNull();
    const f = new Uint8Array(SCREEN_W * SCREEN_H * 2);
    f[0] = 0x00;
    f[1] = 0xf8; // 0xF800 little-endian = pure red
    const px = decodeRgb565(f)!;
    expect([px[0], px[1], px[2], px[3]]).toEqual([255, 0, 0, 255]);
  });
});

describe('device pill', () => {
  it('is Not connected when Core is down or the device is offline', () => {
    expect(devicePill(core('not-installed'), null, false).label).toBe('Not connected');
    expect(devicePill(core('running'), { online: false }, false).state).toBe('disconnected');
  });
  it('shows battery and firmware when connected, Pairing while pairing', () => {
    const p = devicePill(core('running'), { online: true, device: { battery: 82, version: '1.0.2' } }, false);
    expect(p).toMatchObject({ state: 'connected', battery: 82, firmware: 'v1.0.2' });
    expect(devicePill(core('running'), null, true).state).toBe('pairing');
    expect(devicePill(core('running'), { online: true, device: { battery: -1 } }, false).battery).toBeNull();
  });
});

describe('onboarding detection', () => {
  const offline: DeviceInfo = { online: false };
  const base = { core: core('running'), info: offline as DeviceInfo | null, paired: false, sentId: null as string | null, historyIds: [] as string[] };
  const done = (o: Partial<typeof base>) => onboardingSteps({ ...base, ...o }).map((s) => s.done);
  it('does not tick anything while Core is down', () => {
    expect(done({ core: core('failed') })).toEqual([false, false, false, false]);
  });
  it('ticks from API state, in order', () => {
    expect(done({ info: { online: true, device: {} } })).toEqual([true, true, false, false]);
    expect(done({ info: { online: true }, sentId: 'm1' })).toEqual([true, true, true, false]);
    expect(done({ info: { online: true }, sentId: 'm1', historyIds: ['m1'] })).toEqual([true, true, true, true]);
  });
  it('pair step completes after a successful USB pair', () => {
    expect(onboardingSteps({ ...base, paired: true })[1].done).toBe(true);
  });
});

describe('remote keys', () => {
  it('maps keyboard events to Core device actions', () => {
    const e = { code: 'KeyA', key: 'a', ctrlKey: false, shiftKey: false, altKey: false };
    expect(keyAction(e)).toBe('key:4,97,0');
    expect(keyAction({ ...e, code: 'Enter', key: 'Enter', ctrlKey: true })).toBe('key:40,0,1');
    expect(keyAction({ ...e, code: 'F13', key: 'F13' })).toBeNull();
  });
});

describe('env edits', () => {
  it('only allows listed keys and sane values', () => {
    expect(validateEnvEdit('MAZ_TOKEN', 'x')).not.toBeNull();
    expect(validateEnvEdit('MAZ_DEFAULT_ROUTE', 'banana')).not.toBeNull();
    expect(validateEnvEdit('MAZ_GROQ_API_KEY', 'a\nMAZ_TOKEN=evil')).not.toBeNull();
    expect(validateEnvEdit('MAZ_DEFAULT_ROUTE', 'cloud')).toBeNull();
  });
  it('replaces or appends a line without touching the rest', () => {
    expect(applyEnvEdit('MAZ_TOKEN=t\nMAZ_DEFAULT_ROUTE=local\n', 'MAZ_DEFAULT_ROUTE', 'cloud')).toBe('MAZ_TOKEN=t\nMAZ_DEFAULT_ROUTE=cloud\n');
    expect(applyEnvEdit('MAZ_TOKEN=t\n', 'MAZ_GROQ_API_KEY', 'k')).toBe('MAZ_TOKEN=t\nMAZ_GROQ_API_KEY=k\n');
  });
  it('never exposes secret values to the renderer', () => {
    const v = viewEnv('MAZ_GROQ_API_KEY=secret\nMAZ_DEFAULT_ROUTE=auto');
    expect(v).toMatchObject({ hasGroqKey: true, route: 'auto' });
    expect(JSON.stringify(v)).not.toContain('secret');
  });
});
