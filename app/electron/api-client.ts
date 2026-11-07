// Main-process HTTP client for Core. The token never reaches the renderer.
import type { ApiErrorCode, ApiResult } from '../shared/types';

export interface ApiClientDeps {
  baseUrl(): string;
  token(): string;
  /** Called after a 401 so the token can be re-read from .env (Core may have been reinstalled). */
  refreshToken?(): string;
  fetch?: typeof fetch;
  timeoutMs?: number;
}

const FRIENDLY: Record<string, string> = {
  authentication_required: 'Core rejected the saved token. Restart Core or re-run setup.',
  cardputer_unreachable: 'Your Nod is not reachable. Check it is on, on Wi-Fi, and paired.',
  approval_expired: 'That approval has already expired.',
  no_fish_key: 'No Fish Audio key is set, so voice search is unavailable.',
  too_many_auth_failures: 'Too many failed attempts. Wait a minute and try again.',
};

export function friendly(detail: unknown, fallback: string): string {
  const obj = detail && typeof detail === 'object' ? (detail as Record<string, unknown>) : null;
  const raw = typeof detail === 'string' ? detail : obj ? String(obj.message ?? obj.error ?? '') : '';
  if (!raw) return fallback;
  const key = Object.keys(FRIENDLY).find((k) => raw.includes(k));
  return key ? FRIENDLY[key] : raw.replace(/_/g, ' ');
}

export function createApiClient(deps: ApiClientDeps) {
  const doFetch = deps.fetch ?? fetch;
  const timeoutMs = deps.timeoutMs ?? 20_000;

  function once(method: string, path: string, body: unknown, token: string): Promise<Response> {
    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    let payload: string | undefined;
    if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
      payload = JSON.stringify(body);
    }
    return doFetch(deps.baseUrl() + path, { method, headers, body: payload, signal: AbortSignal.timeout(timeoutMs), cache: 'no-store' });
  }

  async function run<T>(method: string, path: string, body: unknown, raw: boolean): Promise<ApiResult<T>> {
    let res: Response;
    try {
      res = await once(method, path, body, deps.token());
      if (res.status === 401 && deps.refreshToken) {
        const fresh = deps.refreshToken();
        if (fresh && fresh !== deps.token()) res = await once(method, path, body, fresh);
      }
    } catch (e) {
      const timeout = e instanceof Error && (e.name === 'TimeoutError' || e.name === 'AbortError');
      return { ok: false, status: 0, code: timeout ? 'timeout' : 'offline', message: timeout ? 'Core took too long to answer.' : 'Core is not running.' };
    }
    if (res.ok) {
      if (raw) return { ok: true, status: res.status, data: new Uint8Array(await res.arrayBuffer()) as unknown as T };
      const text = await res.text();
      try {
        return { ok: true, status: res.status, data: (text ? JSON.parse(text) : {}) as T };
      } catch {
        return { ok: true, status: res.status, data: { text } as unknown as T };
      }
    }
    let detail: unknown;
    try {
      detail = ((await res.json()) as { detail?: unknown }).detail;
    } catch {
      detail = undefined;
    }
    const code: ApiErrorCode =
      res.status === 401 ? 'locked' : res.status === 503 || String(detail).includes('cardputer') ? 'device-offline' : res.status >= 500 ? 'server' : 'bad-request';
    return { ok: false, status: res.status, code, message: friendly(detail, `Core answered HTTP ${res.status}.`) };
  }

  return {
    request: <T = unknown>(method: string, path: string, body?: unknown) => run<T>(method, path, body, false),
    bytes: (path: string, method = 'GET', body?: unknown) => run<Uint8Array>(method, path, body, true),
    /** Unauthenticated probe: is a nod Core listening here? */
    async probe(): Promise<boolean> {
      try {
        const res = await doFetch(deps.baseUrl() + '/health', { signal: AbortSignal.timeout(2500), cache: 'no-store' });
        if (!res.ok) return false;
        const j = (await res.json()) as { name?: string };
        return typeof j.name === 'string' && /core/i.test(j.name);
      } catch {
        return false;
      }
    },
  };
}
export type ApiClient = ReturnType<typeof createApiClient>;
