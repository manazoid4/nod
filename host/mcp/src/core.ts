// Thin HTTP client for Piblo Core (piblo-proto v1). No orchestration lives here: every decision
// (timeouts, halt, expiry, dedup, storage) is Core's. This file only turns tool calls into /buddy/* requests.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const VERSION = "0.1.0";
const DEFAULT_URL = "http://127.0.0.1:8787";

export interface CoreConfig {
  url: string;
  token: string;
  agent: string;
}

/** Pull MAZ_TOKEN / NOD_TOKEN / PIBLO_TOKEN out of a dotenv-style file. Returns "" when absent. */
export function tokenFromEnvFile(path: string): string {
  try {
    for (const line of readFileSync(path, "utf8").split(/\r?\n/)) {
      const m = /^\s*(?:export\s+)?(?:PIBLO_TOKEN|NOD_TOKEN|MAZ_TOKEN)\s*=\s*(.*?)\s*$/.exec(line);
      if (m) return m[1].replace(/^(['"])(.*)\1$/, "$2");
    }
  } catch {
    /* file missing or unreadable: fall through to "no token" */
  }
  return "";
}

/**
 * Token lookup, first hit wins: PIBLO_TOKEN / NOD_TOKEN / MAZ_TOKEN env, then a dotenv file
 * (PIBLO_ENV_FILE, else the host/.env that Core itself reads, found relative to this package).
 * shortcut: no OS credential store. Core keeps its token in host/.env and has no keyring dependency,
 * so a keyring lookup here would only add a native module. Upgrade when Core moves the token there.
 */
export function resolveToken(env: NodeJS.ProcessEnv = process.env): string {
  const direct = env.PIBLO_TOKEN || env.NOD_TOKEN || env.MAZ_TOKEN;
  if (direct) return direct;
  const here = dirname(fileURLToPath(import.meta.url));
  const file = env.PIBLO_ENV_FILE || join(here, "..", "..", ".env");
  return tokenFromEnvFile(file);
}

export function cleanAgentName(raw: string | undefined): string {
  // Control characters out, length bounded to Core's 60-char agent field.
  return (raw ?? "").replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, 60);
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): CoreConfig {
  return {
    url: (env.PIBLO_URL || DEFAULT_URL).replace(/\/+$/, ""),
    token: resolveToken(env),
    agent: cleanAgentName(env.PIBLO_AGENT_NAME),
  };
}

export class CoreError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status = 0,
  ) {
    super(message);
  }
}

export class CoreClient {
  constructor(private readonly cfg: CoreConfig) {}

  private async call<T>(method: "GET" | "POST", path: string, body?: unknown, timeoutMs = 10_000): Promise<T> {
    if (!this.cfg.token) {
      throw new CoreError("no_token", "No Piblo token found. Set PIBLO_TOKEN or start Core from a folder with host/.env.");
    }
    let res: Response;
    try {
      res = await fetch(this.cfg.url + path, {
        method,
        headers: {
          Authorization: `Bearer ${this.cfg.token}`,
          "Content-Type": "application/json",
          "X-Piblo-Client": `mcp/${VERSION}`,
        },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: AbortSignal.timeout(timeoutMs),
      });
    } catch {
      throw new CoreError("core_unreachable", `Piblo Core is not reachable at ${this.cfg.url}. Is it running?`);
    }
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const j = (await res.json()) as { detail?: unknown };
        if (typeof j.detail === "string") detail = j.detail;
      } catch {
        /* non-JSON error body */
      }
      throw new CoreError(res.status === 401 ? "unauthorized" : "core_error", `Core said ${res.status}: ${detail}`, res.status);
    }
    return (await res.json()) as T;
  }

  get<T>(path: string, timeoutMs?: number) {
    return this.call<T>("GET", path, undefined, timeoutMs);
  }
  post<T>(path: string, body: unknown, timeoutMs?: number) {
    return this.call<T>("POST", path, body, timeoutMs);
  }
}
