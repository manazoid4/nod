import { describe, expect, it, vi } from 'vitest';
import { createApiClient, friendly } from '../electron/api-client';

const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });
const asFetch = (f: unknown) => f as typeof fetch;
const mk = (f: unknown, extra: Partial<Parameters<typeof createApiClient>[0]> = {}) =>
  createApiClient({ baseUrl: () => 'http://127.0.0.1:8787', token: () => 'tok', fetch: asFetch(f), ...extra });

describe('api client', () => {
  it('sends the bearer token and JSON body', async () => {
    const f = vi.fn(async () => json(200, { ok: true }));
    const r = await mk(f).request('POST', '/x', { a: 1 });
    expect(r).toEqual({ ok: true, status: 200, data: { ok: true } });
    const [url, init] = f.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe('http://127.0.0.1:8787/x');
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer tok');
    expect(init.body).toBe('{"a":1}');
  });

  it('re-reads the token once after a 401 and retries', async () => {
    const f = vi.fn().mockResolvedValueOnce(json(401, { detail: 'authentication_required' })).mockResolvedValueOnce(json(200, { n: 1 }));
    const r = await mk(f, { refreshToken: () => 'new-tok' }).request('GET', '/needs');
    expect(r.ok).toBe(true);
    const retry = f.mock.calls[1] as unknown as [string, RequestInit];
    expect((retry[1].headers as Record<string, string>).Authorization).toBe('Bearer new-tok');
  });

  it('maps a refused connection to a plain "Core is not running" error', async () => {
    const r = await mk(vi.fn().mockRejectedValue(new TypeError('fetch failed'))).request('GET', '/health');
    expect(r).toMatchObject({ ok: false, code: 'offline', message: 'Core is not running.' });
  });

  it('maps timeouts, locked tokens and device errors to friendly messages', async () => {
    const t = Object.assign(new Error('x'), { name: 'TimeoutError' });
    expect(await mk(vi.fn().mockRejectedValue(t)).request('GET', '/a')).toMatchObject({ code: 'timeout' });
    expect(await mk(vi.fn(async () => json(401, { detail: 'authentication_required' }))).request('GET', '/a')).toMatchObject({ code: 'locked' });
    const d = await mk(vi.fn(async () => json(503, { detail: 'cardputer_unreachable:boom' }))).request('GET', '/a');
    expect(d).toMatchObject({ ok: false, code: 'device-offline' });
    expect(!d.ok && d.message).toMatch(/Nod is not reachable/);
  });

  it('returns raw bytes for the screen endpoint', async () => {
    const r = await mk(vi.fn(async () => new Response(new Uint8Array([1, 2, 3])))).bytes('/core/cardputer/screen');
    expect(r.ok && Array.from(r.data)).toEqual([1, 2, 3]);
  });

  it('probe only accepts a nod Core health answer', async () => {
    expect(await mk(vi.fn(async () => json(200, { ok: true, name: 'nod Core' }))).probe()).toBe(true);
    expect(await mk(vi.fn(async () => json(200, { name: 'something else' }))).probe()).toBe(false);
    expect(await mk(vi.fn().mockRejectedValue(new Error('refused'))).probe()).toBe(false);
  });

  it('friendly() humanises snake_case details', () => {
    expect(friendly('dump_not_found', 'x')).toBe('dump not found');
    expect(friendly(undefined, 'fallback')).toBe('fallback');
  });
});
