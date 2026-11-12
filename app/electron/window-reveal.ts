/**
 * First-paint gate for the main window.
 *
 * A window created with `show: false` only appears once `ready-to-show` fires. If the renderer
 * never paints (bad file URL, crash while loading, a slow first run), that event never arrives
 * and the app keeps running with an invisible 0x0 window: the process is in Task Manager but
 * nothing is on screen. This gate reveals on the first of `ready-to-show`, `did-finish-load` or
 * a failsafe timeout — and only once — so the window always becomes visible.
 *
 * `present()` is the separate, repeatable path used when the user asks for the window (tray
 * click, second instance, dock activation). It ignores the gate, so a window that was closed to
 * the tray or started hidden still comes back.
 */

export interface RevealableWindow {
  on(event: 'ready-to-show' | 'did-finish-load', listener: () => void): void;
  show(): void;
  focus(): void;
  restore(): void;
  isMinimized(): boolean;
  isDestroyed(): boolean;
}

export interface RevealOptions {
  /** Started minimised to the tray (`--hidden`): the gate stays shut until `present()`. */
  startHidden?: boolean;
  /** Failsafe delay before showing an unpainted window anyway. 0 disables the timer. */
  timeoutMs?: number;
}

export const REVEAL_FAILSAFE_MS = 4000;

export class WindowReveal {
  private revealed: boolean;

  constructor(
    private readonly win: RevealableWindow,
    opts: RevealOptions = {},
  ) {
    this.revealed = opts.startHidden === true;
    if (this.revealed) return;
    // Both events fire on a healthy load; the gate makes the second one a no-op.
    win.on('ready-to-show', () => void this.reveal());
    win.on('did-finish-load', () => void this.reveal());
    if (opts.timeoutMs === 0) return;
    const timer = setTimeout(() => void this.reveal(), opts.timeoutMs ?? REVEAL_FAILSAFE_MS);
    (timer as { unref?: () => void }).unref?.();
  }

  get hasRevealed(): boolean {
    return this.revealed;
  }

  /** Show the window for the first time. Returns true only for the call that made it visible. */
  reveal(): boolean {
    if (this.revealed || this.win.isDestroyed()) return false;
    this.revealed = true;
    this.present();
    return true;
  }

  /** Always bring the window up: tray click, second instance, or an explicit request. */
  present(): void {
    if (this.win.isDestroyed()) return;
    this.revealed = true;
    if (this.win.isMinimized()) this.win.restore();
    this.win.show();
    this.win.focus();
  }
}
