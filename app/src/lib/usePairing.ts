import { useCallback, useEffect, useState } from 'react';
import { decisionResult, pairPath, pendingRequests, type DecisionResult, type PairDecision, type PairRequest } from './pairing';

/** Polled every 2 s while onboarding or Settings is open, per the pairing contract. */
export const PAIRING_POLL_MS = 2000;

export interface PairingState {
  requests: PairRequest[];
  error: string | null;
  /** request_id currently being approved or denied. */
  busy: string | null;
  decide(requestId: string, decision: PairDecision): Promise<DecisionResult>;
  reload(): void;
}

/** Reads pending pairing requests from Core. Never approves anything by itself. */
export function usePairing({ active, ms = PAIRING_POLL_MS }: { active: boolean; ms?: number }): PairingState {
  const [requests, setRequests] = useState<PairRequest[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [nudge, setNudge] = useState(0);

  useEffect(() => {
    if (!active) {
      setRequests([]);
      return;
    }
    let live = true;
    const load = () =>
      void window.piblo.api<{ requests?: PairRequest[] }>('GET', '/pair/device/pending').then((r) => {
        if (!live) return;
        if (r.ok) {
          setRequests(pendingRequests(r.data?.requests));
          setError(null);
        } else setError(r.message);
      });
    load();
    const id = window.setInterval(load, ms);
    return () => {
      live = false;
      window.clearInterval(id);
    };
  }, [active, ms, nudge]);

  const decide = useCallback(async (requestId: string, decision: PairDecision) => {
    if (!requestId) return { ok: false, expired: true, message: 'That request expired, press Connect on Piblo again.' };
    setBusy(requestId);
    const r = await window.piblo.api<{ ok?: boolean }>('POST', pairPath(requestId, decision));
    setBusy(null);
    setRequests((list) => list.filter((x) => x.request_id !== requestId));
    return decisionResult(decision, r);
  }, []);

  return { requests, error, busy, decide, reload: () => setNudge((x) => x + 1) };
}
