import { useEffect, useState } from 'react';
import { CoreGate } from '../components/CoreGate';
import { Icon } from '../components/ui';
import { onboardingSteps } from '../lib/logic';
import { useAct, usePoll, useStore } from '../lib/store';

interface Beam {
  messages?: { id: string }[];
}

/** First run: Connect Nod, Pair, Try your first action, See the result. Each tick comes from the API, not from a click. */
export function Onboarding({ onDone }: { onDone(): void }) {
  const { core, deviceInfo, setPairing, pairing, refreshDevice, toast } = useStore();
  const act = useAct();
  const [paired, setPaired] = useState(false);
  const [sentId, setSentId] = useState<string | null>(null);
  const [pairErr, setPairErr] = useState<string | null>(null);
  const history = usePoll<Beam>(sentId ? '/beam/history?limit=10' : null, 2000);

  const steps = onboardingSteps({ core, info: deviceInfo, paired, sentId, historyIds: (history.data?.messages ?? []).map((m) => m.id) });
  const current = steps.findIndex((s) => !s.done);
  const allDone = current === -1;

  useEffect(() => {
    if (core?.phase === 'running') refreshDevice();
  }, [core?.phase, refreshDevice]);

  const pair = async () => {
    setPairing(true);
    setPairErr(null);
    const r = await window.nod.device.pair();
    setPairing(false);
    if (r.ok) setPaired(true);
    else setPairErr(r.message);
    refreshDevice();
  };
  const send = async () => {
    const r = await act<{ message?: { id: string } }>('POST', '/beam/to-pocket', { text: 'Hello from Nod Core' });
    if (r.ok && r.data.message?.id) setSentId(r.data.message.id);
  };
  const finish = async () => {
    await window.nod.settings.set({ onboardingDone: true });
    toast('You are all set');
    onDone();
  };
  const skip = async () => {
    await window.nod.settings.set({ onboardingDone: true });
    onDone();
  };

  const rows = [
    {
      title: 'Connect your Nod',
      body: steps[0].hint,
      action:
        core?.phase !== 'running' ? null : (
          <button className="btn" onClick={refreshDevice}><Icon name="refresh" size={16} /> Check again</button>
        ),
    },
    {
      title: 'Pair it with this PC',
      body: pairErr ?? steps[1].hint,
      action: <button className="btn primary" onClick={pair} disabled={pairing || core?.phase !== 'running'}>{pairing ? 'Pairing...' : pairErr ? 'Try pairing again' : 'Pair over USB'}</button>,
    },
    {
      title: 'Try your first action',
      body: steps[2].hint,
      action: <button className="btn primary" onClick={send} disabled={core?.phase !== 'running'}><Icon name="send" size={16} /> Send "Hello" to my Nod</button>,
    },
    { title: 'See the result', body: steps[3].hint, action: null },
  ];

  return (
    <div className="onboard">
      <div>
        <h1 style={{ fontSize: 'var(--text-2xl)', letterSpacing: '-0.02em' }}>Welcome to Nod Core</h1>
        <p style={{ color: 'var(--text-2)' }}>Four quick steps to get your Nod talking to this PC.</p>
      </div>

      {core && core.phase !== 'running' && <CoreGate />}

      {core?.phase === 'running' &&
        rows.map((r, i) => {
          const s = steps[i];
          const state = s.done ? 'done' : i === current ? 'active' : 'future';
          return (
            <div key={r.title} className={`step ${state}`} aria-current={state === 'active' ? 'step' : undefined}>
              <div className="step-mark">{s.done ? <Icon name="check" size={18} /> : i + 1}</div>
              <div className="grow">
                <h3>{r.title}</h3>
                <p>{r.body}</p>
                {state === 'active' && r.action && <div className="actions">{r.action}</div>}
              </div>
            </div>
          );
        })}

      <div className="row">
        <button className="btn ghost" onClick={skip}>Skip for now</button>
        <span className="grow" />
        {allDone && <button className="btn primary" onClick={finish}>Open Nod Core</button>}
      </div>
    </div>
  );
}
