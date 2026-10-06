# nod

**Your AI agent asks. You nod.**

### The physical control for the age of AI agents.

AI agents now write code, send emails, move files, run workflows and spend money while you are somewhere else. They work fast, but they still need a human to say *yes*. Today that means being chained to a laptop, alt-tabbing back to a terminal, or approving blind from a phone notification buried under everything else.

**nod is a pocket device that puts you back in control, wherever you are.**

When an agent wants to do something that matters, nod buzzes. It shows you, in plain words, exactly what is about to happen. One key approves. One key stops it. Your agents keep moving and you stay in charge, from the sofa, the gym, the train or the other side of the world.

### What nod does

- **Approve from anywhere.** Agent requests reach you over your own private, encrypted network, not just across the room. No answer means no action: nod never approves anything by itself.
- **See what matters at a glance.** Which agents are running, which are waiting on you, what they just did and what they cost today.
- **Talk to your AI.** Hold a key, speak, hear the answer. Ask a question, capture an idea, or tell an agent what to do next.
- **One-press actions.** A programmable deck for the things you do every day: launch a task, run a deploy, lock your PC, start a focus session, trigger a workflow.
- **Built to keep you going.** XP, streaks and ranks turn approvals, focus sessions and finished tasks into a game you actually want to keep playing.
- **Yours, not ours.** Open source, works with free AI models, runs through a small hub on your own computer. No subscription and no cloud account needed.

### Who it's for

- **Developers** running Claude Code, Codex, Cursor, Gemini CLI or any agent that asks for permission.
- **Founders and solo builders** who run AI to do the work of a team and can't sit at a desk all day.
- **Automators** with n8n, Make or Zapier flows that should check with a human before they act.
- **Makers and tinkerers** who want a hackable, beautifully built device they can bend to their own workflow.

### Why a device and not an app?

A phone is where focus goes to die. nod does one job: it keeps your agents moving and keeps you in charge, without pulling you into a feed. A real key is also a safety feature. It is deliberate and hard to press by accident, and it is always within reach.

> **Status: early build.** nod is being developed in the open. The first version runs on the M5Stack Cardputer ADV (ESP32-S3) and a custom device is in design. Star or watch the repo to follow along and hear about the launch first.

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
| `docs/ROADMAP.md` | What works today and what is coming |
| `docs/UPSTREAM-NOTE.md` | Notes for a later contribution to Anthropic's Buddy repo |
| `firmware/draft/` | Uncompiled draft of the Bluetooth Buddy module (see notice below) |

## License

MIT. See [LICENSE](LICENSE).

Parts of `firmware/draft/buddy/` are adapted from [anthropics/claude-desktop-buddy](https://github.com/anthropics/claude-desktop-buddy), Copyright 2026 Anthropic, PBC, MIT License. See [NOTICE](NOTICE). nod is an independent project and is not affiliated with or endorsed by Anthropic.
