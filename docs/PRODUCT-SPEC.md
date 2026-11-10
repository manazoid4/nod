# Piblo product spec (source of truth)

Owner: Maz. Last updated: 10 Nov 2026. Every page, campaign and agent copies from this file. If something here is wrong, fix it here first.

**Public-copy rule:** the site and Kickstarter say *less* than this file. Never publish prices, chip names, RAM figures, dates or exit plans. Label every illustration "concept" until a real photo exists.

## Who it is for

1. **Lead audience:** busy people and people with ADHD. Reminders, focus, voice notes, one thing at a time.
2. Also: makers and tinkerers (add-ons, open source), developers and AI-agent users (approvals, webhooks, KVM), families.

Message order: lead with audience 1, then "and there's more" for the others.

## Piblo Standard

| | Decision |
|---|---|
| Base | M5Stack Cardputer ADV. No custom board (decided 10 Nov: avoid months of hardware testing). |
| Look | Retro: custom case and keycaps. Keys stay the Cardputer's size. |
| Voice | Conversational, GPT-Live style. The voice model runs on the companion device, not on Piblo. |
| Sound | Better speaker via software first (PR #75). |
| Typing | Keyboard, plus voice and phone typing to cut typing. |

## Piblo Pro

| | Decision |
|---|---|
| Voice | Conversational, and runs **on the device itself**. |
| Sound | Better speaker and mic. |
| Connection | Ethernet and/or a simple web interface. |
| KVM | Can see and control another computer. |
| Hardware | Not chosen. Must support on-device voice and KVM. |

## Both

- **Expandable** with add-on modules, Flipper-style. First add-on idea: a second screen or clip-on tag.
- Open-source software. No mandatory subscription.
- Works with any AI model; not tied to one company.

## Voice target

It should feel like GPT Live: fast replies, you can interrupt, natural turn-taking, natural voice. Current engine is LFM3-Omni through llama-server. Pipecat (BSD-2) is the leading framework to try for turn-taking and interruption. Main risk: echo from a small speaker next to the mic.

## Open questions

- **Companion: PC or phone?** Earlier: the voice model runs on the PC. The site draft (PR #77) now says the Piblo app runs on a phone. Maz to decide.
- Can M5Stack boards be resold inside a rebranded product? Ask M5Stack before any Kickstarter copy.
- Real prototype photos to replace the concept art.
- Which add-on ships first, and whether it is included or sold separately.

## Not public

Price targets and long-term plans are kept privately, not in this public repo.
