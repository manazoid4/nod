# Nod: Kickstarter campaign draft

Status: DRAFT for the owner to edit. Nothing here is live. Do not paste into Kickstarter until the launch gates in `GATES.md` are met.

How to use: each section below maps to a Kickstarter editor field. Text in `[square brackets]` is a placeholder the owner must fill with real, verified information. Every claim marked WORKING must be backed by uncut video before launch (see `GATES.md`). Page structure was informed only by how other hardware campaigns order their pages (short pitch, demo first, honest risks); no text has been copied and no similar result is implied.

Source note: the repo records that nothing has yet been verified on a physical Cardputer by an independent test (`docs/NOD-DEVICE-AND-CORE.md`, 6 Nov 2026), although the owner reports v1.0.2 firmware boots on the device. The "working" labels below reflect the owner's brief; confirm each on video. `docs/NOD-FILM-PLAN.md` was listed in the brief but does not exist in the repo, so no film plan was used.

---

## Title (60 characters max on Kickstarter)

Nod: a pocket button for your PC's AI

## Subtitle (under 135 characters)

A small open-source device to talk to your PC's AI, save thoughts and approve AI actions with one press. [Edit]

(Length: about 108 characters.)

## Short blurb (for the project card)

Nod is an open-source pocket device built on the M5Stack Cardputer ADV. Hold a key to talk to the AI on your Windows PC, capture a thought, or approve what an AI agent wants to do. It needs your PC and Wi-Fi to work. This is an early prototype.

## Funding goal and dates

- Goal: [TBD - set only after `ECONOMICS.md` is complete and supplier quotes are in]
- Campaign length: [TBD - Kickstarter allows 1 to 60 days]
- Currency: [TBD - GBP assumed]

---

## Story

### Video and images (placeholder)

[Lead with the uncut demo video of the real device on the real PC. Show the device, the PC screen and a hand pressing the keys in one continuous shot. Disclose on screen that the PC does the heavy work. Do not use renders of a finished case as if it already exists. The existing site illustration is labelled "interface illustration, not product photo"; keep that label if reused.]

### The problem

AI tools are useful, but they live in places that pull your attention away: a phone full of notifications or a laptop you have to sit at. To ask a quick question, save an idea or check what an AI agent is about to do, you unlock, find the app, type and get distracted.

There is a second problem for people who run AI coding agents or automations on their PC. These agents sometimes ask permission before doing something that matters, such as running a command or changing files. That prompt is easy to miss or click through without reading. A separate physical place to see and decide on those requests is useful.

### What Nod is

Nod is a small device with a screen, a keyboard, a microphone and a speaker. It connects over Wi-Fi to a program called Nod Core that runs on your Windows PC. You hold a key and talk; the PC does the thinking; the answer comes back on the device.

It is not a phone replacement and it does not run AI models itself. The device is the controls. The PC is the engine.

### What works today and what is planned

Please read this section carefully. We would rather under-promise.

**Working in the prototype** (built into the current firmware and Nod Core; owner to confirm each on camera before launch):

| Feature | What it does |
|---|---|
| CALL (hold-to-talk) | Hold a key, speak, release, and hear a spoken reply from the AI connected to your PC. |
| Voice capture / Brain Dump | Speak a thought and save it as a note for later. |
| Agent approvals | When a supported AI agent on your PC asks permission, the request appears on the device and you accept or decline. If you do not answer, nothing is approved and the request falls back to the normal prompt on your PC. |
| Focus timers | Start and run focus sessions from the device. |
| Charging mode | A calm screen while charging that shows battery percentage and status. Charging is inferred from the battery-voltage trend, so it may occasionally be wrong. |
| Quick-action routines | One-press shortcuts for simple actions on your PC. |

**Planned, not built or not yet proven. Do not treat these as part of any reward:**

| Feature | Honest status |
|---|---|
| SUBTITLES | Planned: load or generate subtitles for local video files played from a PC connected to a TV. It will not work with Netflix, Disney+, YouTube or other DRM or streaming services unless real, authorised support is built and tested. |
| Routine builder | Planned: create your own routines without code. Today routines are set up by editing configuration. |
| Larger screen | Planned and only a template so far. The screen driver and wiring are unknown until a sample is tested. May not happen. |
| Printed case | Planned: a 3D-printed enclosure. [Design, fit and print testing status: TBD]. It is not a manufactured, injection-moulded or metal case. |

Other ideas on our website, such as saved-video search and Reel-to-Print, are research only and are not part of this campaign.

### How it works (and what you need)

1. You press a key on Nod.
2. Nod sends your request over Wi-Fi to Nod Core on your Windows PC.
3. Nod Core talks to the AI service or tools you have set up and sends the result back.
4. For approvals, Nod shows what is being asked and waits for you. It never approves by itself.

You need:

- A Windows PC that is switched on and running Nod Core. Nod does not work without it.
- A Wi-Fi network that both Nod and the PC can reach.
- An AI service of your choice. Free models are supported; some providers charge, and that cost is yours, not ours. [List only models actually tested.]
- For the kit: nothing else. For the software-only option: your own M5Stack Cardputer ADV and the ability to flash firmware.

Nod itself has no subscription. Optional AI or cloud services you choose to connect may cost money. Using Nod away from home depends on how you set up your own private connection; this is not yet tested with ordinary users. [Update after setup tests.]

### Who it is for

- People who already use AI on a Windows PC and want a quicker, calmer way to reach it.
- People who run AI coding agents and want a physical place to review and approve their requests.
- Makers who like hackable devices and are happy to flash firmware.

Probably not for you yet: anyone who needs Mac or Linux support, anyone who wants it to work without a PC, or anyone who needs a polished finished product. [Edit once outsider setup tests are complete.]

### Open source

Nod's firmware and Nod Core are open source under the MIT licence, so you can read the code before backing. Parts of the Bluetooth-related draft are adapted from Anthropic's open-source Claude Desktop Buddy (MIT). Nod is an independent project and is not affiliated with or endorsed by Anthropic or M5Stack. The hardware is the M5Stack Cardputer ADV, a third-party board, and we say so plainly.

### Why we are crowdfunding

[Owner to write: what the money pays for, tied to real quotes from `ECONOMICS.md`. Only list items that are in the budget.]

### Timeline

[TBD - dates only after supplier quotes and sample lead times exist. Suggested structure: campaign ends, software release for software-only backers, kit assembly, shipping. Add buffer. Do not state a month until it is evidence-based.]

### Risks and challenges

Rewrite this in your own words and keep it specific. Starting points drawn from the project's own audit:

- **Prototype stage.** Features have been tested by the maker, not yet by many outside users. [Update with results of the 5 outsider setup tests and the 100 approval trials.]
- **Needs a PC.** The device is a remote control and display. Without your Windows PC and Wi-Fi it does nothing useful.
- **Third-party hardware.** The core board is an M5Stack Cardputer ADV. Supply, price and availability are outside our control.
- **Case and fit.** The printed case may need several revisions. Print quality, yield and fit around the battery, USB-C port, speaker and keyboard are not yet proven at batch scale.
- **Battery and shipping.** Lithium batteries have transport rules (UN38.3). Some countries or carriers may restrict shipping, and we may have to exclude some destinations.
- **Compliance.** The Cardputer is a certified module, but a finished product still needs its own assessment (radio, EMC, battery, WEEE, product safety and consumer law). [Status: TBD.] This could add cost or delay.
- **Security.** Approving AI actions is a safety feature, so mistakes matter. We test that nothing runs without your explicit approval, but no outside security review has been done. [Update.]
- **AI services change.** Third-party providers can change prices, limits or terms. We cannot promise any provider will work for ever.
- **Subtitles and routines.** These are planned and may be delayed, limited or dropped.
- **Costs and funding.** Pledges are not profit. Fees, VAT, shipping, returns and failed prints come out of the total. If costs rise we may have to absorb the difference or reduce scope. [Summarise from `ECONOMICS.md`.]
- **Small team.** [Owner to describe team and experience honestly, including what happens if you are unavailable.]

How we will handle problems: [TBD - commit to regular updates and say what you will do if a reward cannot be delivered. Check Kickstarter's rules on creator responsibilities.]

### FAQ

**Do I need a PC?** Yes, a Windows PC running Nod Core, on the same Wi-Fi or reachable network.

**Does it work offline?** No. It needs Wi-Fi and your PC. Some AI models can run locally on your PC, depending on your PC.

**Is there a subscription?** Nod has none. AI providers you choose may charge you directly.

**Which AI does it use?** Whichever you configure in Nod Core. [List only models actually tested.]

**Can the AI do things without my say-so?** Approval requests wait for your answer, and no answer means no approval. Please still read the risks: this is a prototype.

**Does it work with Mac or Linux?** Not currently. [Confirm.]

**Does it work with Netflix, YouTube or other streaming?** No. Planned subtitles are only for supported local video files.

**Is the case metal?** No. The kit case is planned to be 3D printed. [Confirm material and finish once tested.]

**Can I use my own Cardputer?** Yes, with the software-only reward. You flash the firmware yourself.

**Where do you ship?** [TBD after shipping and battery-transport quotes.]

**What about VAT and customs?** [TBD - depends on VAT registration and destination. Take advice.]

**Is this affiliated with Anthropic or M5Stack?** No.

**What if it does not arrive or does not work?** [TBD - state your replacement approach after checking Kickstarter's policies; do not promise refunds Kickstarter does not provide.]

### Specs and requirements

Device (M5Stack Cardputer ADV, per the manufacturer; verify against current M5Stack documentation before publishing):

- Microcontroller: ESP32-S3, 8 MB flash
- Display: 240 x 135
- Input: 56-key keyboard
- Audio: microphone and speaker
- Battery: 1750 mAh (confirm against the supplied unit)
- Connectivity: Wi-Fi and Bluetooth LE
- Case: [3D-printed, details TBD]

Computer:

- Windows PC (version [TBD]) running Nod Core
- Wi-Fi network shared with the device
- An AI service or local model of your choice

Firmware: v1.0.2 reported on the owner's device. The latest compile was 1,460,865 B of 1,572,864 B available. Not independently verified on hardware.

---

## Creator profile and extras

- Creator name and bio: [Owner to write]
- Website: [Owner's site URL, once it has a real opt-in signup instead of a mailto link]
- Do not publish your home location (see `docs/NOD-SINGLE-RUN-CONSUMER-FUNDING.md`).
