// Safe, allow-listed edits to Core's .env. Secrets are write-only: the renderer only learns "is it set".
import type { CoreEnvView, EnvKey } from '../shared/types';
import { parseEnv } from './core-locator';

const ALLOWED: readonly EnvKey[] = ['MAZ_DEFAULT_ROUTE', 'MAZ_OLLAMA_MODEL', 'MAZ_GROQ_API_KEY', 'MAZ_OPENROUTER_API_KEY', 'MAZ_FISH_API_KEY'];
const ROUTES = ['local', 'auto', 'cloud', 'mazlatest'];

export function viewEnv(text: string | null): CoreEnvView {
  const e = text ? parseEnv(text) : {};
  const route = (e.MAZ_DEFAULT_ROUTE ?? '').toLowerCase();
  return {
    route: (ROUTES.includes(route) ? route : '') as CoreEnvView['route'],
    ollamaModel: e.MAZ_OLLAMA_MODEL ?? '',
    hasGroqKey: !!(e.MAZ_GROQ_API_KEY || e.MAZ_GROQ_KEY),
    hasOpenRouterKey: !!e.MAZ_OPENROUTER_API_KEY,
    hasFishKey: !!e.MAZ_FISH_API_KEY,
    envFile: text !== null,
  };
}

export function validateEnvEdit(key: string, value: string): string | null {
  if (!(ALLOWED as readonly string[]).includes(key)) return 'That setting cannot be changed from the app.';
  if (/[\r\n]/.test(value)) return 'Value must be a single line.';
  if (key === 'MAZ_DEFAULT_ROUTE' && !ROUTES.includes(value)) return 'Unknown route.';
  if (value.length > 400) return 'Value is too long.';
  return null;
}

/** Returns new .env text with KEY=value set (replacing an existing line, else appending). */
export function applyEnvEdit(text: string, key: string, value: string): string {
  const lines = text.split(/\r?\n/);
  let found = false;
  const out = lines.map((l) => {
    if (l.startsWith(key + '=')) {
      found = true;
      return `${key}=${value}`;
    }
    return l;
  });
  if (!found) {
    if (out.length && out[out.length - 1] === '') out.pop();
    out.push(`${key}=${value}`, '');
  }
  return out.join('\n');
}
