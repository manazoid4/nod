import { describe, expect, it } from 'vitest';
import type { ApiResult } from '../shared/types';
import { decisionResult, EXPIRED_TEXT, formatCode, pairingCardText, pairPath, pendingRequests, REQUEST_TTL_S, type PairRequest } from '../src/lib/pairing';

const req = (over: Partial<PairRequest> = {}): PairRequest => ({
  request_id: 'r1',
  code: '482913',
  name: 'Piblo',
  device_id: 'piblo-a1b2',
  ip: '192.168.1.42',
  age_s: 8,
  ...over,
});

describe('pairing card copy', () => {
  it('groups the code the way the device shows it', () => {
    expect(formatCode('482913')).toBe('482 913');
    expect(formatCode('12345')).toBe('12345'); // never invents digits
  });

  it('says exactly what the person compares on both screens', () => {
    expect(pairingCardText(req())).toEqual({ title: 'Piblo wants to connect.', body: 'Check Piblo shows' });
    expect(pairingCardText(req({ name: '  ' })).title).toBe('Piblo wants to connect.');
  });
});

describe('pending requests', () => {
  it('hides what Core has already expired or removed', () => {
    const list = [req({ request_id: 'a', age_s: 5 }), req({ request_id: 'b', age_s: REQUEST_TTL_S }), req({ request_id: 'c', age_s: 119 })];
    expect(pendingRequests(list).map((r) => r.request_id)).toEqual(['c', 'a']);
    expect(pendingRequests([])).toEqual([]);
    expect(pendingRequests(undefined)).toEqual([]);
  });

  it('drops duplicates and puts the oldest request first', () => {
    const list = [req({ request_id: 'same', age_s: 1 }), req({ request_id: 'same', age_s: 1 }), req({ request_id: 'old', age_s: 60 })];
    expect(pendingRequests(list).map((r) => r.request_id)).toEqual(['old', 'same']);
  });
});

describe('approve and deny', () => {
  const ok: ApiResult<{ ok?: boolean }> = { ok: true, status: 200, data: { ok: true } };

  it('reports Connected only after Core says yes', () => {
    expect(decisionResult('allow', ok)).toEqual({ ok: true, expired: false, message: 'Connected' });
    expect(decisionResult('deny', ok)).toEqual({ ok: true, expired: false, message: 'Not connected' });
  });

  it('explains an expired request when Core answers 404', () => {
    const gone: ApiResult<{ ok?: boolean }> = { ok: false, status: 404, code: 'bad-request', message: 'Core answered HTTP 404.' };
    expect(decisionResult('allow', gone)).toEqual({ ok: false, expired: true, message: EXPIRED_TEXT });
    expect(EXPIRED_TEXT).toMatch(/press Connect on Piblo again/);
  });

  it('passes other failures through unchanged', () => {
    const offline: ApiResult<{ ok?: boolean }> = { ok: false, status: 0, code: 'offline', message: 'Piblo on this PC is not running.' };
    expect(decisionResult('allow', offline)).toEqual({ ok: false, expired: false, message: 'Piblo on this PC is not running.' });
  });

  it('builds the documented routes and encodes the id', () => {
    expect(pairPath('abc', 'allow')).toBe('/pair/device/abc/approve');
    expect(pairPath('abc', 'deny')).toBe('/pair/device/abc/deny');
    expect(pairPath('a/b c', 'allow')).toBe('/pair/device/a%2Fb%20c/approve');
  });
});
