# Piblo product spec (source of truth)

Owner: Maz. Last updated: 10 Nov 2026. **Living document:** decisions can change, but change this file first and change only what must move. Do not rewire the whole project for one change.

Every page, campaign and agent copies from this file.

**Public-copy rules**
- Lead with the solution, not with "AI".
- Never publish prices, chip names, RAM figures, dates or business plans.
- Hardware: say "proven open hardware". Never deny the base board if asked.
- Label every illustration "concept" until a real photo exists.

## The pitch

**Tagline:** Say it once. Piblo handles the rest.

Piblo is a small, calm device you talk to like a person. It remembers what you told it, does things for you, and speaks up when something matters (like "your train's delayed, leave 10 minutes early"). It works with any AI, keeps your memory yours, and grows with you.

## Who it is for

1. **Lead:** busy people and people with ADHD (time, reminders, focus, getting things out of your head).
2. Also: makers, developers and AI-agent users, families. They get extras on top: open source, add-ons, agents, approvals.

## Pillars

| Pillar | What it means |
|---|---|
| Talk like a person | Natural, interruptible conversation. Wake word "Hey Piblo" plus a mic button. Just start talking to interrupt. |
| Remembers you | "Like I said yesterday..." Memory across days, linked notes you can browse (Obsidian-style). |
| Does things | Ask Piblo to build an agent ("check my email at 8 and tell me what matters"). Agents can be spawned mid-conversation and run off-device. |
| Show me once (Teach Demo) | Do a task on your computer while explaining it; Piblo turns the recording into a reusable helper, reads it back for you to confirm, then does it for you next time (with your approval). Recordings stay on your own devices. |
| Speaks first when it matters | Launch scope: time and travel (commute delays, leave now, meeting in 10, deadlines). |
| Neutral | Works with any AI and any agent harness. Open-weight models by default, any provider (e.g. OpenRouter) optional. No lock-in. |
| Yours | Memory is local-first on your own devices with optional end-to-end encrypted sync; can also live in Notion, a home server and more. |
| Connects to everything | Integrations through MCP (Gmail, Calendar, Notion, GitHub, Hermes and more). |
| Grows with you | Buddy, the on-screen character, changes form based on what you do together. No feeding, no guilt. |

## Safety: what agents may do

Set per agent:
- **Just do it:** read, summarise, remind.
- **Ask on Piblo:** send, book, post. A key press approves.
- **Never:** payments, deletions, unless the owner unlocks them.

## First three minutes

1. "Hi, I'm Piblo. What should I call you?"
2. A friendly chat about the person's day.
3. "What's one thing you always forget?" It builds that agent live.
4. "What are you working towards?" The goal links to the agent.
5. "Watch this": a flashy moment (several AIs at once, or acting on the computer).
6. Buddy changes form for the first time.

QR-code setup is the backup path. Any step can be skipped.

## Buddy

- Pixel art on the device; clean shapes on the site and app.
- Forms are set by what you do together (e.g. Monk for focus, Tinkerer for building agents, Explorer for goals and travel).
- Each form is artwork plus one simple rule (data, not code). About 6 at launch; the community can add more later.
- Customise by voice ("make yourself blue") or 3 presets. No editor screens.
- The reacting face ships only when it is properly done.

## Look and sound

- Style: Apple polish + Teenage Engineering character + Flipper Zero community, friendly for everyday people.
- Sounds: soft, warm chimes (a "bloop" for reminders, a happy run for done) with soft premium mechanical clicks.
- Interface is voice-first; the keyboard is there but out of the way.

## Models

| Model | Decision |
|---|---|
| Piblo Standard | Batch 01 runs on proven open hardware inside Piblo's own retro case. The voice model runs on the paired phone or computer (a small ~2B open omni model that runs on most laptops), or in the cloud. Better sound via software. Pairs with phone or computer; Android and Windows first, then native Linux, macOS and iPhone. |
| Piblo Standard (Batch 02) | "Standard, but better": Piblo's own hardware built from off-the-shelf modules. |
| Piblo Pro (Batch 02) | "Your AI, on your desk. Nothing leaves the room." Offline voice and local agents, biggest screen, better sound and mic, more mechanical feel, an intuitive KVM (see and control another computer). E-ink desk display included. Runs a small tool-calling model (about 7-9B) without needing a gaming GPU. Hardware chosen by benchmark after Batch 01. |

## Add-ons

Touchscreen (second screen / clip-on tag), camera, e-ink desk display, Ethernet. Each Piblo should make the next one more useful (pocket + desk + home + family).

## Engine

- Piblo's own engine. Borrow permissively licensed code (e.g. MIT code from Nous Research's Hermes Agent: learning loop, skills, user profile) without depending on any one project.
- Adapters for any agent harness; integrations via MCP.
- Voice: build on the existing `host/mazhost/live_voice.py` path. Pipecat (BSD-2) is the leading framework for turn-taking and interruption. Main risk: echo from a small speaker next to the mic.
- Check every borrowed project's licence. Do not copy AGPL code into Piblo.

## Kickstarter (draft)

- Small goal so it funds fast; a numbered, genuinely limited first batch ("Batch 01").
- Tiers: Batch 01 early bird, Standard, Standard + add-on, Founder (special colour, name or company in the credits, optional call).
- Batch 01 backers get extra perks; only promise extras that will definitely ship.
- Stretch goals mix free software upgrades for everyone with paid add-on unlocks, plus backer-count goals and backer votes. Draft order: personalise (voted voices and personalities, Batch 01 Buddy form), touchscreen add-on, connects to everything (MCP, at 300 backers), camera add-on + travel mode, template gallery, Mac and Linux apps + Buddy form creator (1,000 backers), e-ink display add-on, retro key mat for all, secret Pro reveal, iPhone app, Founders' Pro upgrade.
- Launch only when the launch list hits its target. Channels: YouTube, Instagram, Discord, built in public.

## Optional paid extras (never required)

Piblo Plus: always-on cloud agents, encrypted sync, bundled AI credits. Also a marketplace for community agents, templates and add-ons, and hardware add-ons.

## Open questions

- Ask M5Stack whether their board may be resold inside a rebranded product.
- Check AI providers' terms before selling credit bundles.
- Real prototype photos to replace the concept art.
- Pro hardware benchmark (after Batch 01).

## Not in this public repo

Prices, budgets and long-term plans are kept privately.
