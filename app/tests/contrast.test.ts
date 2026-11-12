import { describe, expect, it } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const tokensPath = resolve(__dirname, '../src/styles/tokens.css');
const css = readFileSync(tokensPath, 'utf8');

/** Parse CSS custom properties from a :root or [data-theme] block. */
function parseTokens(source: string, selector: string): Record<string, string> {
  const start = source.indexOf(selector);
  if (start === -1) return {};
  const braceStart = source.indexOf('{', start);
  const braceEnd = source.indexOf('}', braceStart);
  const block = source.slice(braceStart + 1, braceEnd);
  const props: Record<string, string> = {};
  for (const line of block.split('\n')) {
    const m = line.trim().match(/^(--[\w-]+):\s*([^;]+);?/);
    if (m) props[m[1]] = m[2].trim();
  }
  return props;
}

/** Resolve a token value that may reference other tokens (single-level). */
function resolveValue(val: string, allTokens: Record<string, string>): string {
  const m = val.match(/var\((--[\w-]+)\)/);
  if (m) return allTokens[m[1]] ?? val;
  return val;
}

/** Parse a hex color like #rrggbb or #rgb to {r,g,b} 0-255. */
function parseHex(hex: string): { r: number; g: number; b: number } | null {
  const clean = hex.trim().replace(/^#/, '');
  if (!/^([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(clean)) return null;
  if (clean.length === 3) {
    return {
      r: parseInt(clean[0] + clean[0], 16),
      g: parseInt(clean[1] + clean[1], 16),
      b: parseInt(clean[2] + clean[2], 16),
    };
  }
  return {
    r: parseInt(clean.slice(0, 2), 16),
    g: parseInt(clean.slice(2, 4), 16),
    b: parseInt(clean.slice(4, 6), 16),
  };
}

/** sRGB to linear RGB. */
function lin(c: number): number {
  const v = c / 255;
  return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
}

/** Relative luminance per WCAG. */
function luminance({ r, g, b }: { r: number; g: number; b: number }): number {
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

/** WCAG contrast ratio between two colors. */
function contrastRatio(fg: string, bg: string): number | null {
  const a = parseHex(fg);
  const b = parseHex(bg);
  if (!a || !b) return null;
  const L1 = luminance(a);
  const L2 = luminance(b);
  return (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
}

const lightTokens = parseTokens(css, ':root');
const darkTokens = parseTokens(css, ':root[data-theme="dark"]');

// Text/background pairs used in actual UI (from app.css) — must meet 4.5:1 (AA)
// These pairs are checked in BOTH themes
const textBgPairs = [
  // body text
  ['--text', '--bg'],
  ['--text', '--surface'],
  ['--text', '--surface-2'],
  // secondary text
  ['--text-2', '--surface'],
  ['--text-2', '--surface-2'],
  ['--text-2', '--surface-3'],
  // muted text
  ['--text-3', '--surface'],
  ['--text-3', '--surface-2'],
  ['--text-3', '--surface-3'],
  // button text on accent backgrounds
  ['--on-accent', '--accent'],
  ['--on-accent', '--accent-hover'],
  // pair mark: tomato-deep on accent-soft
  ['--tomato-deep', '--accent-soft'],
  // pair notice: text on warn-soft (inherits body text color)
  ['--text', '--warn-soft'],
  // warning pill label and status dot
  ['--warn', '--warn-soft'],
  // connected pill label and status dot
  ['--ok', '--ok-soft'],
  // toast: bg on text (dark text on light)
  ['--bg', '--text'],
  // toast.bad: bg on danger
  ['--bg', '--danger'],
  // step.done mark: bg on ok
  ['--bg', '--ok'],
];

// Theme-specific focus ring pairs (UI component borders, must meet 3:1)
const focusPairs = {
  light: [['--ink', '--bg']],
  dark: [['--text', '--bg']],
};

// Controls and status indicators that convey meaning need >= 3:1 against their container.
// The pair mark's decorative accent fill is covered by its icon contrast above.
// Checked in BOTH themes
const accentBgPairs = [
  // primary button (accent) on surface
  ['--accent', '--surface'],
  ['--accent-hover', '--surface'],
  // danger button text (tomato-deep) on surface (ghost button)
  ['--danger', '--surface'],
  // ok background (mint-deep/mint) on surface
  ['--ok', '--surface'],
  // warning banner fill conveys status against its container
  ['--warn-soft', '--surface'],
];

describe('WCAG contrast', () => {
  it('uses the same dark tokens for system and explicit dark mode', () => {
    expect(parseTokens(css, ':root:not([data-theme="light"])')).toEqual(darkTokens);
  });

  for (const [themeName, tokens] of Object.entries({ light: lightTokens, dark: darkTokens })) {
    describe(`${themeName} theme`, () => {
      const allTokens = { ...lightTokens, ...tokens };

      for (const [fgKey, bgKey] of textBgPairs) {
        const fgRaw = allTokens[fgKey];
        const bgRaw = allTokens[bgKey];
        if (!fgRaw || !bgRaw) continue;

        const fgResolved = resolveValue(fgRaw, allTokens);
        const bgResolved = resolveValue(bgRaw, allTokens);

        it(`${fgKey} on ${bgKey} >= 4.5:1`, () => {
          const ratio = contrastRatio(fgResolved, bgResolved);
          expect(ratio).not.toBeNull();
          expect(ratio!).toBeGreaterThanOrEqual(4.5);
        });

        it(`${fgKey} on ${bgKey} >= 7:1 preferred`, () => {
          const ratio = contrastRatio(fgResolved, bgResolved);
          expect(ratio).not.toBeNull();
          if (ratio! < 7) {
            console.warn(`[WCAG] ${themeName} ${fgKey} on ${bgKey}: ${ratio!.toFixed(2)}:1 (below 7:1)`);
          }
        });
      }

      // Theme-specific focus rings
      for (const [fgKey, bgKey] of focusPairs[themeName as keyof typeof focusPairs] || []) {
        const fgRaw = allTokens[fgKey];
        const bgRaw = allTokens[bgKey];
        if (!fgRaw || !bgRaw) continue;

        const fgResolved = resolveValue(fgRaw, allTokens);
        const bgResolved = resolveValue(bgRaw, allTokens);

        it(`${fgKey} on ${bgKey} >= 3:1 (focus ring)`, () => {
          const ratio = contrastRatio(fgResolved, bgResolved);
          expect(ratio).not.toBeNull();
          expect(ratio!).toBeGreaterThanOrEqual(3);
        });
      }

      for (const [fgKey, bgKey] of accentBgPairs) {
        const fgRaw = allTokens[fgKey];
        const bgRaw = allTokens[bgKey];
        if (!fgRaw || !bgRaw) continue;

        const fgResolved = resolveValue(fgRaw, allTokens);
        const bgResolved = resolveValue(bgRaw, allTokens);

        it(`${fgKey} on ${bgKey} >= 3:1 (UI components)`, () => {
          const ratio = contrastRatio(fgResolved, bgResolved);
          expect(ratio).not.toBeNull();
          expect(ratio!).toBeGreaterThanOrEqual(3);
        });
      }
    });
  }
});
