# Upstream note: Cardputer port for anthropics/claude-desktop-buddy

**Status: parked. Do not open the PR yet.**

## Idea
Contribute an M5Stack Cardputer ADV port of the official Bluetooth Buddy firmware to
https://github.com/anthropics/claude-desktop-buddy.

## Why later
- nod's remote path (hub + Wi-Fi/Tailscale) comes first.
- The Bluetooth draft in `firmware/draft/` must compile, fit flash (likely needs NimBLE)
  and be tested on hardware before it is worth proposing.

## When ready
1. Port the draft to stand alone against the upstream repo's structure (no nod/MAZ Pocket includes).
2. Keep it minimal: display + keyboard driver swap, Y/N keys, passkey pairing.
3. Check upstream CONTRIBUTING and open issues for an existing Cardputer port first.
4. Open the PR, link nod as the remote-first sibling project.

## Claude for Open Source program (checked 2026-10-06)
Criteria: dependents/downloads, foundation core-committer, 100+ merged PRs elsewhere,
20+ external contributors, or OpenSSF score 0.4+. nod meets none yet. A merged upstream
PR plus a public, used nod repo is the realistic route.
