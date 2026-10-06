# nod roadmap

nod grows out of **MAZ Pocket**, a working prototype on the M5Stack Cardputer ADV
with a companion hub (**MAZ Core**) on Windows. Everything under "Working today" runs
on that prototype now. Everything else is planned and marked as such.

## Working today (prototype, v0.8)

**Talk**
- **Call** — hold Space to talk, release to send. The hub transcribes, asks the AI, and the answer is shown and spoken back.
- Replay the last answer, mute voice, start a new conversation, all from the keyboard.
- Switch AI route on the device: cloud, local, or auto (local first, then cloud).

**Capture**
- **Teach by demonstration** — record a PC workflow while you narrate, mark key moments, and turn it into reusable instructions for AI agents.
- **Brain dump** — speak freely, mark highlights, get structured notes back.
- **Voice recorder** — plain audio when that's all you need.

**Agents**
- **Agent status** — which agents are working, waiting, stale or need attention.
- **Plan** — give it a task and a project, get an implementation plan without anything being executed.
- **Crew** — splits bigger jobs across Claude Code, Codex or Hermes, run one at a time so they don't collide.
- **Retro** — reviews finished work and proposes one lasting improvement (prompt, skill, knowledge or test).
- **Projects and builds** — Git state, tests and builds for your local projects.

**Control and safety**
- **Confirmed PC actions** — the AI proposes, you press Enter. It can never supply a URL, path or command.
- **Phone-approved PC control** — scoped, short-lived, revocable grants (read-only, project, full PC). The AI can't approve itself, and one tap revokes everything.
- **Prompt deck** — ready-made templates for bug fixing, features, audits, security and more, filled with live project context.
- **Pairing** — token-based pairing, a local web page at `mazpocket.local`, and redacted debug bundles.

## v1.0 — nod launch

- **Approve from anywhere** — agent permission requests reach the device over your private network. Status light and buzz when an agent needs you. Y or N. Nothing is auto-approved.
- **Live agent lights** — idle, thinking, done, needs-you, error, visible at a glance.
- **Free AI by default** — a chain of free cloud models with local fallback. No subscription.
- **Fast, accurate speech** — cloud speech-to-text with an offline fallback.
- **Natural voice replies** — high-quality text-to-speech.
- **Voice to task** — say it, and it becomes a task, a note or a reminder automatically.
- **Action keys with layers** — Work, Home and Focus layers, each with one-press actions and routines.
- **Goals** — track what matters (applications sent, clients contacted, workouts, study hours) in one tap from your phone, glance at progress on nod.
- **Daily brief** — your priorities in the morning, nudges during the day, "what next" on demand.
- **XP, streaks and ranks** — earned from real outcomes, not screen time.
- **One-step setup** — a single installer for the hub and a web flasher for the device.

## v1.x — after launch

- Phone companion app for setup, goals and approvals on the go.
- Automation triggers for n8n, Make and Zapier, so workflows can ask nod before they act.
- Bluetooth mode compatible with Anthropic's Claude Desktop Buddy protocol.
- Smart home controls.
- Community action packs and themes.
- A desk handset for voice calls with your AI at home.
- Mac and Linux hub.

## v2 — the nod device

- Custom hardware designed around nod: bigger battery, dedicated approve and talk keys, status light ring.
- Precision-machined metal case as a limited Founders edition, with a lighter standard edition.
- Fully open firmware and hub. No account required, no subscription, and nothing a buyout can switch off.
