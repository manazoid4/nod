import { useEffect, useState } from 'react';
import iconUrl from './assets/piblo-icon.svg';
import { PairingList } from './components/PairingCard';
import { CoreGate } from './components/CoreGate';
import { Icon } from './components/ui';
import { usePairing } from './lib/usePairing';
import { Actions } from './pages/Actions';
import { Ask } from './pages/Ask';
import { Home } from './pages/Home';
import { LiveView } from './pages/LiveView';
import { Memory } from './pages/Memory';
import { Onboarding } from './pages/Onboarding';
import { Settings } from './pages/Settings';
import { StoreProvider, usePoll, useStore } from './lib/store';

type Section = 'home' | 'live' | 'ask' | 'memory' | 'actions' | 'settings';
const NAV: { id: Section; label: string; icon: string }[] = [
  { id: 'home', label: 'Home', icon: 'device' },
  { id: 'live', label: 'Live View', icon: 'screen' },
  { id: 'ask', label: 'Ask', icon: 'ask' },
  { id: 'memory', label: 'Memory', icon: 'memory' },
  { id: 'actions', label: 'Actions', icon: 'actions' },
  { id: 'settings', label: 'Settings', icon: 'settings' },
];

function DevicePillView() {
  const { pill } = useStore();
  const cls = pill.state === 'connected' ? 'ok' : pill.state === 'pairing' ? 'warn' : '';
  return (
    <div className={`pill ${cls}`} role="status" aria-label={`Device ${pill.label}`}>
      <span className="dot" />
      {pill.label}
      {pill.battery !== null && <span>{pill.battery}%</span>}
      {pill.firmware && <span className="meta">{pill.firmware}</span>}
    </div>
  );
}

function Shell() {
  const { core, toastNow } = useStore();
  const [section, setSection] = useState<Section>('home');
  const [welcome, setWelcome] = useState<boolean | null>(null);
  const needs = usePoll<{ items: { tier: string }[] }>('/needs', 15000);
  const badge = (needs.data?.items ?? []).filter((n) => n.tier !== 'approvals').length;
  const running = core?.phase === 'running';
  // Pending pairing requests, polled every 2 s while this window is open.
  const pairing = usePairing({ active: running });
  const [notice, setNotice] = useState<string | null>(null);
  const showPairing = !welcome && pairing.requests.length > 0;

  useEffect(() => {
    void window.piblo.settings.get().then((s) => setWelcome(!s.onboardingDone));
    const onHash = () => location.hash === '#/welcome' && setWelcome(true);
    window.addEventListener('hashchange', onHash);
    // Clicking the tray notification means "show me the card"; Settings holds one.
    const off = window.piblo.onPairingOpen(() => {
      setSection('settings');
      setWelcome(false);
    });
    return () => {
      window.removeEventListener('hashchange', onHash);
      off();
    };
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!e.ctrlKey || e.altKey || e.shiftKey) return;
      const n = Number(e.key);
      if (n >= 1 && n <= NAV.length) {
        e.preventDefault();
        setSection(NAV[n - 1].id);
        setWelcome(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const decide = async (requestId: string, decision: 'allow' | 'deny') => {
    const out = await pairing.decide(requestId, decision);
    setNotice(out.message);
    if (out.ok && decision === 'allow') {
      setWelcome(false);
      setSection('live');
    }
    window.setTimeout(() => setNotice(null), 6000);
  };

  const needsCore = section !== 'settings' && !running;
  const Page = { home: Home, live: LiveView, ask: Ask, memory: Memory, actions: Actions, settings: Settings }[section];

  return (
    <div className="shell">
      <header className="titlebar">
        <div className="brand">
          <img className="brand-icon" src={iconUrl} alt="" aria-hidden="true" />
          Piblo
        </div>
        <span className="spacer" />
        <DevicePillView />
      </header>
      <nav className="rail" aria-label="Sections">
        {NAV.map((n, i) => (
          <button
            key={n.id}
            className="rail-item"
            aria-current={!welcome && section === n.id ? 'page' : undefined}
            onClick={() => {
              setSection(n.id);
              setWelcome(false);
            }}
          >
            <Icon name={n.icon} />
            {n.label}
            {n.id === 'actions' && badge > 0 ? <span className="rail-badge" aria-label={`${badge} waiting`}>{badge}</span> : <kbd>Ctrl+{i + 1}</kbd>}
          </button>
        ))}
        <div className="rail-foot meta">{running ? (core?.managed ? 'Piblo on this PC: running' : 'Piblo on this PC: already running') : ''}</div>
      </nav>
      <main className="content">
        {welcome === null ? null : welcome ? (
          <Onboarding onDone={() => { setWelcome(false); location.hash = ''; setSection('live'); }} />
        ) : needsCore ? (
          <CoreGate />
        ) : (
          <>
            {showPairing && <PairingList requests={pairing.requests} busy={pairing.busy} notice={notice} onDecide={(id, d) => void decide(id, d)} />}
            <Page />
          </>
        )}
      </main>
      {toastNow && <div className={`toast ${toastNow.bad ? 'bad' : ''}`} role="status">{toastNow.text}</div>}
    </div>
  );
}

export function App() {
  return (
    <StoreProvider>
      <Shell />
    </StoreProvider>
  );
}
