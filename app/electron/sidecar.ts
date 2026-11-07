// Core sidecar lifecycle: never duplicate a running Core, start it when we can, explain clearly when we cannot.
import { EventEmitter } from 'node:events';
import type { CoreState } from '../shared/types';
import type { CoreLocation } from './core-locator';

export interface ChildLike {
  pid?: number;
  kill(): boolean;
  once(event: 'exit', cb: (code: number | null) => void): unknown;
}

export interface SidecarDeps {
  probe(): Promise<boolean>;
  locate(): CoreLocation;
  hasToken(): boolean;
  port(): number;
  spawn(python: string, args: string[], opts: { cwd: string; env: Record<string, string> }): ChildLike;
  hasSystemPython(): boolean;
  sleep(ms: number): Promise<void>;
  startTimeoutMs?: number;
  logTail?(): string;
  baseEnv?: Record<string, string | undefined>;
}

export class CoreSidecar extends EventEmitter {
  private child: ChildLike | null = null;
  private exited = false;
  private inflight: Promise<CoreState> | null = null;
  state: CoreState;

  constructor(private deps: SidecarDeps) {
    super();
    this.state = this.make('checking', 'Looking for Nod Core...');
  }

  private make(phase: CoreState['phase'], message: string, detail?: string, managed = false): CoreState {
    const loc = this.deps.locate();
    return { phase, managed, message, detail, installDir: loc.installDir, port: this.deps.port(), hasToken: this.deps.hasToken() };
  }

  private set(s: CoreState): CoreState {
    this.state = s;
    this.emit('state', s);
    return s;
  }

  /** Idempotent: concurrent callers share one attempt. */
  ensure(): Promise<CoreState> {
    this.inflight ??= this.run().finally(() => {
      this.inflight = null;
    });
    return this.inflight;
  }

  private async run(): Promise<CoreState> {
    this.set(this.make('checking', 'Looking for Nod Core...', undefined, this.state.managed));
    if (await this.deps.probe()) {
      return this.set(this.make('running', 'Nod Core is running.', undefined, this.child !== null && !this.exited));
    }
    const loc = this.deps.locate();
    if (!loc.python || !loc.sourceDir) {
      if (!this.deps.hasSystemPython()) {
        return this.set(
          this.make('no-python', 'Python 3 is not installed, so Nod Core cannot run yet.', 'Install Python 3.11 or newer (winget install Python.Python.3.12), then choose Set up Core.'),
        );
      }
      return this.set(this.make('not-installed', 'Nod Core is not set up on this PC yet.', 'Set up Core to install the local service that talks to your Nod.'));
    }
    if (!loc.envFile || !this.deps.hasToken()) {
      return this.set(this.make('needs-setup', 'Nod Core needs its first-time setup.', 'The settings file or token is missing. Run setup to create them.'));
    }
    return this.spawnAndWait(loc);
  }

  private async spawnAndWait(loc: CoreLocation): Promise<CoreState> {
    this.set(this.make('starting', 'Starting Nod Core...', undefined, true));
    const env: Record<string, string> = {};
    for (const [k, v] of Object.entries(this.deps.baseEnv ?? {})) if (v !== undefined) env[k] = v;
    if (loc.sourceDir && loc.sourceDir !== loc.installDir) env.PYTHONPATH = loc.sourceDir;
    this.exited = false;
    try {
      this.child = this.deps.spawn(loc.python!, ['-m', 'mazhost'], { cwd: loc.installDir, env });
    } catch (e) {
      return this.set(this.make('failed', 'Nod Core could not be launched.', String((e as Error).message)));
    }
    this.child.once('exit', (code) => {
      this.exited = true;
      this.child = null;
      if (this.state.phase === 'running' || this.state.phase === 'starting') {
        this.set(this.make('failed', 'Nod Core stopped unexpectedly.', `Exit code ${code ?? 'unknown'}. ${this.deps.logTail?.() ?? ''}`.trim()));
      }
    });
    const deadline = this.deps.startTimeoutMs ?? 30_000;
    for (let waited = 0; waited < deadline; waited += 500) {
      if (this.exited) break;
      await this.deps.sleep(500);
      if (await this.deps.probe()) return this.set(this.make('running', 'Nod Core is running.', undefined, true));
    }
    const tail = this.deps.logTail?.() ?? '';
    this.stop();
    return this.set(this.make('failed', 'Nod Core did not start.', tail || 'No answer on the local port. Open the log for details.'));
  }

  /** Stops only a Core this app launched. A Core someone else started is left alone. */
  stop(): void {
    const c = this.child;
    this.child = null;
    if (c) {
      this.exited = true;
      try {
        c.kill();
      } catch {
        /* already gone */
      }
    }
  }

  async restart(): Promise<CoreState> {
    this.stop();
    await this.deps.sleep(300);
    return this.ensure();
  }

  get isManaged(): boolean {
    return this.child !== null;
  }
}
