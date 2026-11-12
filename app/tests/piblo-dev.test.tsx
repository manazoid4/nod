import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { CommandPalette } from '../src/components/CommandPalette';
import {
  clampPercent,
  filterCommands,
  PALETTE_COMMANDS,
  prCheckSummary,
  usageTone,
  xCounter,
  type DevChecklist,
  type DevDraft,
} from '../src/lib/dev';
import {
  DevAgentsView,
  DevBuildsView,
  DevChecklistsView,
  DevContentStudioView,
  DevTodayView,
} from '../src/pages/PibloDev';

const SAMPLE_LISTS: DevChecklist[] = [
  {
    id: 'founder-today',
    items: [
      { id: 'pair-device', text: 'Pair Piblo with the Windows app', done: true, when: '2026-11-12T10:15:00Z', note: 'Worked first try' },
      { id: 'film-demo', text: 'Record a 30-second clip of Ask on Piblo', done: false },
    ],
  },
  {
    id: 'feature-tests',
    items: [{ id: 'ask-on-piblo', text: 'Ask on Piblo speaks reply', done: false }],
  },
  {
    id: 'kickstarter-gates',
    items: [{ id: 'hero-video', text: 'Hero video ready', done: false }],
  },
];

const SAMPLE_DRAFTS: DevDraft[] = [
  {
    id: 'draft-1',
    title: 'Ask on Piblo launch post',
    body: 'Ask on Piblo: calm spoken answers on your desk.',
    media_path: 'clip.mp4',
    link: 'https://piblo.co.uk',
    targets: [
      { platform: 'reddit', subreddit: 'SideProject', post_type: 'text', title: 'Ask on Piblo', body: 'Reddit body text' },
      { platform: 'x', title: null, body: 'Short X post under 280 chars' },
      { platform: 'linkedin', title: 'Ask on Piblo', body: 'LinkedIn post body' },
      { platform: 'instagram', title: null, body: 'Instagram caption #piblo' },
    ],
    status: 'draft',
    created: '2026-11-12T10:00:00Z',
  },
];

describe('Piblo Dev pure helpers', () => {
  it('counts X characters and flags over-280 text', () => {
    expect(xCounter('hello')).toEqual({ count: 5, left: 275, over: false });
    const long = 'a'.repeat(285);
    expect(xCounter(long)).toEqual({ count: 285, left: -5, over: true });
  });

  it('keeps usage meters calm up to 80% and amber only above 80%', () => {
    expect(usageTone(0)).toBe('calm');
    expect(usageTone(80)).toBe('calm');
    expect(usageTone(80.1)).toBe('amber');
    expect(usageTone(95)).toBe('amber');
    expect(usageTone(null)).toBe('unknown');
    expect(clampPercent(120)).toBe(100);
    expect(clampPercent(-5)).toBe(0);
  });

  it('summarises PR statusCheckRollup states cleanly', () => {
    expect(prCheckSummary({ number: 1, title: 'A', headRefName: 'b', url: 'u', statusCheckRollup: [] }).state).toBe('none');
    expect(
      prCheckSummary({
        number: 2,
        title: 'B',
        headRefName: 'b',
        url: 'u',
        statusCheckRollup: [{ name: 'test', conclusion: 'SUCCESS' }],
      }),
    ).toEqual({ state: 'ok', label: '1 passing', failing: 0, total: 1 });
    expect(
      prCheckSummary({
        number: 3,
        title: 'C',
        headRefName: 'b',
        url: 'u',
        statusCheckRollup: [{ name: 'test', conclusion: 'FAILURE' }],
      }).state,
    ).toBe('bad');
  });

  it('filters command palette entries by query words', () => {
    expect(filterCommands(PALETTE_COMMANDS, 'content studio').map((c) => c.id)).toEqual(['dev:content']);
    expect(filterCommands(PALETTE_COMMANDS, 'zzzznotfound')).toEqual([]);
  });
});

describe('DevTodayView', () => {
  it('renders counts and unticked founder items, plus empty and error states', () => {
    const html = renderToStaticMarkup(
      <DevTodayView
        overview={{ founder_unticked: 1, failing_pr_checks: 0, drafts_awaiting_approval: 2, usage_warnings: 1 }}
        checklists={SAMPLE_LISTS}
        onJump={() => {}}
      />,
    );
    expect(html).toContain('1 remaining');
    expect(html).toContain('2 waiting');
    expect(html).toContain('All clear');
    expect(html).toContain('1 above 80%');
    expect(html).toContain('Record a 30-second clip of Ask on Piblo');

    const emptyHtml = renderToStaticMarkup(<DevTodayView overview={null} checklists={[]} onJump={() => {}} />);
    expect(emptyHtml).toContain('Nothing loaded yet');

    const errHtml = renderToStaticMarkup(<DevTodayView overview={null} checklists={[]} error="Core offline" onJump={() => {}} />);
    expect(errHtml).toContain('Could not load Today overview');
    expect(errHtml).toContain('Core offline');
  });
});

describe('DevChecklistsView', () => {
  it('renders founder-today, feature-tests and kickstarter-gates with saved notes, plus empty and error states', () => {
    const html = renderToStaticMarkup(
      <DevChecklistsView
        lists={SAMPLE_LISTS}
        activeListId="founder-today"
        onSelectList={() => {}}
        onTick={() => {}}
      />,
    );
    expect(html).toContain('Founder today (1/2)');
    expect(html).toContain('Feature tests (0/1)');
    expect(html).toContain('Kickstarter gates (0/1)');
    expect(html).toContain('Saved note: Worked first try');
    expect(html).toContain('Ticked');

    const emptyHtml = renderToStaticMarkup(
      <DevChecklistsView lists={[]} activeListId="founder-today" onSelectList={() => {}} onTick={() => {}} />,
    );
    expect(emptyHtml).toContain('No checklists found');

    const errHtml = renderToStaticMarkup(
      <DevChecklistsView lists={[]} error="Disk error" activeListId="founder-today" onSelectList={() => {}} onTick={() => {}} />,
    );
    expect(errHtml).toContain('Could not load checklists');
    expect(errHtml).toContain('Disk error');
  });
});

describe('DevContentStudioView', () => {
  it('states nothing ever posts by itself, shows platform previews with 280 counter, plus empty and error states', () => {
    const html = renderToStaticMarkup(
      <DevContentStudioView
        drafts={SAMPLE_DRAFTS}
        sharesByDraft={{
          'draft-1': [{ platform: 'reddit', subreddit: 'SideProject', url: 'https://www.reddit.com/r/SideProject/submit' }],
        }}
        onCreateFromFeature={() => {}}
        onApprove={() => {}}
        onMarkPosted={() => {}}
        onOpenExternal={() => {}}
      />,
    );
    expect(html).toContain('Nothing ever posts by itself');
    expect(html).toContain('New from feature');
    expect(html).toContain('r/SideProject');
    expect(html).toContain('X (28/280)');
    expect(html).toContain('LinkedIn');
    expect(html).toContain('Instagram');
    expect(html).toContain('Approve');

    const emptyHtml = renderToStaticMarkup(
      <DevContentStudioView
        drafts={[]}
        sharesByDraft={{}}
        onCreateFromFeature={() => {}}
        onApprove={() => {}}
        onMarkPosted={() => {}}
        onOpenExternal={() => {}}
      />,
    );
    expect(emptyHtml).toContain('No drafts yet');

    const errHtml = renderToStaticMarkup(
      <DevContentStudioView
        drafts={[]}
        error="Bad JSON"
        sharesByDraft={{}}
        onCreateFromFeature={() => {}}
        onApprove={() => {}}
        onMarkPosted={() => {}}
        onOpenExternal={() => {}}
      />,
    );
    expect(errHtml).toContain('Could not load Content Studio');
    expect(errHtml).toContain('Bad JSON');
  });
});

describe('DevAgentsView and DevBuildsView', () => {
  it('renders calm and >80% amber usage meters plus empty and error states', () => {
    const html = renderToStaticMarkup(
      <DevAgentsView
        usage={{
          claude: { available: true, accounts: [{ number: 1, five_hour: { used_percent: 45 }, seven_day: { used_percent: 85 } }] },
          codex: { available: false },
        }}
      />,
    );
    expect(html).toContain('45%');
    expect(html).toContain('85%');
    expect(html).toContain('usage-meter amber');

    const emptyHtml = renderToStaticMarkup(<DevAgentsView usage={null} />);
    expect(emptyHtml).toContain('No usage data yet');

    const errHtml = renderToStaticMarkup(<DevAgentsView usage={null} error="Timeout" />);
    expect(errHtml).toContain('Could not load agent usage');
  });

  it('renders open PRs and handles unavailable, empty and error states', () => {
    const html = renderToStaticMarkup(
      <DevBuildsView
        github={{
          available: true,
          prs: [
            {
              number: 95,
              title: 'Add Piblo Dev section',
              headRefName: 'feat/piblo-dev-hermes',
              url: 'https://github.com/manazoid4/piblo/pull/95',
              statusCheckRollup: [{ name: 'ci', conclusion: 'SUCCESS' }],
            },
          ],
        }}
        onOpenExternal={() => {}}
      />,
    );
    expect(html).toContain('Add Piblo Dev section');
    expect(html).toContain('1 passing');
    expect(html).toContain('Open PR');

    expect(renderToStaticMarkup(<DevBuildsView github={{ available: false }} />)).toContain('Builds unavailable');
    expect(renderToStaticMarkup(<DevBuildsView github={{ available: true, prs: [] }} />)).toContain('No open pull requests');
    expect(renderToStaticMarkup(<DevBuildsView github={null} error="GitHub error" />)).toContain('Could not load builds');
  });
});

describe('CommandPalette', () => {
  it('renders jump dialog when open and nothing when closed', () => {
    expect(renderToStaticMarkup(<CommandPalette open={false} onClose={() => {}} onSelect={() => {}} />)).toBe('');
    const html = renderToStaticMarkup(<CommandPalette open={true} onClose={() => {}} onSelect={() => {}} />);
    expect(html).toContain('Jump anywhere in Piblo...');
    expect(html).toContain('Piblo Dev: Content Studio');
  });
});
