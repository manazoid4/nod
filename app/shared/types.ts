// Types shared by the main process, preload bridge and renderer.

export type CorePhase =
  | 'checking'
  | 'starting'
  | 'running'
  | 'not-installed' // no Core files / venv on this PC
  | 'no-python' // Core files exist but Python 3 is missing, so Core cannot be set up
  | 'needs-setup' // venv exists but no .env / token yet
  | 'failed'; // we tried to start it and it did not come up

export interface CoreState {
  phase: CorePhase;
  /** true when this app launched Core (and will stop it on quit). */
  managed: boolean;
  message: string;
  detail?: string;
  installDir: string;
  port: number;
  hasToken: boolean;
}

export type ApiErrorCode = 'offline' | 'locked' | 'bad-request' | 'device-offline' | 'server' | 'timeout';

export type ApiResult<T = unknown> =
  | { ok: true; status: number; data: T }
  | { ok: false; status: number; code: ApiErrorCode; message: string };

export interface AppSettings {
  closeToTray: boolean;
  startWithWindows: boolean;
  onboardingDone: boolean;
}

export interface CoreEnvView {
  route: 'local' | 'auto' | 'cloud' | 'mazlatest' | '';
  ollamaModel: string;
  hasGroqKey: boolean;
  hasOpenRouterKey: boolean;
  hasFishKey: boolean;
  envFile: boolean;
}

export type EnvKey = 'MAZ_DEFAULT_ROUTE' | 'MAZ_OLLAMA_MODEL' | 'MAZ_GROQ_API_KEY' | 'MAZ_OPENROUTER_API_KEY' | 'MAZ_FISH_API_KEY';

export interface NodBridge {
  platform: string;
  version: string;
  core: {
    state(): Promise<CoreState>;
    ensure(): Promise<CoreState>;
    restart(): Promise<CoreState>;
    install(): Promise<{ ok: boolean; message: string }>;
    openLogs(): Promise<void>;
    onState(cb: (s: CoreState) => void): () => void;
  };
  api<T = unknown>(method: 'GET' | 'POST' | 'PATCH' | 'DELETE', path: string, body?: unknown): Promise<ApiResult<T>>;
  screen(): Promise<ApiResult<Uint8Array>>;
  /** POST that returns audio bytes (voice preview / say). */
  audio(path: string, body: unknown): Promise<ApiResult<Uint8Array>>;
  device: { pair(): Promise<{ ok: boolean; message: string }> };
  settings: {
    get(): Promise<AppSettings>;
    set(patch: Partial<AppSettings>): Promise<AppSettings>;
  };
  env: {
    get(): Promise<CoreEnvView>;
    set(key: EnvKey, value: string): Promise<{ ok: boolean; message: string }>;
  };
  openExternal(url: string): Promise<void>;
}

declare global {
  interface Window {
    nod: NodBridge;
  }
}
