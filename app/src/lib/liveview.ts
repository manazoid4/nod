// Live View: the 2 fps screen poller, the on-screen buttons and the "type on Piblo" box.
// Kept free of React and of `window`, so the polling rules can be unit-tested.

export const FRAME_INTERVAL_MS = 500; // 2 fps, as the device can produce frames that fast
export const MAX_TYPE_CHARS = 400; // Core's /core/cardputer/key limit
export const UNREACHABLE_TEXT = "Piblo isn't reachable, check it's on and on the same Wi-Fi.";

export interface Frame {
  ok: boolean;
  status: number;
  message?: string;
}

export interface ScreenPollerDeps {
  read(): Promise<Frame>;
  /** True when the page or window is hidden: no traffic at all while hidden. */
  isHidden(): boolean;
  onFrame(frame: Frame): void;
  intervalMs?: number;
  every?(fn: () => void, ms: number): number;
  cancel?(id: number): void;
}

export interface ScreenPoller {
  start(): void;
  stop(): void;
  tick(): Promise<void>;
  readonly running: boolean;
}

/** Polls the screen while it is visible, stops the moment it is hidden, and never overlaps reads. */
export function createScreenPoller(deps: ScreenPollerDeps): ScreenPoller {
  const every = deps.every ?? ((fn, ms) => setInterval(fn, ms) as unknown as number);
  const cancel = deps.cancel ?? ((id) => clearInterval(id));
  let timer: number | null = null;
  let busy = false;

  const tick = async () => {
    if (busy || deps.isHidden()) return;
    busy = true;
    try {
      deps.onFrame(await deps.read());
    } catch (e) {
      deps.onFrame({ ok: false, status: 0, message: (e as Error).message });
    } finally {
      busy = false;
    }
  };

  return {
    start() {
      if (timer !== null) return;
      timer = every(() => void tick(), deps.intervalMs ?? FRAME_INTERVAL_MS);
      void tick();
    },
    stop() {
      if (timer === null) return;
      cancel(timer);
      timer = null;
    },
    tick,
    get running() {
      return timer !== null;
    },
  };
}

/** What to show under the screen when a frame does not arrive. */
export function frameMessage(frame: Frame | null, lastGood: boolean): string | null {
  if (!frame) return lastGood ? null : 'Waiting for the first frame...';
  if (frame.ok) return null;
  if (frame.status === 503) return UNREACHABLE_TEXT;
  if (frame.status === 0) return 'Piblo on this PC is not answering.';
  return frame.message || UNREACHABLE_TEXT;
}

/** On-screen buttons. Values match Core's `key:<hid>,<char>,<mods>` device action. */
export const DEVICE_BUTTONS: { label: string; action: string; wide?: boolean }[] = [
  { label: 'Esc', action: 'key:41,0,0' },
  { label: 'Tab', action: 'key:43,0,0' },
  { label: 'Enter', action: 'key:40,0,0' },
  { label: 'Left', action: 'key:80,0,0' },
  { label: 'Up', action: 'key:82,0,0' },
  { label: 'Down', action: 'key:81,0,0' },
  { label: 'Right', action: 'key:79,0,0' },
  { label: 'Backspace', action: 'key:42,0,0', wide: true },
];

/** Text for /core/cardputer/key: 1 to 400 printable characters, or null when there is nothing to send. */
export function typePayload(text: string): string | null {
  const clean = String(text ?? '')
    .replace(/[\r\n\t]+/g, ' ')
    .replace(/[^\x20-\x7e£]/g, '') // the device keyboard only takes printable ASCII
    .replace(/\s{2,}/g, ' ')
    .trim();
  if (!clean || clean.length > MAX_TYPE_CHARS) return null;
  return clean;
}
