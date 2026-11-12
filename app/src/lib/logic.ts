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
  title: string;
  done: boolean;
  hint: string;
}
export interface OnboardingInput {
  core: CoreState | null;
  connected: boolean; // pairing succeeded: the person pressed Allow
  pending: number; // how many devices are asking right now
}

/** Detects each onboarding step from live state, never from a button press alone. */
export function onboardingSteps(i: OnboardingInput): StepState[] {
  const coreUp = i.core?.phase === 'running';
  return [
    {
      title: 'Piblo on this PC',
      done: coreUp,
      hint: coreUp ? 'It is running on this PC.' : 'Starting it for you. This takes a few seconds the first time.',
    },
    {
      title: 'Connect your Piblo',
      done: i.connected,
      hint: i.connected
        ? 'Your Piblo is connected to this PC.'
        : i.pending > 0
          ? 'Check the code on Piblo matches the one below, then press Allow.'
          : 'On Piblo, open More, then Connect to computer. A code will appear here.',
    },
    {
      title: 'All set',
      done: i.connected,
      hint: i.connected ? 'Live View is ready to use.' : 'Finish the step above first.',
    },
  ];
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
