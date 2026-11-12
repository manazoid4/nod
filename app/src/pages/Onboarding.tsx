import { useState } from 'react';
import { CoreGate } from '../components/CoreGate';
import { PairingList } from '../components/PairingCard';
import { Icon } from '../components/ui';
import { onboardingSteps } from '../lib/logic';
import { usePairing } from '../lib/usePairing';
import { useStore } from '../lib/store';

/**
 * First run: Piblo on this PC, then "Piblo wants to connect" (compare the code, press Allow),
 * then Live View. Nothing is typed and nothing is approved without the person pressing Allow.
 */
export function Onboarding({ onDone }: { onDone(): void }) {
  const { core, toast } = useStore();
  const running = core?.phase === 'running';
  const pairing = usePairing({ active: running });
  const [connected, setConnected] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const steps = onboardingSteps({ core, connected, pending: pairing.requests.length });
  const current = steps.findIndex((s) => !s.done);

  const decide = async (requestId: string, decision: 'allow' | 'deny') => {
    const out = await pairing.decide(requestId, decision);
    setNotice(out.message);
    if (out.ok && decision === 'allow') {
      setConnected(true);
      await window.piblo.settings.set({ onboardingDone: true });
      toast('Connected');
    }
  };
  const skip = async () => {
    await window.piblo.settings.set({ onboardingDone: true });
    onDone();
  };

  return (
    <div className="onboard">
      <div>
        <h1 style={{ fontSize: 'var(--text-2xl)', letterSpacing: '-0.02em' }}>Welcome to Piblo</h1>
        <p style={{ color: 'var(--text-2)' }}>Two steps, then you can see and use your Piblo from this PC.</p>
      </div>

      {core && !running ? <CoreGate /> : null}

      {steps.map((s, i) => {
        const state = s.done ? 'done' : i === current ? 'active' : 'future';
        return (
          <div key={s.title} className={`step ${state}`} aria-current={state === 'active' ? 'step' : undefined}>
            <div className="step-mark">{s.done ? <Icon name="check" size={18} /> : i + 1}</div>
            <div className="grow">
              <h3>{s.title}</h3>
              <p>{s.hint}</p>
              {i === 1 && state === 'active' && (
                <div className="actions">
                  {pairing.requests.length ? (
                    <PairingList requests={pairing.requests} busy={pairing.busy} notice={notice} onDecide={(id, d) => void decide(id, d)} />
                  ) : (
                    <p className="meta">Waiting for Piblo to ask. Keep this window open.</p>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}

      <div className="row">
        <button className="btn ghost" onClick={skip}>Skip for now</button>
        <span className="grow" />
        {connected && <button className="btn primary" onClick={onDone}>Open Live View</button>}
      </div>
    </div>
  );
}
