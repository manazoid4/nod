import { useEffect, useState } from 'react';
import { Banner, Empty, Icon, PageHead } from '../components/ui';
import {
  CHECKLIST_LABELS,
  clampPercent,
  formatTickedTime,
  prCheckSummary,
  usageTone,
  X_CHAR_LIMIT,
  xCounter,
  type DevChecklist,
  type DevChecklistItem,
  type DevDraft,
  type DevGithub,
  type DevOverview,
  type DevPr,
  type DevShare,
  type DevTarget,
  type DevUsage,
} from '../lib/dev';
import { useAct, usePoll } from '../lib/store';

export type DevTab = 'today' | 'checklists' | 'content' | 'agents' | 'builds';

const TABS: { id: DevTab; label: string }[] = [
  { id: 'today', label: 'Today' },
  { id: 'checklists', label: 'Checklists' },
  { id: 'content', label: 'Content Studio' },
  { id: 'agents', label: 'Agents' },
  { id: 'builds', label: 'Builds' },
];

export function DevTodayView({
  overview,
  checklists,
  error,
  onJump,
  onTick,
}: {
  overview: DevOverview | null;
  checklists: DevChecklist[];
  error?: string | null;
  onJump(tab: DevTab): void;
  onTick?(listId: string, itemId: string, done: boolean): void;
}) {
  if (error) {
    return <Banner kind="bad" title="Could not load Today overview">{error}</Banner>;
  }
  if (!overview) {
    return (
      <section className="card">
        <Empty title="Nothing loaded yet">
          <p>Waiting for Piblo Dev overview from this PC.</p>
        </Empty>
      </section>
    );
  }

  const founder = checklists.find((c) => c.id === 'founder-today');
  const nextItems = (founder?.items ?? []).filter((i) => !i.done).slice(0, 4);

  return (
    <div className="stack">
      <div className="grid-2">
        <section className="card stack" aria-labelledby="today-founder-h">
          <div className="row">
            <h2 id="today-founder-h" className="grow">Founder today</h2>
            <span className={`pill ${overview.founder_unticked === 0 ? 'ok' : ''}`}>
              <span className="dot" />
              {overview.founder_unticked} remaining
            </span>
          </div>
          <p className="sub">Key steps on your founder checklist today.</p>
          <div>
            <button type="button" className="btn" onClick={() => onJump('checklists')}>
              Open Checklists
            </button>
          </div>
        </section>

        <section className="card stack" aria-labelledby="today-content-h">
          <div className="row">
            <h2 id="today-content-h" className="grow">Content drafts</h2>
            <span className={`pill ${overview.drafts_awaiting_approval > 0 ? '' : 'ok'}`}>
              <span className="dot" />
              {overview.drafts_awaiting_approval} waiting
            </span>
          </div>
          <p className="sub">Drafts waiting for your review. Nothing ever posts by itself.</p>
          <div>
            <button type="button" className="btn" onClick={() => onJump('content')}>
              Open Content Studio
            </button>
          </div>
        </section>

        <section className="card stack" aria-labelledby="today-builds-h">
          <div className="row">
            <h2 id="today-builds-h" className="grow">Pull request checks</h2>
            <span className={`pill ${overview.failing_pr_checks > 0 ? 'bad' : 'ok'}`}>
              <span className="dot" />
              {overview.failing_pr_checks > 0 ? `${overview.failing_pr_checks} failing` : 'All clear'}
            </span>
          </div>
          <p className="sub">Open pull requests and automated checks.</p>
          <div>
            <button type="button" className="btn" onClick={() => onJump('builds')}>
              Open Builds
            </button>
          </div>
        </section>

        <section className="card stack" aria-labelledby="today-agents-h">
          <div className="row">
            <h2 id="today-agents-h" className="grow">Agent usage</h2>
            <span className={`pill ${overview.usage_warnings > 0 ? 'warn' : 'ok'}`}>
              <span className="dot" />
              {overview.usage_warnings > 0 ? `${overview.usage_warnings} above 80%` : 'Calm'}
            </span>
          </div>
          <p className="sub">Usage meters stay calm and turn amber only above 80%.</p>
          <div>
            <button type="button" className="btn" onClick={() => onJump('agents')}>
              Open Agents
            </button>
          </div>
        </section>
      </div>

      <section className="card stack" aria-labelledby="today-next-h">
        <div className="row">
          <h2 id="today-next-h" className="grow">What needs you now</h2>
          <button type="button" className="btn sm" onClick={() => onJump('checklists')}>
            See all checklists
          </button>
        </div>
        {nextItems.length ? (
          <div className="list">
            {nextItems.map((item) => (
              <div className="list-item" key={item.id}>
                <button
                  type="button"
                  className="tick-btn"
                  aria-label={`Tick ${item.text}`}
                  onClick={() => onTick?.('founder-today', item.id, true)}
                />
                <span className="grow title">{item.text}</span>
                <span className="tag">founder-today</span>
              </div>
            ))}
          </div>
        ) : (
          <Empty title="Founder checklist complete">
            <p>Every item on founder-today is ticked off.</p>
          </Empty>
        )}
      </section>
    </div>
  );
}

export function DevChecklistsView({
  lists,
  error,
  activeListId,
  onSelectList,
  onTick,
}: {
  lists: DevChecklist[];
  error?: string | null;
  activeListId: string;
  onSelectList(id: string): void;
  onTick(listId: string, item: DevChecklistItem, done: boolean, note?: string): void;
}) {
  const [notes, setNotes] = useState<Record<string, string>>({});

  if (error) {
    return <Banner kind="bad" title="Could not load checklists">{error}</Banner>;
  }
  if (!lists.length) {
    return (
      <section className="card">
        <Empty title="No checklists found">
          <p>Checklists will appear here once Core seeds them.</p>
        </Empty>
      </section>
    );
  }

  const current = lists.find((l) => l.id === activeListId) ?? lists[0];
  const meta = CHECKLIST_LABELS[current.id] ?? { title: current.id, sub: '' };
  const doneCount = current.items.filter((i) => i.done).length;

  return (
    <div className="stack">
      <div className="row wrap">
        <div className="seg" role="group" aria-label="Checklist selector">
          {lists.map((l) => {
            const label = CHECKLIST_LABELS[l.id]?.title ?? l.id;
            const d = l.items.filter((i) => i.done).length;
            return (
              <button
                key={l.id}
                type="button"
                aria-pressed={current.id === l.id}
                onClick={() => onSelectList(l.id)}
              >
                {label} ({d}/{l.items.length})
              </button>
            );
          })}
        </div>
        <span className="grow" />
        <span className="pill ok">
          <span className="dot" />
          {doneCount} of {current.items.length} ticked
        </span>
      </div>

      <section className="card stack" aria-labelledby="chk-title">
        <div>
          <h2 id="chk-title">{meta.title}</h2>
          {meta.sub && <p className="sub">{meta.sub}</p>}
        </div>

        {current.items.length ? (
          <div className="list">
            {current.items.map((item) => {
              const noteVal = notes[item.id] ?? item.note ?? '';
              const timeStr = formatTickedTime(item.when);
              return (
                <div className={`checklist-row ${item.done ? 'done' : ''}`} key={item.id}>
                  <button
                    type="button"
                    role="checkbox"
                    aria-checked={item.done}
                    aria-label={item.text}
                    className={`tick-box ${item.done ? 'checked' : ''}`}
                    onClick={() => onTick(current.id, item, !item.done, noteVal.trim() || undefined)}
                  >
                    {item.done && <Icon name="check" size={18} />}
                  </button>
                  <div className="grow stack" style={{ gap: 'var(--s-1)' }}>
                    <div className="row wrap">
                      <span className="title">{item.text}</span>
                      {item.done && <span className="tag">Ticked{timeStr ? ` ${timeStr}` : ''}</span>}
                    </div>
                    <div className="row wrap">
                      <input
                        className="input"
                        style={{ maxWidth: 360, height: 30, fontSize: 'var(--text-xs)' }}
                        placeholder="Optional note (e.g. tested on Wi-Fi)"
                        aria-label={`Note for ${item.text}`}
                        value={noteVal}
                        onChange={(e) => setNotes((prev) => ({ ...prev, [item.id]: e.target.value }))}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            onTick(current.id, item, true, noteVal.trim() || undefined);
                          }
                        }}
                      />
                      {item.note && <span className="meta">Saved note: {item.note}</span>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <Empty title="Empty checklist">
            <p>No items in this checklist yet.</p>
          </Empty>
        )}
      </section>
    </div>
  );
}

export function DevContentStudioView({
  drafts,
  error,
  sharesByDraft,
  onCreateFromFeature,
  onApprove,
  onMarkPosted,
  onOpenExternal,
}: {
  drafts: DevDraft[];
  error?: string | null;
  sharesByDraft: Record<string, DevShare[]>;
  onCreateFromFeature(feature: string, summary: string, clipPath?: string): void;
  onApprove(id: string): void;
  onMarkPosted(id: string): void;
  onOpenExternal(url: string): void;
}) {
  const [feature, setFeature] = useState('');
  const [summary, setSummary] = useState('');
  const [clip, setClip] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [platformTab, setPlatformTab] = useState<'reddit' | 'x' | 'linkedin' | 'instagram'>('reddit');

  if (error) {
    return <Banner kind="bad" title="Could not load Content Studio">{error}</Banner>;
  }

  const selected = drafts.find((d) => d.id === selectedId) ?? drafts[0] ?? null;
  const redditTargets = (selected?.targets ?? []).filter((t) => t.platform === 'reddit');
  const xTarget = (selected?.targets ?? []).find((t) => t.platform === 'x');
  const linkedinTarget = (selected?.targets ?? []).find((t) => t.platform === 'linkedin');
  const instagramTarget = (selected?.targets ?? []).find((t) => t.platform === 'instagram');

  const xText = xTarget?.body || selected?.body || '';
  const xStats = xCounter(xText);
  const linkedinText = linkedinTarget?.body || selected?.body || '';
  const instagramCaption = instagramTarget?.body || selected?.body || '';
  const shares = selected ? sharesByDraft[selected.id] ?? [] : [];

  const submitFeature = () => {
    if (!feature.trim() || !summary.trim()) return;
    onCreateFromFeature(feature.trim(), summary.trim(), clip.trim() || undefined);
    setFeature('');
    setSummary('');
    setClip('');
  };

  return (
    <div className="stack">
      <Banner kind="ok" title="Nothing ever posts by itself">
        You review every draft here first. Pressing Approve only opens the official share page in your browser so you stay in control.
      </Banner>

      <section className="card stack" aria-labelledby="new-feat-h">
        <h2 id="new-feat-h">New from feature</h2>
        <p className="sub">Turn a finished feature into tailored drafts for Reddit, X, LinkedIn and Instagram.</p>
        <div className="grid-2">
          <input
            className="input"
            placeholder="Feature name (e.g. Ask on Piblo)"
            aria-label="Feature name"
            value={feature}
            onChange={(e) => setFeature(e.target.value)}
          />
          <input
            className="input"
            placeholder="Optional clip file or note"
            aria-label="Optional clip"
            value={clip}
            onChange={(e) => setClip(e.target.value)}
          />
        </div>
        <textarea
          className="input"
          rows={3}
          placeholder="Short plain-English summary of what works now..."
          aria-label="Feature summary"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
        />
        <div className="row">
          <button
            type="button"
            className="btn primary"
            disabled={!feature.trim() || !summary.trim()}
            onClick={submitFeature}
          >
            New from feature
          </button>
        </div>
      </section>

      {!drafts.length ? (
        <section className="card">
          <Empty title="No drafts yet">
            <p>Use "New from feature" above to create your first set of platform previews.</p>
          </Empty>
        </section>
      ) : (
        <div className="home-top">
          <section className="card stack" aria-labelledby="draft-list-h">
            <h2 id="draft-list-h">Drafts ({drafts.length})</h2>
            <div className="list">
              {drafts.map((d) => (
                <div className="list-item" key={d.id}>
                  <button
                    type="button"
                    className={`btn ghost grow ${selected?.id === d.id ? 'active-draft' : ''}`}
                    style={{ justifyContent: 'flex-start', textAlign: 'left' }}
                    onClick={() => setSelectedId(d.id)}
                  >
                    <span className="grow title">{d.title}</span>
                  </button>
                  <span className={`pill ${d.status === 'posted' ? 'ok' : ''}`}>
                    <span className="dot" />
                    {d.status}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {selected && (
            <section className="card stack" aria-labelledby="preview-h">
              <div className="row wrap">
                <div className="grow">
                  <h2 id="preview-h">{selected.title}</h2>
                  <p className="sub">Nothing ever posts by itself. Approve opens the official share page in your browser.</p>
                </div>
                {selected.status === 'draft' && (
                  <button type="button" className="btn primary" onClick={() => onApprove(selected.id)}>
                    <Icon name="check" size={16} /> Approve
                  </button>
                )}
                {selected.status === 'approved' && (
                  <button type="button" className="btn" onClick={() => onMarkPosted(selected.id)}>
                    Mark posted
                  </button>
                )}
              </div>

              <div className="seg" role="group" aria-label="Platform preview">
                <button type="button" aria-pressed={platformTab === 'reddit'} onClick={() => setPlatformTab('reddit')}>
                  Reddit ({redditTargets.length})
                </button>
                <button type="button" aria-pressed={platformTab === 'x'} onClick={() => setPlatformTab('x')}>
                  X ({xStats.count}/{X_CHAR_LIMIT})
                </button>
                <button type="button" aria-pressed={platformTab === 'linkedin'} onClick={() => setPlatformTab('linkedin')}>
                  LinkedIn
                </button>
                <button type="button" aria-pressed={platformTab === 'instagram'} onClick={() => setPlatformTab('instagram')}>
                  Instagram
                </button>
              </div>

              {platformTab === 'reddit' && (
                <div className="stack">
                  {redditTargets.length ? (
                    redditTargets.map((t: DevTarget, idx: number) => {
                      const shareUrl = shares.find((s) => s.platform === 'reddit' && s.subreddit === t.subreddit)?.url;
                      return (
                        <div className="preview-box stack" key={`${t.subreddit ?? idx}`}>
                          <div className="row">
                            <span className="tag">r/{t.subreddit}</span>
                            <strong className="grow">{t.title || selected.title}</strong>
                            {shareUrl && (
                              <button type="button" className="btn sm" onClick={() => onOpenExternal(shareUrl)}>
                                Open share page
                              </button>
                            )}
                          </div>
                          <p className="detail selectable" style={{ whiteSpace: 'pre-wrap' }}>
                            {t.body || selected.body}
                          </p>
                        </div>
                      );
                    })
                  ) : (
                    <p className="meta">No Reddit targets on this draft.</p>
                  )}
                </div>
              )}

              {platformTab === 'x' && (
                <div className="preview-box stack">
                  <div className="row">
                    <span className="tag">X post</span>
                    <span className="grow" />
                    <span className={`pill ${xStats.over ? 'bad' : 'ok'}`}>
                      {xStats.count} / {X_CHAR_LIMIT} ({xStats.left} left)
                    </span>
                  </div>
                  <p className="detail selectable" style={{ whiteSpace: 'pre-wrap' }}>
                    {xText}
                  </p>
                  {shares.find((s) => s.platform === 'x')?.url && (
                    <div>
                      <button
                        type="button"
                        className="btn sm"
                        onClick={() => onOpenExternal(shares.find((s) => s.platform === 'x')!.url!)}
                      >
                        Open X share page
                      </button>
                    </div>
                  )}
                </div>
              )}

              {platformTab === 'linkedin' && (
                <div className="preview-box stack">
                  <div className="row">
                    <span className="tag">LinkedIn</span>
                    <span className="grow" />
                    {shares.find((s) => s.platform === 'linkedin')?.url && (
                      <button
                        type="button"
                        className="btn sm"
                        onClick={() => onOpenExternal(shares.find((s) => s.platform === 'linkedin')!.url!)}
                      >
                        Open LinkedIn share page
                      </button>
                    )}
                  </div>
                  <p className="detail selectable" style={{ whiteSpace: 'pre-wrap' }}>
                    {linkedinText}
                  </p>
                </div>
              )}

              {platformTab === 'instagram' && (
                <div className="preview-box stack">
                  <div className="row">
                    <span className="tag">Instagram caption</span>
                    {selected.media_path && <span className="meta">Clip: {selected.media_path}</span>}
                  </div>
                  <p className="detail selectable" style={{ whiteSpace: 'pre-wrap' }}>
                    {instagramCaption}
                  </p>
                </div>
              )}
            </section>
          )}
        </div>
      )}
    </div>
  );
}

function MeterRow({ label, window }: { label: string; window?: { used_percent?: number | null; resets_at?: string | null } }) {
  const pct = clampPercent(window?.used_percent);
  const tone = usageTone(window?.used_percent);
  return (
    <div className="stack" style={{ gap: 'var(--s-1)' }}>
      <div className="row">
        <span className="grow">{label}</span>
        <span className={`pill ${tone === 'amber' ? 'warn' : 'ok'}`}>
          <span className="dot" />
          {typeof window?.used_percent === 'number' ? `${pct}%` : 'Idle'}
        </span>
      </div>
      <div className={`usage-meter ${tone === 'amber' ? 'amber' : ''}`} role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <i style={{ width: `${pct}%` }} />
      </div>
      {window?.resets_at && <span className="meta">Resets: {window.resets_at}</span>}
    </div>
  );
}

export function DevAgentsView({ usage, error }: { usage: DevUsage | null; error?: string | null }) {
  if (error) {
    return <Banner kind="bad" title="Could not load agent usage">{error}</Banner>;
  }
  if (!usage) {
    return (
      <section className="card">
        <Empty title="No usage data yet">
          <p>Waiting for agent usage windows from this PC.</p>
        </Empty>
      </section>
    );
  }

  const claudeAccounts = usage.claude?.accounts ?? [];
  const codexAvailable = !!usage.codex?.available;

  return (
    <div className="stack">
      <p className="meta">Meters stay calm green and turn amber only above 80%.</p>
      <div className="grid-2">
        <section className="card stack" aria-labelledby="ag-claude-h">
          <div className="row">
            <h2 id="ag-claude-h" className="grow">Claude</h2>
            <span className={`pill ${usage.claude?.available ? 'ok' : ''}`}>
              <span className="dot" />
              {usage.claude?.available ? 'Connected' : 'Not detected'}
            </span>
          </div>
          {claudeAccounts.length ? (
            claudeAccounts.map((acc, i) => (
              <div className="stack" key={String(acc.number ?? i)}>
                <strong style={{ fontSize: 'var(--text-sm)' }}>Account {acc.number ?? i + 1}</strong>
                <MeterRow label="5-hour window" window={acc.five_hour} />
                <MeterRow label="7-day window" window={acc.seven_day} />
              </div>
            ))
          ) : (
            <Empty title="No Claude quota data">
              <p>Local quota helper is not reporting active accounts on this PC.</p>
            </Empty>
          )}
        </section>

        <section className="card stack" aria-labelledby="ag-codex-h">
          <div className="row">
            <h2 id="ag-codex-h" className="grow">Codex</h2>
            <span className={`pill ${codexAvailable ? 'ok' : ''}`}>
              <span className="dot" />
              {codexAvailable ? 'Connected' : 'Not detected'}
            </span>
          </div>
          {codexAvailable ? (
            <div className="stack">
              <MeterRow label="Primary window" window={usage.codex?.primary} />
              <MeterRow label="Secondary window" window={usage.codex?.secondary} />
            </div>
          ) : (
            <Empty title="No Codex session limits">
              <p>Start a Codex session on this PC to see live window percentages.</p>
            </Empty>
          )}
        </section>
      </div>
    </div>
  );
}

export function DevBuildsView({
  github,
  error,
  onOpenExternal,
}: {
  github: DevGithub | null;
  error?: string | null;
  onOpenExternal?(url: string): void;
}) {
  if (error) {
    return <Banner kind="bad" title="Could not load builds">{error}</Banner>;
  }
  if (!github || !github.available) {
    return (
      <section className="card">
        <Empty title="Builds unavailable">
          <p>GitHub pull request checks are paused when Private mode is on or when GitHub CLI is offline.</p>
        </Empty>
      </section>
    );
  }

  const prs: DevPr[] = github.prs ?? [];
  if (!prs.length) {
    return (
      <section className="card">
        <Empty title="No open pull requests">
          <p>All branches are merged or closed right now.</p>
        </Empty>
      </section>
    );
  }

  return (
    <section className="card stack" aria-labelledby="builds-h">
      <h2 id="builds-h">Open pull requests ({prs.length})</h2>
      <div className="list">
        {prs.map((pr) => {
          const summary = prCheckSummary(pr);
          const pillCls = summary.state === 'ok' ? 'ok' : summary.state === 'bad' ? 'bad' : summary.state === 'pending' ? 'warn' : '';
          return (
            <div className="list-item" key={pr.number}>
              <span className="tag">#{pr.number}</span>
              <div className="grow">
                <div className="title">{pr.title}</div>
                <div className="meta">{pr.headRefName}</div>
              </div>
              <span className={`pill ${pillCls}`}>
                <span className="dot" />
                {summary.label}
              </span>
              {pr.url && onOpenExternal && (
                <button type="button" className="btn sm" onClick={() => onOpenExternal(pr.url)}>
                  Open PR
                </button>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function PibloDev({
  initialTab = 'today',
  onOpenCommandPalette,
}: {
  initialTab?: DevTab;
  onOpenCommandPalette?(): void;
}) {
  const [tab, setTab] = useState<DevTab>(initialTab);
  const [activeListId, setActiveListId] = useState('founder-today');
  const [sharesByDraft, setSharesByDraft] = useState<Record<string, DevShare[]>>({});
  const act = useAct();

  useEffect(() => {
    setTab(initialTab);
  }, [initialTab]);

  const overview = usePoll<DevOverview>('/dev/overview', 8000);
  const checklists = usePoll<{ lists: DevChecklist[] }>('/dev/checklists', 8000);
  const content = usePoll<{ drafts: DevDraft[] }>('/dev/content', 8000);
  const usage = usePoll<DevUsage>('/dev/usage', 15000);
  const github = usePoll<DevGithub>('/dev/github', 20000);

  const reloadAll = () => {
    overview.reload();
    checklists.reload();
    content.reload();
    usage.reload();
    github.reload();
  };

  const handleTick = async (listId: string, itemId: string, done: boolean, note?: string) => {
    const r = await act('POST', `/dev/checklists/${encodeURIComponent(listId)}/items/${encodeURIComponent(itemId)}`, { done, note }, done ? 'Ticked off' : 'Unticked');
    if (r.ok) {
      checklists.reload();
      overview.reload();
    }
  };

  const handleCreateFromFeature = async (feature: string, summary: string, clipPath?: string) => {
    const r = await act<DevDraft>('POST', '/dev/content/from-feature', { feature, summary, clip_path: clipPath }, 'Drafts created from feature');
    if (r.ok) {
      content.reload();
      overview.reload();
    }
  };

  const handleApprove = async (id: string) => {
    const r = await act<{ draft: DevDraft; shares: DevShare[] }>('POST', `/dev/content/${encodeURIComponent(id)}/approve`, undefined, 'Approved. Opening official share page.');
    if (r.ok) {
      const shares = r.data.shares ?? [];
      setSharesByDraft((prev) => ({ ...prev, [id]: shares }));
      const firstUrl = shares.find((s) => s.url)?.url;
      if (firstUrl) {
        void window.piblo.openExternal(firstUrl);
      }
      content.reload();
      overview.reload();
    }
  };

  const handleMarkPosted = async (id: string) => {
    const r = await act('POST', `/dev/content/${encodeURIComponent(id)}/posted`, undefined, 'Marked as posted');
    if (r.ok) {
      content.reload();
      overview.reload();
    }
  };

  return (
    <div className="page">
      <PageHead
        title="Piblo Dev"
        sub="Today, founder checklists, Content Studio, calm agent usage meters and open PR checks."
        right={
          <div className="row">
            {onOpenCommandPalette && (
              <button type="button" className="btn" onClick={onOpenCommandPalette}>
                <Icon name="search" size={16} /> Jump (Ctrl+K)
              </button>
            )}
            <button type="button" className="btn" onClick={reloadAll}>
              <Icon name="refresh" size={16} /> Refresh
            </button>
          </div>
        }
      />

      <div className="seg" role="tablist" aria-label="Piblo Dev tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            aria-pressed={tab === t.id}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'today' && (
        <DevTodayView
          overview={overview.data}
          checklists={checklists.data?.lists ?? []}
          error={overview.error}
          onJump={setTab}
          onTick={(listId, itemId, done) => void handleTick(listId, itemId, done)}
        />
      )}

      {tab === 'checklists' && (
        <DevChecklistsView
          lists={checklists.data?.lists ?? []}
          error={checklists.error}
          activeListId={activeListId}
          onSelectList={setActiveListId}
          onTick={(listId, item, done, note) => void handleTick(listId, item.id, done, note)}
        />
      )}

      {tab === 'content' && (
        <DevContentStudioView
          drafts={content.data?.drafts ?? []}
          error={content.error}
          sharesByDraft={sharesByDraft}
          onCreateFromFeature={(f, s, c) => void handleCreateFromFeature(f, s, c)}
          onApprove={(id) => void handleApprove(id)}
          onMarkPosted={(id) => void handleMarkPosted(id)}
          onOpenExternal={(url) => void window.piblo.openExternal(url)}
        />
      )}

      {tab === 'agents' && <DevAgentsView usage={usage.data} error={usage.error} />}

      {tab === 'builds' && (
        <DevBuildsView
          github={github.data}
          error={github.error}
          onOpenExternal={(url) => void window.piblo.openExternal(url)}
        />
      )}
    </div>
  );
}
