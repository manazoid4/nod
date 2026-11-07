import { useEffect, useState } from 'react';
import { CoreGate } from './components/CoreGate';
import { Icon } from './components/ui';
import { Actions } from './pages/Actions';
import { Ask } from './pages/Ask';
import { Memory } from './pages/Memory';
import { MyNod } from './pages/MyNod';
import { Onboarding } from './pages/Onboarding';
import { Settings } from './pages/Settings';
import { StoreProvider, usePoll, useStore } from './lib/store';

type Section = 'nod' | 'ask' | 'memory' | 'actions' | 'settings';
const NAV: { id: Section; label: string; icon: string }[] = [
  { id: 'nod', label: 'My Nod', icon: 'device' },
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
  const { core, health, toastNow } = useStore();
  const [section, setSection] = useState<Section>('nod');
  const [welcome, setWelcome] = useState<boolean | null>(null);
  const needs = usePoll<{ items: { tier: string }[] }>('/needs', 15000);
  const badge = (needs.data?.items ?? []).filter((n) => n.tier !== 'approvals').length;

  useEffect(() => {
    void window.nod.settings.get().then((s) => setWelcome(!s.onboardingDone));
    const onHash = () => location.hash === '#/welcome' && setWelcome(true);
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
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

  const needsCore = section !== 'settings' && core?.phase !== 'running';
  const Page = { nod: MyNod, ask: Ask, memory: Memory, actions: Actions, settings: Settings }[section];

  return (
    <div className="shell">
      <header className="titlebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">N</span>
          Nod Core
        </div>
        <span className="spacer" />
        <DevicePillView />
        {health?.version && <span className="meta">Core v{health.version}</span>}
      </header>
      <nav className="rail" aria-label="Sections">
        {NAV.map((n, i) => (
          <button key={n.id} className="rail-item" aria-current={!welcome && section === n.id ? 'page' : undefined} onClick={() => { setSection(n.id); setWelcome(false); }}>
            <Icon name={n.icon} />
            {n.label}
            {n.id === 'actions' && badge > 0 ? <span className="rail-badge" aria-label={`${badge} waiting`}>{badge}</span> : <kbd>Ctrl+{i + 1}</kbd>}
          </button>
        ))}
        <div className="rail-foot meta">{core?.managed ? 'Core started by this app' : core?.phase === 'running' ? 'Core already running' : ''}</div>
      </nav>
      <main className="content">
        {welcome === null ? null : welcome ? (
          <Onboarding onDone={() => { setWelcome(false); location.hash = ''; }} />
        ) : needsCore ? (
          <CoreGate />
        ) : (
          <Page />
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
