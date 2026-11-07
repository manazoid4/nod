import { useEffect, useRef, useState } from 'react';
import { Empty, Icon, PageHead } from '../components/ui';
import { ago, decodeRgb565, keyAction, SCREEN_H, SCREEN_W } from '../lib/logic';
import { useAct, usePoll, useStore } from '../lib/store';

interface Beam {
  messages?: { id: string; text: string; direction: string; created: number }[];
}

function LiveScreen({ online }: { online: boolean }) {
  const ref = useRef<HTMLCanvasElement>(null);
  const [stale, setStale] = useState(false);
  const act = useAct();

  useEffect(() => {
    if (!online) return;
    let live = true;
    let busy = false;
    const draw = async () => {
      if (busy || document.hidden) return;
      busy = true;
      const r = await window.nod.screen();
      busy = false;
      if (!live) return;
      const rgba = r.ok ? decodeRgb565(r.data) : null;
      setStale(!rgba);
      const ctx = ref.current?.getContext('2d');
      if (rgba && ctx) ctx.putImageData(new ImageData(rgba, SCREEN_W, SCREEN_H), 0, 0);
    };
    void draw();
    const id = window.setInterval(draw, 1000);
    return () => {
      live = false;
      window.clearInterval(id);
    };
  }, [online]);

  const onKey = (e: React.KeyboardEvent) => {
    if (e.metaKey) return;
    const a = keyAction(e);
    if (!a) return;
    e.preventDefault();
    e.stopPropagation();
    void act('POST', '/core/cardputer/action', { action: a });
  };

  return (
    <div className="screen-wrap">
      <canvas
        ref={ref}
        className="screen"
        width={SCREEN_W}
        height={SCREEN_H}
        tabIndex={online ? 0 : -1}
        aria-label="Live mirror of your Nod screen. Focus it and type to send keys."
        onKeyDown={onKey}
        style={{ opacity: online && !stale ? 1 : 0.25 }}
      />
      {(!online || stale) && (
        <p className="meta" style={{ position: 'absolute' }}>
          {online ? 'Waiting for a frame...' : 'Screen appears here when your Nod is connected'}
        </p>
      )}
    </div>
  );
}

const KEYS: [string, string][] = [
  ['Esc', 'key:41,0,0'],
  ['Up', 'key:82,0,0'],
  ['Down', 'key:81,0,0'],
  ['Left', 'key:80,0,0'],
  ['Right', 'key:79,0,0'],
  ['Tab', 'key:43,0,0'],
  ['Enter', 'key:40,0,0'],
  ['Back', 'key:42,0,0'],
];

export function MyNod() {
  const { deviceInfo, pill, core, toast, refreshDevice, health } = useStore();
  const act = useAct();
  const online = pill.state === 'connected';
  const beam = usePoll<Beam>('/beam/history?limit=6', 6000);
  const [note, setNote] = useState('');
  const [checking, setChecking] = useState(false);
  const dev = deviceInfo?.device;
  const hub = deviceInfo?.hub_fw;

  const send = async () => {
    if (!note.trim()) return;
    const r = await act('POST', '/beam/to-pocket', { text: note.trim() }, 'Sent to your Nod');
    if (r.ok) {
      setNote('');
      beam.reload();
    }
  };
  const check = async () => {
    setChecking(true);
    const r = await act('POST', '/core/update/check', undefined, 'Checked for updates');
    setChecking(false);
    if (r.ok) refreshDevice();
  };
  const install = async () => {
    if (!window.confirm(`Install ${hub?.version ?? 'the new build'} on your Nod? It restarts when done. Keep it on Wi-Fi with 30%+ battery or charging.`)) return;
    const r = await act('POST', '/core/cardputer/action', { action: 'update' });
    if (r.ok) toast('Update started. Your Nod restarts when it finishes.');
  };

  return (
    <div className="page">
      <PageHead title="My Nod" sub={online ? 'Your Nod is connected.' : 'Plug in or power on your Nod and it will show up here.'} />
      <div className="nod-top">
        <LiveScreen online={online} />
        <div className="stack">
        <section className="card stack" aria-labelledby="dev-h">
          <h2 id="dev-h">Device</h2>
          {online && dev ? (
            <>
              <div className="row">
                <span className="grow">Battery</span>
                <div className={`battery ${typeof dev.battery === 'number' && dev.battery >= 0 && dev.battery < 20 ? 'low' : ''}`}>
                  <i style={{ width: `${Math.max(0, Math.min(100, dev.battery ?? 0))}%` }} />
                </div>
                <span className="meta" style={{ width: 36, textAlign: 'right' }}>{pill.battery !== null ? `${pill.battery}%` : '?'}</span>
              </div>
              <div className="row"><span className="grow">Firmware</span><span className="tag">{pill.firmware || 'unknown'}</span></div>
              <div className="row"><span className="grow">Current screen</span><span className="tag">{dev.app || 'unknown'}</span></div>
            </>
          ) : (
            <Empty title="Not connected">
              <p>{core?.phase === 'running' ? 'Core cannot reach your Nod. Check it is on and on the same Wi-Fi.' : 'Start Nod Core to see your device.'}</p>
            </Empty>
          )}
        </section>

        <section className="card stack" aria-labelledby="fw-h">
          <h2 id="fw-h">Firmware</h2>
          <p className="sub">
            {hub ? `Core has v${hub.version ?? '?'} ready.` : 'No firmware staged on this PC.'}{' '}
            {online && hub ? (deviceInfo?.update_available ? 'It is newer than your Nod.' : 'Your Nod is up to date.') : ''}
          </p>
          {health?.fw_latest?.version && <span className="meta">Latest known: v{health.fw_latest.version}</span>}
          {deviceInfo?.last_report?.stage && (
            <span className="meta">
              Last update: {deviceInfo.last_report.stage}
              {deviceInfo.last_report.error ? ` (${deviceInfo.last_report.error})` : ''}
            </span>
          )}
          <div className="row wrap">
            <button className="btn" onClick={check} disabled={checking}><Icon name="refresh" size={16} /> Check for updates</button>
            <button className="btn primary" onClick={install} disabled={!online || !deviceInfo?.update_available}>Install update</button>
          </div>
        </section>
        </div>
      </div>

      <section className="card stack" aria-labelledby="keys-h">
        <h2 id="keys-h">Remote keys</h2>
        <p className="sub">Click the screen and type, or use the buttons.</p>
        <div className="keys">
          {KEYS.map(([label, action]) => (
            <button key={label} className="btn sm" disabled={!online} onClick={() => void act('POST', '/core/cardputer/action', { action })}>{label}</button>
          ))}
          <button className="btn sm" disabled={!online} onClick={() => window.confirm('Restart your Nod?') && void act('POST', '/core/cardputer/action', { action: 'reboot' }, 'Restarting your Nod')}>Reboot</button>
        </div>
      </section>

      <section className="card stack" aria-labelledby="beam-h">
        <h2 id="beam-h">Send to Nod</h2>
        <p className="sub">Beam a note or link to your Nod. It appears the next time the device checks in.</p>
        <div className="row">
          <input className="input" placeholder="Type a note or paste a link" value={note} onChange={(e) => setNote(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && void send()} maxLength={2000} aria-label="Note to send" />
          <button className="btn primary" onClick={send} disabled={!note.trim()}><Icon name="send" size={16} /> Send</button>
        </div>
        <div className="list">
          {(beam.data?.messages ?? []).map((m) => (
            <div className="list-item" key={m.id}>
              <span className="tag">{m.direction === 'to_pocket' ? 'to Nod' : 'from Nod'}</span>
              <span className="grow detail selectable">{m.text}</span>
              <span className="meta">{ago(Math.max(0, Date.now() / 1000 - m.created))}</span>
            </div>
          ))}
          {!beam.loading && !(beam.data?.messages ?? []).length && <p className="meta">Nothing beamed yet.</p>}
        </div>
      </section>
    </div>
  );
}
