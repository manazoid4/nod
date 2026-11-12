import { useState } from 'react';
import { useStore } from '../lib/store';
import { Icon, Spinner } from './ui';

/** Shown instead of a section when Core is not running. Always says what is wrong and offers the next step. */
export function CoreGate() {
  const { core, toast } = useStore();
  const [busy, setBusy] = useState(false);
  if (!core) return null;

  const run = async (fn: () => Promise<unknown>) => {
    setBusy(true);
    try {
      await fn();
    } finally {
      setBusy(false);
    }
  };
  const install = () =>
    run(async () => {
      const r = await window.piblo.core.install();
      toast(r.message, !r.ok);
    });
  const again = () => run(() => window.piblo.core.ensure());

  if (core.phase === 'checking' || core.phase === 'starting') {
    return (
      <div className="gate" role="status">
        <Spinner />
        <h1>{core.phase === 'starting' ? 'Starting Piblo on this PC' : 'Looking for Piblo on this PC'}</h1>
        <p className="meta">This usually takes a few seconds.</p>
      </div>
    );
  }

  const copy: Record<string, { title: string; body: string }> = {
    'not-installed': { title: 'Piblo on this PC is not set up yet', body: 'It is the small background service that connects this app to your Piblo. Setting it up takes a couple of minutes and runs on this PC only.' },
    'no-python': { title: 'Python is needed first', body: 'Piblo runs on Python 3.11 or newer, which is not installed on this PC. Install it once, then come back.' },
    'needs-setup': { title: 'Finish setting up Piblo on this PC', body: 'It is installed but its settings file is missing, so it cannot start. Run setup to create it.' },
    outdated: { title: 'Piblo on this PC needs updating', body: 'The copy on this PC is older than this app expects, so some features would fail. Update it to continue.' },
    'token-mismatch': { title: 'The saved key was rejected', body: 'Piblo on this PC is running but does not accept the key this app has saved.' },
    failed: { title: 'Piblo on this PC would not start', body: core.message },
  };
  const c = copy[core.phase] ?? copy.failed;

  return (
    <div className="gate">
      <div className="gate-icon">
        <Icon name={core.phase === 'failed' ? 'warn' : 'plug'} size={30} />
      </div>
      <h1>{c.title}</h1>
      <p>{c.body}</p>
      {core.detail && <p className="meta selectable">{core.detail}</p>}
      <div className="row wrap" style={{ justifyContent: 'center' }}>
        {(core.phase === 'not-installed' || core.phase === 'needs-setup' || core.phase === 'outdated') && (
          <button className="btn primary" disabled={busy} onClick={install}>
            {core.phase === 'needs-setup' || core.phase === 'outdated' ? (core.phase === 'outdated' ? 'Update' : 'Run setup') : 'Set up Piblo'}
          </button>
        )}
        {core.phase === 'no-python' && (
          <button className="btn primary" onClick={() => void window.piblo.openExternal('https://www.python.org/downloads/windows/')}>
            Get Python
          </button>
        )}
        {core.phase === 'failed' && (
          <button className="btn" onClick={() => void window.piblo.core.openLogs()}>
            Open log
          </button>
        )}
        <button className={core.phase === 'failed' ? 'btn primary' : 'btn'} disabled={busy} onClick={again}>
          <Icon name="refresh" size={16} /> {core.phase === 'failed' ? 'Try again' : 'Check again'}
        </button>
      </div>
    </div>
  );
}
