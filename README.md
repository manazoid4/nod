# nod

**Your AI agent asks. You nod.**

nod turns a pocket device into a remote control for AI coding agents. When Claude Code wants to run a command or write a file, your device buzzes, shows exactly what it wants to do, and you press **Y** or **N**. It works from anywhere, not just within Bluetooth range of your desk.

It is also a personal action deck: big, game-like tiles for agent control, push-to-talk voice and PC macros, with XP, streaks and ranks.

> Status: **early build.** The plan and research are done. The firmware draft has not been compiled yet. Watch the repo for the first working release.

## How it works

```
Claude Code ──permission hook──▶ hub on your PC ◀──Wi-Fi / Tailscale──▶ nod device
                                      │                                     │
                                      ◀───────────── Y / N ─────────────────┘
```

- **Hub:** a small server on your PC. A Claude Code `PermissionRequest` hook sends each prompt to it and waits for your answer.
- **Device:** polls the hub, shows the prompt, sends back your decision. The first target is the M5Stack Cardputer ADV (ESP32-S3).
- **Fail-safe:** no answer in 60 seconds means the prompt falls back to the normal terminal question. nod never auto-approves anything.

## Why not just use Claude Desktop Buddy?

Anthropic's open-source [Claude Desktop Buddy](https://github.com/anthropics/claude-desktop-buddy) is excellent, but it uses Bluetooth and only works with the desktop app. nod targets Claude Code, works remotely over your own private network, and adds a programmable action deck.

## Roadmap

1. Hub endpoints and Claude Code hook
2. Device firmware: deck home screen, approvals, XP
3. Cardputer port of the official Bluetooth Buddy protocol
4. Custom hardware in a CNC metal case 

Full plan: [docs/PLAN.md](docs/PLAN.md)

## Repo layout

| Path | What |
|------|------|
| `docs/PLAN.md` | Architecture and build slices |
| `docs/UPSTREAM-NOTE.md` | Notes for a later contribution to Anthropic's Buddy repo |
| `firmware/draft/` | Uncompiled draft of the Bluetooth Buddy module (see notice below) |

## License

MIT. See [LICENSE](LICENSE).

Parts of `firmware/draft/buddy/` are adapted from [anthropics/claude-desktop-buddy](https://github.com/anthropics/claude-desktop-buddy), Copyright 2026 Anthropic, PBC, MIT License. See [NOTICE](NOTICE). nod is an independent project and is not affiliated with or endorsed by Anthropic.
