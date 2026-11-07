# Piblo: Kickstarter page draft

Status: DRAFT. Do not paste into Kickstarter until the gates in `docs/kickstarter/GATES.md` are met. Items marked `TODO-owner` need the owner. Nothing here is a price, reward or date promise.

Labels used: **Verified** (tested, see `README.md`), **In testing** (built, not yet proven on video), **Concept** (drawn only).

---

## Title (60 characters max)

Piblo: a pocket helper for less screen time

## Subtitle

A small open-source pocket device for your PC's AI. Hold a key, say it, get on with your day. Early prototype.

## Hook (first lines of the page)

Ever get to the front door and remember the bins?

Piblo is a small pocket device for the things you would otherwise lose: the note, the idea, the question you did not want to open a laptop for.

Hold a key. Say it. Put it away.

Less screen. More life.

This is an early prototype. We would rather show you what is real than promise more.

`TODO-owner`: lead the page with an uncut video of the real device and a PC in one shot. Do not lead with the concept films. See `real-footage-shotlist.md`.

---

## The story

### The problem

Your phone is full of other people's alerts. To ask one quick question or save one idea, you unlock it, find an app and lose ten minutes.

If you use AI on a Windows PC, there is a second problem. AI agents sometimes ask permission before they run a command or change files. That prompt is easy to miss or click through.

### What Piblo is

Piblo is a pocket device with a small screen, a keyboard, a microphone and a speaker. It connects over Wi-Fi to a program called Piblo Core on your Windows PC. The PC does the heavy work. The device is the controls.

It does not replace your phone. It does not run AI models itself.

### Why we are building it

`TODO-owner`: two or three plain sentences in your own voice. Why you, why this, why now.

---

## What it does today

Only things we have tested. Source: `docs/ROADMAP.md`, `docs/NOD-DEVICE-AND-CORE.md`.

| What | Status |
|---|---|
| Piblo Core on a PC answers questions using free cloud AI, and switches provider when one is down or rate-limited | Verified |
| The device connects to Core over Wi-Fi and stays in sync | Verified |
| Firmware updates over Wi-Fi | Verified |
| Firmware builds for the Cardputer ADV | Verified (build only, not a hardware test) |
| Open-source code on GitHub, MIT licence | Verified (the repo is public) |

## What is built but not yet proven on camera

We will move each line up only when there is uncut footage. `TODO-owner`: update this table as footage arrives.

| What | Status |
|---|---|
| Hold a key, speak, hear a spoken reply | In testing |
| Voice capture: say a thought, save it as a note | In testing |
| Typed notes on the device | In firmware, device test pending |
| Charging screen with battery percentage (charging is inferred from the battery-voltage trend, so it can be wrong) | In firmware, not yet checked on a device |
| Agent status on the device | In testing |
| Yes or no on the device when your PC asks to do something important. No answer means no. | To verify. Zero unapproved runs is a hard requirement and is not yet proven |

## Concept only

None of these exist as hardware. None are in any reward.

| Idea | What it would be |
|---|---|
| Piblo Flip | A hinged screen that opens to a full keyboard |
| Piblo Slide | A sliding keyboard |
| Piblo Snap | A touchscreen module that clips on the back, plus add-ons and accessories |
| Larger screen | A bigger display. Driver and wiring are unknown until a sample is tested. It may not happen |
| Today screen | A calm place for reminders and what comes next |
| Subtitles for local video files | Planned. It will not work with Netflix, Disney+, YouTube or other streaming services |
| Saved-video search, print-from-video | Research only |

Every concept image and film in this campaign is labelled "Concept render, not final hardware".

---

## The hardware, honestly

- The device is an **M5Stack Cardputer ADV**. It is off-the-shelf hardware made by M5Stack. Piblo does not make it and it is not made in Britain.
- Published size: 84 x 54 x 19.6 mm. Screen 1.14 inch (240 x 135). 56 keys. Microphone and speaker. `TODO-owner`: check every figure against M5Stack's current page before publishing.
- The Piblo case is a **concept**. It is a snap-on front and back for a home 3D printer, in orange, cream or mint. It has not been printed or fit-tested. The CAD is in the repo (`hardware/case/nod_case.scad`).
- Piblo is not affiliated with or endorsed by M5Stack or Anthropic.

## What you need

- A Windows PC, switched on, running Piblo Core.
- A Wi-Fi network that both the PC and device can reach.
- An AI service of your choice. Free providers work. Some providers charge. That cost is yours.

There is no Piblo subscription. Optional online services you connect may cost money.

---

## Open source

The firmware, Piblo Core and the website are on GitHub under the MIT licence. You can read the code before you back. Some Bluetooth draft code is adapted from Anthropic's open-source Claude Desktop Buddy (MIT). `TODO-owner`: confirm credit wording.

## Who it is for

- People who use AI on a Windows PC and want a calmer way to reach it.
- People who run AI agents and want a physical yes or no.
- Makers who are happy to flash firmware.

Probably not yet for: Mac or Linux users, anyone who wants it to work without a PC, anyone who wants a finished product.

---

## Rewards

`TODO-owner`: all reward tiers, prices, limits and shipping. See `docs/kickstarter/REWARDS.md` for the structure. Nothing is decided. Do not list any concept item as a reward.

## Funding goal and what the money pays for

`TODO-owner`: goal, from `docs/kickstarter/ECONOMICS.csv` once real quotes exist. List only budgeted items.

## Timeline

`TODO-owner`: dates only after supplier quotes and sample lead times. Add buffer. Until then, state no month.

---

## Risks and challenges

Piblo is a one-maker prototype. Here is what could go wrong.

- **Prototype stage.** The core path works for the maker. Few outside people have tried it. `TODO-owner`: add results of the five outsider setup tests when done.
- **It needs a PC.** Without your Windows PC and Wi-Fi it does nothing useful.
- **Voice and approvals are still being tested.** We will not call them working until we have shown them on camera, and the approval feature has had no outside security review.
- **Third-party hardware.** The Cardputer ADV is made by M5Stack. Price, supply and availability are outside our control.
- **The case is unproven.** It has not been printed. Fit around the battery, USB-C port, speaker and keys may need several revisions. Batch printing is untested.
- **Shipping batteries.** Lithium batteries have transport rules (UN38.3). Some countries or carriers may be excluded.
- **Compliance.** The Cardputer is a certified module, but a finished product still needs its own UK assessment (radio, EMC, battery, WEEE, product safety, consumer law). `TODO-owner`: status. This could add cost or delay.
- **AI services change.** Providers can change prices, limits or terms. We cannot promise any provider will work for ever.
- **Planned features may slip or be dropped.** Concepts are ideas, not promises.
- **Money.** Pledges are not profit. Fees, VAT, shipping, returns and failed prints come out of the total. `TODO-owner`: summary from the economics model.
- **Small team.** `TODO-owner`: who you are, what you have built, and what happens if you are unavailable.

How we will handle problems: regular honest updates, including failures. `TODO-owner`: add the replacement approach after reading Kickstarter's creator rules. Do not promise refunds that Kickstarter does not provide.

---

## FAQ

**Do I need a PC?** Yes. A Windows PC running Piblo Core, on the same Wi-Fi.

**Does it work offline?** No. It needs Wi-Fi and your PC.

**Is there a subscription?** Piblo has none. AI providers you choose may charge you.

**Which AI does it use?** Whichever you set up in Core. Free cloud providers are verified. `TODO-owner`: list the models actually tested.

**Can the AI act without my say-so?** The design is that nothing runs without your yes, and no answer means no. This is still being tested. Please read the risks.

**Does it work on Mac or Linux?** Not now.

**Does it work with Netflix or YouTube subtitles?** No.

**Is the case metal?** No. The planned case is 3D printed and not yet made.

**Is Flip, Slide or a touchscreen coming?** They are concepts. We are not promising them.

**Can I use my own Cardputer?** The software is open source, so you can flash your own. `TODO-owner`: what a software-only reward would include.

**Where is it made?** Designed in the UK. The Cardputer ADV is made by M5Stack and is not made in Britain.

**Where will you ship, and what about VAT?** `TODO-owner`: after shipping and VAT advice.

**What is the price, and when will it ship?** Not set. Join the list at https://piblo.co.uk for honest updates.

**Is Piblo affiliated with Anthropic or M5Stack?** No.

**What if something goes wrong?** `TODO-owner`: replacement approach, after reading Kickstarter's policies.

---

## Creator

`TODO-owner`: name, bio, links. Say "Designed in the UK". Do not give a town, region or address.
