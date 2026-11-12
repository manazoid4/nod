// Pairing: the PC side of docs/protocol/DEVICE-PAIRING.md. Pure functions only, so the card can be
// tested without Electron, a Core or a device.
import type { ApiResult } from '../../shared/types';

export interface PairRequest {
  request_id: string;
  code: string;
  name: string;
  device_id: string;
  ip: string;
  age_s: number;
}

/** Core expires a request 120 s after it was made; mirror that so a failed poll never leaves a stale card. */
export const REQUEST_TTL_S = 120;

export type PairDecision = 'allow' | 'deny';

/** "482913" -> "482 913", because the person compares it with two groups on the device screen. */
export function formatCode(code: string): string {
  const digits = String(code ?? '').replace(/\D/g, '');
  return digits.length === 6 ? `${digits.slice(0, 3)} ${digits.slice(3)}` : String(code ?? '');
}

export function deviceName(req: Pick<PairRequest, 'name'>): string {
  const name = String(req.name ?? '').trim();
  return name || 'Piblo';
}

export function pairingCardText(req: Pick<PairRequest, 'name' | 'code'>): { title: string; body: string } {
  const name = deviceName(req);
  return { title: `${name} wants to connect.`, body: `Check ${name} shows` };
}

/** Requests worth showing: still pending, younger than the TTL, oldest first, no duplicates. */
export function pendingRequests(list: PairRequest[] | undefined | null): PairRequest[] {
  const seen = new Set<string>();
  return (Array.isArray(list) ? list : [])
    .filter((r) => {
      if (!r || typeof r.request_id !== 'string' || !r.request_id || seen.has(r.request_id)) return false;
      seen.add(r.request_id);
      return !(typeof r.age_s === 'number' && r.age_s >= REQUEST_TTL_S);
    })
    .sort((a, b) => (b.age_s ?? 0) - (a.age_s ?? 0));
}

export function pairPath(requestId: string, decision: PairDecision): string {
  const id = encodeURIComponent(requestId);
  return `/pair/device/${id}/${decision === 'allow' ? 'approve' : 'deny'}`;
}

export interface DecisionResult {
  ok: boolean;
  /** True when Core says 404: the request expired or was already decided elsewhere. */
  expired: boolean;
  message: string;
}

export const EXPIRED_TEXT = 'That request expired, press Connect on Piblo again.';

/** Turns Core's answer into what the person sees. Approval is never assumed. */
export function decisionResult(decision: PairDecision, result: ApiResult<{ ok?: boolean }>): DecisionResult {
  if (result.ok) {
    return { ok: true, expired: false, message: decision === 'allow' ? 'Connected' : 'Not connected' };
  }
  if (result.status === 404) return { ok: false, expired: true, message: EXPIRED_TEXT };
  return { ok: false, expired: false, message: result.message };
}
