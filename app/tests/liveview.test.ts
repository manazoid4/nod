import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createScreenPoller, DEVICE_BUTTONS, FRAME_INTERVAL_MS, frameMessage, MAX_TYPE_CHARS, typePayload, UNREACHABLE_TEXT, type Frame } from '../src/lib/liveview';

function harness(reads: () => Promise<Frame>) {
  let hidden = false;
  let count = 0;
  const frames: Frame[] = [];
  const poller = createScreenPoller({
    read: () => {
      count += 1;
      return reads();
    },
    isHidden: () => hidden,
    onFrame: (f) => frames.push(f),
  });
  return {
    poller,
    frames,
    hide: (v: boolean) => (hidden = v),
    get count() {
      return count;
    },
  };
}

describe('live view polling', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('polls at 2 fps while visible and stops dead when hidden', async () => {
    const h = harness(async () => ({ ok: true, status: 200 }));
    expect(FRAME_INTERVAL_MS).toBe(500);
    h.poller.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(h.count).toBe(1); // first frame right away

    await vi.advanceTimersByTimeAsync(FRAME_INTERVAL_MS * 3);
    expect(h.count).toBe(4);

    h.hide(true);
    await vi.advanceTimersByTimeAsync(FRAME_INTERVAL_MS * 10);
    expect(h.count).toBe(4); // no traffic at all while hidden

    h.hide(false);
    await vi.advanceTimersByTimeAsync(FRAME_INTERVAL_MS);
    expect(h.count).toBe(5); // resumes on its own
  });

  it('stops when the page goes away', async () => {
    const h = harness(async () => ({ ok: true, status: 200 }));
    h.poller.start();
    await vi.advanceTimersByTimeAsync(0);
    const seen = h.count;
    h.poller.stop();
    expect(h.poller.running).toBe(false);
    await vi.advanceTimersByTimeAsync(FRAME_INTERVAL_MS * 5);
    expect(h.count).toBe(seen);
  });

  it('never overlaps two frames', async () => {
    let release: (f: Frame) => void = () => {};
    const slow = new Promise<Frame>((resolve) => (release = resolve));
    const h = harness(() => slow);
    void h.poller.tick();
    void h.poller.tick();
    expect(h.count).toBe(1);
    release({ ok: true, status: 200 });
    await vi.advanceTimersByTimeAsync(0);
    expect(h.frames).toHaveLength(1);
  });

  it('shows the friendly message when Piblo answers 503', async () => {
    const h = harness(async () => ({ ok: false, status: 503, message: 'cardputer unreachable' }));
    h.poller.start();
    await vi.advanceTimersByTimeAsync(0);
    expect(frameMessage(h.frames[0], false)).toBe(UNREACHABLE_TEXT);
    expect(UNREACHABLE_TEXT).toBe("Piblo isn't reachable, check it's on and on the same Wi-Fi.");
  });
});

describe('screen messages', () => {
  it('is quiet while frames arrive and clear when Piblo is off', () => {
    expect(frameMessage({ ok: true, status: 200 }, true)).toBeNull();
    expect(frameMessage({ ok: false, status: 0 }, false)).toMatch(/not answering/);
    expect(frameMessage(null, false)).toMatch(/first frame/);
  });
});

describe('live view keys', () => {
  it('sends Core-shaped device actions for every on-screen button', () => {
    expect(DEVICE_BUTTONS.map((b) => b.label)).toEqual(['Esc', 'Tab', 'Enter', 'Left', 'Up', 'Down', 'Right', 'Backspace']);
    for (const b of DEVICE_BUTTONS) expect(b.action).toMatch(/^key:\d{1,3},\d{1,3},\d{1,2}$/);
    expect(DEVICE_BUTTONS.find((b) => b.label === 'Esc')!.action).toBe('key:41,0,0');
    expect(DEVICE_BUTTONS.find((b) => b.label === 'Enter')!.action).toBe('key:40,0,0');
  });
});

describe('type on Piblo', () => {
  it('accepts 1 to 400 printable characters', () => {
    expect(typePayload('hello')).toBe('hello');
    expect(typePayload('  ')).toBeNull();
    expect(typePayload('a'.repeat(MAX_TYPE_CHARS))).toHaveLength(MAX_TYPE_CHARS);
    expect(typePayload('a'.repeat(MAX_TYPE_CHARS + 1))).toBeNull();
  });

  it('strips what the device keyboard cannot type instead of silently sending it', () => {
    expect(typePayload('hi\nthere')).toBe('hi there');
    expect(typePayload('caf\u00e9 \u00a3')).toBe('caf \u00a3');
    expect(typePayload('a\t\tb')).toBe('a b');
  });
});
