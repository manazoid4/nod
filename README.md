# nod

**Ask. Listen. Nod.**

### Your AI sidekick, in your pocket.

AI can already answer almost anything, remember everything and do real work for you. But it lives inside a phone full of notifications or a laptop you have to sit at. Every time you reach for it you lose the thread: unlock, find the app, type, scroll, get distracted.

**nod is a small, beautifully built device with one job: put your AI one press away.**

Hold a key and talk. nod listens, thinks and answers out loud. Capture an idea before it disappears. Ask a question mid-conversation. Tell your AI to get something done and get on with your day. No feeds, no apps, no rabbit holes. Just you and an assistant that actually helps.

### What nod does

- **Talk, don't type.** Hold to speak, release to hear the answer. Fast, natural, hands mostly free.
- **Never lose a thought.** Voice notes become clean notes, tasks and reminders automatically.
- **Your day, at a glance.** What's next, what's waiting on you, and what got done today.
- **One-press actions.** A programmable deck for the things you do every day: start a focus session, message someone, control your computer, run a routine, trigger an automation.
- **Stay in charge of your AI.** When an AI agent wants to do something that matters, like sending, buying, deleting or deploying, nod shows you exactly what and waits for your nod. Nothing happens without you.
- **Built to keep you going.** XP, streaks and ranks turn focus, follow-through and finished tasks into a game you want to keep playing.
- **Yours, not ours.** Open source. Works with free AI models. Your data goes through a small hub on your own computer. No subscription required.

### Who it's for

- **Busy people** who want the power of AI without living on their phone.
- **Students and creatives** capturing ideas, studying and staying on track.
- **Founders, freelancers and small businesses** using AI to do the work of a team.
- **Developers and automators** who need a human-in-the-loop for their AI agents and workflows.
- **Makers** who want a hackable device they can shape around their own life.

### Why a device and not an app?

Your phone is built to grab your attention. nod is built to give it back. One device, one purpose, a real key you can press without looking, and an assistant that's there the moment you need it and quiet when you don't.

> **Status: early build.** nod is being developed in the open. The first version runs on the M5Stack Cardputer ADV (ESP32-S3) and a custom device is in design. Star or watch the repo to follow along and hear about the launch first.

## How it works (agent approvals, first feature)

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
| `docs/ROADMAP.md` | What is verified, in progress and planned |
| `docs/UPSTREAM-NOTE.md` | Notes for a later contribution to Anthropic's Buddy repo |
| `firmware/draft/` | Uncompiled draft of the Bluetooth Buddy module (see notice below) |

## License

MIT. See [LICENSE](LICENSE).

Parts of `firmware/draft/buddy/` are adapted from [anthropics/claude-desktop-buddy](https://github.com/anthropics/claude-desktop-buddy), Copyright 2026 Anthropic, PBC, MIT License. See [NOTICE](NOTICE). nod is an independent project and is not affiliated with or endorsed by Anthropic.
