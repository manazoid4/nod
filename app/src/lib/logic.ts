// Pure renderer logic (unit-tested): frame decoding, device pill, onboarding detection, key mapping.
import type { CoreState } from '../../shared/types';

export const SCREEN_W = 240;
export const SCREEN_H = 135;

/** Decode a little-endian RGB565 frame (240x135) to RGBA. Returns null when the frame is the wrong size. */
export function decodeRgb565(bytes: Uint8Array): Uint8ClampedArray<ArrayBuffer> | null {
  if (bytes.length !== SCREEN_W * SCREEN_H * 2) return null;
  const out = new Uint8ClampedArray(new ArrayBuffer(SCREEN_W * SCREEN_H * 4));
  for (let p = 0, i = 0; p < SCREEN_W * SCREEN_H; p++, i += 2) {
    const v = bytes[i] | (bytes[i + 1] << 8);
    const o = p * 4;
    out[o] = (((v >> 11) & 31) * 255) / 31;
    out[o + 1] = (((v >> 5) & 63) * 255) / 63;
    out[o + 2] = ((v & 31) * 255) / 31;
    out[o + 3] = 255;
  }
  return out;
}

export interface DeviceInfo {
  device?: { version?: string; fw_build?: string; battery?: number; app?: string };
  online?: boolean;
  hub_fw?: { version?: string; sha?: string; size?: number } | null;
  update_available?: boolean;
  hub_update?: unknown;
  last_report?: { stage?: string; error?: string } | null;
}

export type PillState = 'connected' | 'disconnected' | 'pairing';
export interface DevicePill {
  state: PillState;
  label: string;
  battery: number | null;
  firmware: string;
}

export function devicePill(core: CoreState | null, info: DeviceInfo | null, pairing: boolean): DevicePill {
  if (pairing) return { state: 'pairing', label: 'Pairing', battery: null, firmware: '' };
  if (core?.phase === 'running' && info?.online && info.device) {
    const b = info.device.battery;
    return {
      state: 'connected',
      label: 'Connected',
      battery: typeof b === 'number' && b >= 0 ? b : null,
      firmware: info.device.version ? `v${info.device.version}` : '',
    };
  }
  return { state: 'disconnected', label: 'Not connected', battery: null, firmware: '' };
}

export interface StepState {
  done: boolean;
  hint: string;
}
export interface OnboardingInput {
  core: CoreState | null;
  info: DeviceInfo | null;
  paired: boolean; // pairing succeeded this session
  sentId: string | null; // beam message id from the first action
  historyIds: string[];
}

/** Detects each onboarding step from live API state, never from a button press alone. */
export function onboardingSteps(i: OnboardingInput): StepState[] {
  const coreUp = i.core?.phase === 'running';
  const online = coreUp && !!i.info?.online;
  const connect: StepState = {
    done: online,
    hint: !coreUp ? 'Core is not running yet. Start it first.' : online ? 'Your Nod answered.' : 'Turn on your Nod and make sure it is on the same Wi-Fi as this PC.',
  };
  const pair: StepState = {
    done: i.paired || online,
    hint: i.paired || online ? 'Your Nod knows this PC.' : 'Plug your Nod into this PC with a USB cable, then press Pair.',
  };
  const act: StepState = {
    done: i.sentId !== null,
    hint: i.sentId ? 'Sent.' : 'Send a short note to your Nod.',
  };
  const result: StepState = {
    done: i.sentId !== null && i.historyIds.includes(i.sentId),
    hint: i.sentId && i.historyIds.includes(i.sentId) ? 'Core saved it and your Nod will show it.' : 'Waiting for Core to confirm the note.',
  };
  return [connect, pair, act, result];
}

const MODS = { ctrl: 1, shift: 2, alt: 4 };
const HID: Record<string, number> = {
  Enter: 0x28, Escape: 0x29, Backspace: 0x2a, Tab: 0x2b, Space: 0x2c, Minus: 0x2d, Equal: 0x2e, BracketLeft: 0x2f, BracketRight: 0x30,
  Backslash: 0x31, Semicolon: 0x33, Quote: 0x34, Backquote: 0x35, Comma: 0x36, Period: 0x37, Slash: 0x38, Delete: 0x4c,
  ArrowRight: 0x4f, ArrowLeft: 0x50, ArrowDown: 0x51, ArrowUp: 0x52, Digit0: 0x27,
};

export function hidOf(code: string): number {
  if (/^Key[A-Z]$/.test(code)) return 4 + code.charCodeAt(3) - 65;
  if (/^Digit[1-9]$/.test(code)) return 0x1e + code.charCodeAt(5) - 49;
  return HID[code] ?? 0;
}

/** Builds Core's `key:hid,char,mods` device action from a keyboard event; null when unmapped. */
export function keyAction(e: { code: string; key: string; ctrlKey: boolean; shiftKey: boolean; altKey: boolean }): string | null {
  const hid = hidOf(e.code);
  if (!hid) return null;
  const ch = e.key.length === 1 && e.key.charCodeAt(0) < 127 ? e.key.charCodeAt(0) : 0;
  const mods = (e.ctrlKey ? MODS.ctrl : 0) | (e.shiftKey ? MODS.shift : 0) | (e.altKey ? MODS.alt : 0);
  return `key:${hid},${ch},${mods}`;
}

export function ago(seconds: number): string {
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} h ago`;
  return `${Math.floor(seconds / 86400)} d ago`;
}
