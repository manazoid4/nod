import { useEffect, useRef, useState } from 'react';
import { Icon, PageHead } from '../components/ui';
import { useAct, usePoll, useStore } from '../lib/store';

type Route = 'local' | 'auto' | 'cloud';
interface Msg {
  me: boolean;
  text: string;
  note?: string;
}
interface Models {
  local?: boolean;
  local_model?: string;
  local_model_installed?: boolean;
  local_engine?: string;
  backup_model?: string;
  default_route?: string;
  last_route?: { provider?: string; model?: string };
  ai_profile?: string;
}
interface Voices {
  current?: string;
  current_name?: string;
  voices?: { name: string; reference_id: string; description?: string; current?: boolean }[];
}

// Conversation survives switching sections; it is gone when the app quits (nothing is saved to disk by the app).
const kept: { msgs: Msg[]; session: string | null; route: Route } = { msgs: [], session: null, route: 'local' };

export function Ask() {
  const act = useAct();
  const { core, toast } = useStore();
  const [msgs, setMsgs] = useState<Msg[]>(kept.msgs);
  const [route, setRoute] = useState<Route>(kept.route);
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const models = usePoll<Models>('/models', 15000);
  const voices = usePoll<Voices>('/voices', 0);
  const end = useRef<HTMLDivElement>(null);

  useEffect(() => {
    kept.msgs = msgs;
    kept.route = route;
    end.current?.scrollIntoView({ block: 'end' });
  }, [msgs, route]);

  const send = async () => {
    const t = text.trim();
    if (!t || busy) return;
    setText('');
    setMsgs((m) => [...m, { me: true, text: t }]);
    setBusy(true);
    if (!kept.session) {
      const s = await act<{ session_id: string }>('POST', '/session/start');
      if (!s.ok) {
        setBusy(false);
        return;
      }
      kept.session = s.data.session_id;
    }
    const r = await act<{ reply?: string; provider?: string }>('POST', '/turn/text', { text: t, session_id: kept.session, route });
    if (!r.ok && r.status === 404) kept.session = null; // session expired: next send starts a new one
    setMsgs((m) => [...m, r.ok ? { me: false, text: r.data.reply || '(no reply)', note: r.data.provider } : { me: false, text: r.message, note: 'error' }]);
    setBusy(false);
  };

  const newChat = () => {
    if (kept.session) void window.piblo.api('POST', `/session/end?session_id=${encodeURIComponent(kept.session)}`);
    kept.session = null;
    setMsgs([]);
  };

  const pickVoice = async (id: string, name: string) => {
    const r = await act('POST', '/voices/select', { reference_id: id, name }, `Voice set to ${name}`);
    if (r.ok) voices.reload();
  };
  const preview = async (id: string) => {
    const r = await window.piblo.audio('/voices/preview', { reference_id: id });
    if (!r.ok) return toast(r.message, true);
    void new Audio(URL.createObjectURL(new Blob([new Uint8Array(r.data)]))).play();
  };

  const m = models.data;
  return (
    <div className="page">
      <PageHead
        title="Ask"
        sub="Talk to the same brain your Piblo uses."
        right={<button className="btn" onClick={newChat} disabled={!msgs.length}>New conversation</button>}
      />
      <section className="card stack" aria-label="Conversation">
        <div className="chat" aria-live="polite">
          {!msgs.length && <p className="meta">Ask anything. Try: "What should I focus on today?"</p>}
          {msgs.map((x, i) => (
            <div key={i} className={`bubble ${x.me ? 'me' : ''}`}>
              {x.text}
              {x.note && <small>{x.note}</small>}
            </div>
          ))}
          {busy && <div className="bubble"><span className="spinner" style={{ display: 'inline-block' }} /></div>}
          <div ref={end} />
        </div>
        <div className="row">
          <textarea
            className="input grow"
            rows={2}
            placeholder="Ask Piblo anything"
            value={text}
            maxLength={8000}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                void send();
              }
            }}
            aria-label="Message"
            disabled={core?.phase !== 'running'}
          />
          <button className="btn primary" onClick={send} disabled={!text.trim() || busy}><Icon name="send" size={16} /> Send</button>
        </div>
        <div className="row">
          <span className="meta">Brain for this chat</span>
          <div className="seg" role="group" aria-label="Brain">
            {(['local', 'auto', 'cloud'] as Route[]).map((r) => (
              <button key={r} aria-pressed={route === r} onClick={() => setRoute(r)}>{r === 'local' ? 'On this PC' : r === 'auto' ? 'Auto' : 'Cloud'}</button>
            ))}
          </div>
        </div>
      </section>

      <div className="grid-2">
        <section className="card stack" aria-labelledby="model-h">
          <h2 id="model-h">Model</h2>
          <div className="row"><span className="grow">Local engine</span><span className="tag">{m?.local_engine ?? '...'}</span></div>
          <div className="row"><span className="grow">Local model</span><span className="tag">{m?.local_model ?? '...'}</span></div>
          <div className="row">
            <span className="grow">Status</span>
            <span className={`pill ${m?.local && m.local_model_installed ? 'ok' : 'warn'}`}><span className="dot" />{m ? (m.local ? (m.local_model_installed ? 'Ready' : 'Model not installed') : 'Engine not running') : '...'}</span>
          </div>
          <div className="row"><span className="grow">Default route</span><span className="tag">{m?.default_route ?? '...'}</span></div>
          {m?.last_route?.provider && <div className="row"><span className="grow">Last answer from</span><span className="tag">{m.last_route.provider}</span></div>}
          <p className="meta">Change the default route and add API keys in Settings.</p>
        </section>

        <section className="card stack" aria-labelledby="voice-h">
          <h2 id="voice-h">Voice</h2>
          <p className="sub">The voice your Piblo speaks with. {voices.data?.current_name ? `Now: ${voices.data.current_name}.` : ''}</p>
          {voices.error && <p className="meta">{voices.error}</p>}
          <div className="list">
            {(voices.data?.voices ?? []).slice(0, 6).map((v) => (
              <div className="list-item" key={v.reference_id}>
                <div className="grow">
                  <div className="title">{v.name}</div>
                  {v.description && <div className="detail">{v.description}</div>}
                </div>
                <button className="btn sm ghost" onClick={() => preview(v.reference_id)}>Preview</button>
                <button className="btn sm" disabled={v.current} onClick={() => void pickVoice(v.reference_id, v.name)}>{v.current ? 'In use' : 'Use'}</button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
