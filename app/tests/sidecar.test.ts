import { describe, expect, it, vi } from 'vitest';
import type { CoreLocation } from '../electron/core-locator';
import { CoreSidecar, type ChildLike, type SidecarDeps } from '../electron/sidecar';

const ready: CoreLocation = { installDir: 'I', sourceDir: 'S', python: 'py.exe', envFile: 'I\\.env', bundledDir: 'S' };

function make(over: Partial<SidecarDeps> & { loc?: CoreLocation } = {}) {
  const child = {
    pid: 1,
    kill: vi.fn(() => true),
    exitCb: null as null | ((c: number | null) => void),
    once(_e: 'exit', cb: (c: number | null) => void) {
      this.exitCb = cb;
    },
  };
  const spawn = vi.fn((..._a: unknown[]) => child as ChildLike);
  const deps: SidecarDeps = {
    probe: async () => false,
    locate: () => over.loc ?? ready,
    hasToken: () => true,
    port: () => 8787,
    spawn: spawn as unknown as SidecarDeps['spawn'],
    hasSystemPython: () => true,
    sleep: async () => {},
    startTimeoutMs: 2000,
    ...over,
  };
  return { sc: new CoreSidecar(deps), spawn, child };
}

describe('CoreSidecar', () => {
  it('never duplicates a Core that is already running', async () => {
    const { sc, spawn } = make({ probe: async () => true });
    const s = await sc.ensure();
    expect(s.phase).toBe('running');
    expect(s.managed).toBe(false);
    expect(spawn).not.toHaveBeenCalled();
    sc.stop(); // must not kill what it did not start
  });

  it('spawns Core with the right cwd, args and PYTHONPATH, then reports running', async () => {
    let up = false;
    const { sc, spawn } = make({
      probe: async () => up,
      sleep: async () => {
        up = true;
      },
      loc: { ...ready, sourceDir: 'BUNDLED' },
    });
    const s = await sc.ensure();
    expect(s.phase).toBe('running');
    expect(s.managed).toBe(true);
    const [py, args, opts] = spawn.mock.calls[0] as [string, string[], { cwd: string; env: Record<string, string> }];
    expect(py).toBe('py.exe');
    expect(args).toEqual(['-m', 'mazhost']);
    expect(opts.cwd).toBe('I');
    expect(opts.env.PYTHONPATH).toBe('BUNDLED');
  });

  it('shares one attempt between concurrent ensure() calls', async () => {
    let up = false;
    const { sc, spawn } = make({
      probe: async () => up,
      sleep: async () => {
        up = true;
      },
    });
    await Promise.all([sc.ensure(), sc.ensure(), sc.ensure()]);
    expect(spawn).toHaveBeenCalledTimes(1);
  });

  it('explains missing Python instead of failing silently', async () => {
    const { sc, spawn } = make({ loc: { ...ready, python: null }, hasSystemPython: () => false });
    const s = await sc.ensure();
    expect(s.phase).toBe('no-python');
    expect(s.message).toMatch(/Python/);
    expect(spawn).not.toHaveBeenCalled();
  });

  it('offers setup when Core is not installed but Python exists', async () => {
    const { sc } = make({ loc: { ...ready, python: null, sourceDir: null } });
    expect((await sc.ensure()).phase).toBe('not-installed');
  });

  it('asks for setup when the token or .env is missing', async () => {
    const { sc } = make({ hasToken: () => false });
    expect((await sc.ensure()).phase).toBe('needs-setup');
  });

  it('fails clearly, with the log tail, when Core never answers', async () => {
    const { sc, child } = make({ startTimeoutMs: 1000, logTail: () => 'ModuleNotFoundError: fastapi' });
    const s = await sc.ensure();
    expect(s.phase).toBe('failed');
    expect(s.detail).toContain('fastapi');
    expect(child.kill).toHaveBeenCalled();
  });

  it('detects a crash right after launch', async () => {
    const holder: { exit?: () => void } = {};
    const { sc, child } = make({
      startTimeoutMs: 5000,
      sleep: async () => {
        holder.exit?.();
      },
    });
    holder.exit = () => child.exitCb?.(1);
    const s = await sc.ensure();
    expect(s.phase).toBe('failed');
  });

  it('stop() kills only the child it launched', async () => {
    let up = false;
    const { sc, child } = make({
      probe: async () => up,
      sleep: async () => {
        up = true;
      },
    });
    await sc.ensure();
    sc.stop();
    expect(child.kill).toHaveBeenCalledTimes(1);
    expect(sc.isManaged).toBe(false);
  });
});
