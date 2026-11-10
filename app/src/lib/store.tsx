import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import type { ApiResult, CoreState } from '../../shared/types';
import { devicePill, type DeviceInfo, type DevicePill } from './logic';

export interface Health {
  version?: string;
  git_sha?: string;
  llm?: { local?: boolean; local_model?: string; local_model_installed?: boolean; local_engine?: string; last_route?: Record<string, unknown> };
  stt?: unknown;
  tts?: unknown;
  update?: { available?: boolean; latest?: string } | null;
  fw_latest?: { version?: string; sha?: string } | null;
  remote_url?: string;
}

interface Toast {
  text: string;
  bad: boolean;
}

interface Ctx {
  core: CoreState | null;
  health: Health | null;
  deviceInfo: DeviceInfo | null;
  pill: DevicePill;
  pairing: boolean;
  setPairing(v: boolean): void;
  refreshDevice(): void;
  toast(text: string, bad?: boolean): void;
  toastNow: Toast | null;
  needsCount: number;
  setNeedsCount(n: number): void;
}

const StoreCtx = createContext<Ctx | null>(null);
export const useStore = () => {
  const c = useContext(StoreCtx);
  if (!c) throw new Error('store missing');
  return c;
};

export function StoreProvider({ children }: { children: ReactNode }) {
  const [core, setCore] = useState<CoreState | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo | null>(null);
  const [pairing, setPairing] = useState(false);
  const [toastNow, setToast] = useState<Toast | null>(null);
  const [needsCount, setNeedsCount] = useState(0);
  const timer = useRef<number>();

  useEffect(() => {
    void window.piblo.core.state().then(setCore);
    return window.piblo.core.onState(setCore);
  }, []);

  const running = core?.phase === 'running';
  const refreshDevice = useCallback(() => {
    if (!running) return;
    void window.piblo.api<DeviceInfo>('GET', '/core/device').then((r) => setDeviceInfo(r.ok ? r.data : null));
  }, [running]);

  useEffect(() => {
    if (!running) {
      setHealth(null);
      setDeviceInfo(null);
      return;
    }
    const tick = () => {
      void window.piblo.api<Health>('GET', '/health').then((r) => setHealth(r.ok ? r.data : null));
      refreshDevice();
    };
    tick();
    const id = window.setInterval(tick, 5000);
    return () => window.clearInterval(id);
  }, [running, refreshDevice]);

  const toast = useCallback((text: string, bad = false) => {
    setToast({ text, bad });
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setToast(null), 3200);
  }, []);

  const pill = useMemo(() => devicePill(core, deviceInfo, pairing), [core, deviceInfo, pairing]);
  const value: Ctx = { core, health, deviceInfo, pill, pairing, setPairing, refreshDevice, toast, toastNow, needsCount, setNeedsCount };
  return <StoreCtx.Provider value={value}>{children}</StoreCtx.Provider>;
}

/** Poll an endpoint while Core is running. Errors are returned, never thrown. */
export function usePoll<T>(path: string | null, ms = 5000): { data: T | null; error: string | null; loading: boolean; reload(): void } {
  const { core } = useStore();
  const running = core?.phase === 'running';
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [n, setN] = useState(0);
  useEffect(() => {
    if (!path || !running) {
      setLoading(false);
      return;
    }
    let live = true;
    const load = () =>
      void window.piblo.api<T>('GET', path).then((r: ApiResult<T>) => {
        if (!live) return;
        setLoading(false);
        if (r.ok) {
          setData(r.data);
          setError(null);
        } else setError(r.message);
      });
    load();
    const id = ms > 0 ? window.setInterval(load, ms) : 0;
    return () => {
      live = false;
      window.clearInterval(id);
    };
  }, [path, running, ms, n]);
  return { data, error, loading, reload: () => setN((x) => x + 1) };
}

/** Run an action with toast feedback. */
export function useAct() {
  const { toast } = useStore();
  return useCallback(
    async <T,>(method: 'GET' | 'POST' | 'PATCH', path: string, body?: unknown, ok?: string): Promise<ApiResult<T>> => {
      const r = await window.piblo.api<T>(method, path, body);
      if (r.ok) {
        if (ok) toast(ok);
      } else toast(r.message, true);
      return r;
    },
    [toast],
  );
}
