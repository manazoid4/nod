# Piblo: competitor list and Kickstarter day-1 playbook

Researched 9 Nov 2026 with open-websearch (DuckDuckGo engine; Bing and Brave failed). Kickstarter pages return 403 to fetchers, so campaign figures come from Kickstarter search snippets, BackerKit/BackerTracker, Kicktraq (via BackerGuardian), the Wayback Machine, or the creators' own posts.

Labels: **[S]** = sourced (URL given). **[E]** = my estimate or inference. Prices are in the currency stated at the source; I have not converted unless marked.

---

## 1. Competitor table (22 rows)

### A. Closest to Piblo (pocket ESP32 and AI-approval devices)

| # | Name | What it is | Price (source) | Crowdfunding | Sub? | Open source? | Main pitch | URL |
|---|---|---|---|---|---|---|---|---|
| 1 | **M5Stack Cardputer ADV** | Card-sized ESP32-S3, 56-key keyboard, 1.14" 240x135 LCD, 1,750 mAh. This is the hardware Piblo v1 runs on. | US$29.99 on M5Stack store/AliExpress [S: cnx-software.com/2025/10/23/m5stack-cardputer-adv-esp32-s3-computer-gains-improved-antenna-larger-1750-mah-battery-es8311-audio-codec/]. UK price (Pi Hut) not retrieved (HTTP 429). | None for the ADV. Original Cardputer 2023 was a normal retail launch [E]. | No | Yes (docs, schematics) | "Pocket programmable computer"; Anthropic named Cardputer as a recommended agent-device board [S: cnx-software.com/2026/05/16/anthropics-open-source-claude-desktop-buddy-turns-esp32-s3-devices-into-interactive-ai-desk-companions/] | https://shop.m5stack.com/products/m5stack-cardputer-adv-version-esp32-s3 |
| 2 | **Kode Dot** | Pocket maker device: 2.13" AMOLED touch, ESP32-P4+C5, NFC/IR, kodeOS app launcher | KS base US$129 + $15-40 shipping; now store GBP149 "Standard Backer Edition" [S: backerguardian.com/campaign/kode-dot; kode.diy/product/kode-dot] | **Kickstarter**, 4 Nov-23 Dec 2025: live $1,751,547 / 8,646 backers [S: backerguardian.com, Kicktraq]; with late pledges about $2.75M / 13.3k [S: tcf.team case study]; Kode itself says EUR2,943,475 / 16,144 [S: kode.diy/news/kode-dot-kickstarter-campaign-story]; KS page now shows 16,193 backers, $3,366,566. Figures differ by source and date. | No | Yes (Apache-2.0/GPL-3.0) | "Breadboard replacement in your pocket" | https://www.kickstarter.com/projects/kode/kode-dot-the-all-in-one-pocket-size-maker-device/ |
| 3 | **M5Stack CardputerZero** | Credit-card Linux computer (Pi CM0), 46-key keyboard, 1.9" LCD | Super Early Bird US$59 Lite / US$89 full; MSRP $99/$149 [S: shop.m5stack.com/pages/m5-cardputerzero] | **Kickstarter** 26 May-3 Jul 2026: 13,644 backers, HK$14,960,226 (about US$1.91M) on HK$78,500 goal [S: gearinhere.com/intelligence/cardputerzero] | No | Yes | "Pocket Linux lab", mentions running AI agents on it | https://www.kickstarter.com/projects/m5stack/cardputerzero |
| 4 | **M5Stack StackChan** | ESP32-S3 AI desktop robot, cute face, voice assistant | US$59 early, US$65 Super Early Bird (72 h); first 1,000 reservations from US$47 [S: cnx-software.com/2026/01/13/m5stack-stackchan-is-a-cute-open-source-ai-desktop-robot/; shop.m5stack.com/pages/m5stack] | **Kickstarter** Jan 2026: 4,142 backers, HK$3,582,197 (about US$460k at 0.1275) on goal about US$10k [S: kickstarter.com/projects/m5stack/stackchan-the-first-co-created-open-source-ai-desktop-robot; backerkit.com] | No | Yes (100%) | "Co-created open-source AI desktop robot" | link above |
| 5 | **Anthropic Claude Desktop Buddy** | Official open-source firmware + BLE API: ESP32 desk pet shows Claude Code permission prompts, approve/deny with buttons, mood/XP-style states ("level up every 50K tokens") | Free firmware; runs on M5StickC Plus (about US$30) [S: cnx-software.com 2026/05/16 article above] | None | No | Yes (github.com/anthropics/claude-desktop-buddy) | "Approve Claude's actions from a physical button" | https://github.com/anthropics/claude-desktop-buddy |
| 6 | **Vibe Desktop Buddy** (independent seller) | Pre-flashed M5StickS3 running Anthropic's Buddy firmware | US$110 pre-order, ships "summer 2026" [S: claude-desktop-buddy.com] | None; own pre-order page with email list | No | Firmware open | "Approve or deny with a physical button" | https://claude-desktop-buddy.com/ |
| 7 | **Starbond Vox** | DIY ESP32-S3 Claude desk pet: tool approval, token feeding, mood hearts, levels to Lv.255 | Avg pledge US$175.50 [S: backerkit.com/projects/starbond/starbond-vox-a-physical-ai-companion-for-your-desk] | **Kickstarter**: only 22 backers, US$3,861 on US$3,000 goal [S: same BackerKit page]. Nearly the same idea as Piblo, and it barely moved. | No | Partly (APIs promised) | "Physical AI companion for your desk" | https://www.kickstarter.com/projects/starbond/starbond-vox-a-physical-ai-companion-for-your-desk |
| 8 | **DIY approval boxes** (clawd-approval-device, claude-code-remote, M5 Core2 console) | GitHub hobby projects: ESP32 + buttons to approve/deny Claude Code tool calls | Free (about US$20-30 hardware) [S: github.com/PapaFuchs84/clawd-approval-device; github.com/CVSRohit/claude-code-remote; bizstack.tech] | None | No | Yes | "Physical approve/deny for agents" | github links |
| 9 | **LilyGo T-Deck Plus** | ESP32-S3 BlackBerry-style handheld: QWERTY, 2.8" screen, LoRa, GPS, 2,000 mAh | About US$81.48 on AliExpress (Aug 2024) [S: cnx-software.com/2024/08/30/lilygo-t-deck-plus-...] | None | No | Yes (Meshtastic etc.) | Off-grid messenger / dev kit | https://lilygo.cc/products/t-deck-plus-1 |
| 10 | **Xiaozhi AI (ESP32 voice bots)** | Open-source ESP32 voice assistant firmware plus many cheap kits; talk to DeepSeek/Qwen etc. | Keyestudio kit US$38.68 [S: keyestudio.com/collections/ai-chatbot] | None (community/Chinese kit market) | Free service tier [E] | Yes | Cheap talking AI gadget | https://xiaozhi.dev/en/docs/ |
| 11 | **Seeed SenseCAP Watcher** | ESP32-S3 "physical AI agent" with camera, voice, LLM | Super early bird US$79 (about 20% off retail), 3-day launch offer from $79 [S: hackster.io/news/seeed-studio-s-sensecap-watcher-...; seeedstudio.com blog 2024/09/12] | **Kickstarter** Sep-Oct 2024: 531 backers, US$73,900 on US$10k goal, Project We Love [S: kickstarter.com/projects/seeed/sensecap-watcher-...; backerkit.com] | No | Open-source claimed | "Physical AI agent for spaces" | https://www.kickstarter.com/projects/seeed/sensecap-watcher-open-source-ai-assistant-for-smarter-spaces |
| 12 | **Flipper Zero** | Pocket pentest/radio multitool with a pet dolphin and XP | KS Early Bird US$119 (30% off US$169 est. retail) [S: Wayback copy of KS page]. Current retail price not verified. | **Kickstarter** 30 Jul-29 Aug 2020: 37,987 backers, US$4,882,784 on US$60k goal; US$1M on day 1 [S: backerkit.com/projects/flipper-devices/...; hackaday.io/project/170875/logs] | No | Yes | "Tamagotchi for hackers" | https://www.kickstarter.com/projects/flipper-devices/flipper-zero-tamagochi-for-hackers |

### B. AI voice/wearable devices (what buyers compare Piblo to)

| # | Name | What it is | Price (source) | Crowdfunding | Sub? | Open source? | Main pitch | URL |
|---|---|---|---|---|---|---|---|---|
| 13 | **Rabbit R1** | Handheld AI "agent" box (Teenage Engineering design) | US$199 [S: layer3labs.io/comparisons/humane-ai-pin-alternatives] | None (venture funded) | No | No | Pocket AI agent that uses apps | https://www.rabbit.tech |
| 14 | **Humane AI Pin** | Wearable pin with laser display | US$699 + US$24/month; discontinued 28 Feb 2025, cloud shut down, HP paid about US$116M [S: layer3labs.io same page] | None | **Yes**, mandatory | No | Replace the phone | n/a (dead) |
| 15 | **Plaud NotePin** | Wearable voice recorder with AI summaries | US$159; free 300 min/month plan, paid tiers above [S: store.comu.com/blogs/news/plaud-pricing] | None [E] | Optional tiers | No | Meeting notes | https://www.plaud.ai |
| 16 | **Bee** (Amazon-owned) | Cheap wearable voice-memory pendant | US$49.99; Amazon acquired Jul 2025 [S: layer3labs.io] | None [E] | Not stated | No | Cheapest always-listening note taker | https://www.bee.computer |
| 17 | **Limitless Pendant** | Always-on recorder | US$99; Meta bought Limitless, sales stopped 5 Dec 2025 [S: sekin.in/meta-acquires-limitless-...] | None | Was paid [E] | No | Searchable life memory | gone |
| 18 | **Friend pendant** | Always-listening "AI companion" necklace | US$249 [S: layer3labs.io] | None [E] | No | No | Companion that texts you | https://friend.com |
| 19 | **Omi (Based Hardware)** | Open-source AI pendant | US$169 one-time, free app, no subscription needed [S: omi.me/pages/pendant]; layer3labs lists US$179 | None found | No (paid tiers optional) | **Yes** | Open-source memory pendant | https://www.omi.me |

### C. One-press-action and desk-display angle

| # | Name | What it is | Price (source) | Crowdfunding | Sub? | Open source? | Main pitch | URL |
|---|---|---|---|---|---|---|---|---|
| 20 | **Elgato Stream Deck MK.2** | 15 programmable LCD keys for one-press actions | From GBP109.99 UK [S: pricespy.co.uk/product.php?p=5827120] | None | No | No (plugin SDK) | One tap triggers any action | https://www.elgato.com/uk/en/p/stream-deck-mini |
| 21 | **Tidbyt (Gen 1 and Gen 2)** | Retro pixel desk display, app store | Not retrieved | **Kickstarter** Gen 1: 5,106 backers, US$918,844 on US$40k goal; Gen 2 (Oct-Nov 2023): US$963,083 [S: backerkit.com/projects/tidbyt/retro-display; .../tidbyt/gen2] | No | Apps open (Pixlet) [E] | Glanceable info on desk | https://tidbyt.com |
| 22 | **Flipper One / "Interrupt"** (Linux Flipper alternatives) | Next-gen Linux pocket tools; Flipper One expected US$300+ | [S: cnx-software.com 2026/05/25 CardputerZero article] | Crowdfunding | No | Yes | Pocket Linux hacking | n/a |
| 23 | **Lapis One (Pamir)** | Coaster-sized Linux box for AI agents: Rockchip RK3576 (6 TOPS NPU), 8 GB LPDDR5, 64 GB storage, Sharp memory LCD, 3,300 mAh (about 4 h), **Agent KVM** USB-C port (captures another PC screen + fakes keyboard/mouse), Tailscale built in. **Closest rival to the planned Piblo Pro (same RK3576 + 8 GB + KVM idea).** | US$499 pre-order (US$599 later), ships Dec 2026 to US [S: yankodesign.com/2026/09/20/the-499-lapis-one-is-a-tiny-mac-mini-alternative-built-just-to-run-your-ai-agents/] | Pre-orders (not checked whether Kickstarter) | No | Not checked | "The agent's own computer" | https://www.yankodesign.com/2026/09/20/the-499-lapis-one-is-a-tiny-mac-mini-alternative-built-just-to-run-your-ai-agents/ |

Notes: row 7 and row 5/6 matter most. Anthropic itself shipped a free, open-source "Buddy" that already does approve/deny plus a pet with levels. Piblo is not first to the "approval + character" idea and must not pitch it as new.

---

## 2. Campaign playbook: what drove big early numbers

### 2.1 Kode Dot (Kickstarter, 4 Nov 2025, 49 days) - closest comp
- Goal set tiny: EUR4,387 (KS shows $5,000). "Funded in 5 minutes", next day Kickstarter gave "Project We Love" [S: kode.diy news story].
- Pre-launch: ran Meta ads, surveys and audience tests; agency (TCF) said data "showed interest but nothing pointed to a breakout" and set an internal target of about $500k [S: tcf.team/case-studies/kode-dot-case-study]. Day-1 backer count not published.
- Stretch goals: $100k IR, then reordered after backer comments to $250k NFC/RFID (agency says $300k) and $500k vibration motor, $1M ESP32-P4 upgrade, $2M ESP32-C5 swap. All applied free to every pledge [S: kode.diy story; tcf case study]. Reordering after a survey fixed slow conversion about day 10.
- Add-ons: hacker module, bundles, a KS-exclusive Transparent Edition, Black Friday/Cyber Monday/Christmas time-limited bundles. Average order value $190.71 [S: tcf].
- Tiers: base $129 (+ shipping), transparent about $132, LoRa bundle $149 [S: backerguardian.com]. An exact "super early bird" price was not retrievable.
- Audience: Instagram grew to 64k followers, several reels over 1M views, 17.7M paid impressions, ROAS about 3.77, new creative every 4-5 days. Founders answered on Reddit and GitHub daily. Volos Projects (115k YouTube subs) reviewed within a week. Number-1 "Popularity" on Kickstarter for a week [S: tcf; kode.diy].
- Takeaway: it did NOT start with a big list. It won by a tiny goal, fast funded badge, stretch goals voted by backers and nonstop founder-made short video. It also paid an agency, which Piblo cannot.

### 2.2 Flipper Zero (Kickstarter, 30 Jul-29 Aug 2020) - best day-1 result
- US$1M on day 1; final US$4.88M, 37,987 backers on a US$60k goal [S: hackaday.io/project/170875/logs; backerkit.com].
- Tiers: Early Bird US$119 = 30% off US$169 retail, 32,922 backers took it (the "Limited" label never really sold out); US$129 Kickstarter Special, 1,431 backers; 2x Early Bird US$232, 2,155 backers [S: Wayback Machine copy of the KS page, web.archive.org/web/20200829133959/...].
- Stretch goals: $100k new colours, $300k Bluetooth LE, $700k NFC, all unlocked next day; then SD slot confirmed [S: hackaday.io logs].
- Pre-launch: project was public on Hackaday.io for months with logs, 3D models on GitHub, a "Developer Program" (500+ applicants) and a Discord, opened during the campaign [S: hackaday.io logs]. Pre-launch list size not published; the founder had an existing hacker/Twitter following [E].
- Takeaway: very low entry price for a big audience, hacker-community credibility from open work, and stretch goals that cost little but felt big.

### 2.3 M5Stack CardputerZero (Kickstarter, 26 May-3 Jul 2026) - best recent keyboard-pocket comp
- Pre-launch: over 5,000 "notify me" Kickstarter followers; a **US$1 reservation** on M5Stack's site (via PledgeBox) locked the Super Early Bird price; Facebook group, Discord, email list; one snapshot of the page said "432 people have already secured their spot" (undated) [S: cnx-software.com/2026/05/25/...; shop.m5stack.com/pages/m5-cardputerzero].
- Pricing: SEB US$59 / US$89 vs MSRP US$99 / US$149 (40% off) [S: same].
- Result: US$1.62M and 12,014 backers with 23 days left (about day 15) and the $1M stretch reached [S: gizmocrowd.com/post/cardputer-zero-review]; final 13,644 backers, HK$14.96M [S: gearinhere.com].
- Goal set about US$10k; creator also had a prior hit (StackChan) and a huge existing Cardputer owner base [S: gizmocrowd].

### 2.4 M5Stack StackChan (Kickstarter, Jan 2026) - open-source AI companion
- VIP reservation: first 1,000 reservations from US$47, then US$59; launch SEB US$65 for the first 72 hours [S: shop.m5stack.com/pages/m5stack; technews12.com].
- Open repos (JS/TS firmware, KiCad, apps) published before launch from a years-old community project [S: cnx-software.com/2026/01/13/...].
- Result: 4,142 backers, HK$3.58M. One blog claims US$140k on day 1 [S: aixtoy.com/blog/ai-toy-tutorials/6904.html, secondary and unverified].

### 2.5 SenseCAP Watcher (Seeed, Sep-Oct 2024)
- 3-day "Launch Special" from US$79 (20% off). 531 backers, US$73,900. Good comp for the "AI agent hardware" ceiling when the maker has no maker-community crowd [S: seeedstudio.com blog; backerkit.com].

### 2.6 Cautionary: Starbond Vox
- A near-identical "Claude desk pet with tool approval" had only 22 backers, US$3,861 [S: backerkit.com page]. The idea alone does not sell; the audience does.

### 2.7 Tidbyt (2019 and 2023)
- 5,106 backers, US$918,844 (Gen 1); US$963,083 Gen 2. Shows a desk-glance gadget can reach about US$1M with a design-led story [S: backerkit.com].

### 2.8 General follower-to-backer figures (weak sources, treat as rough)
- One Reddit creator reported about 25% of pre-launch followers had backed after one week live [S: reddit.com/r/kickstarter/comments/1dkjtqf/ (snippet only)].
- Gizmocrowd quotes pre-launch followers back at 32% vs 17% for others [S: gizmocrowd.com/post/building-anticipation-before-kickstarter-launch, snippet only, unverified].
- Kickstarter's pre-launch page never gives you the follower emails; guides advise a separate owned list [S: waitlister.me/growth-hub/guides/kickstarter-pre-launch-page].

### 2.9 Realistic day-1 expectation for Piblo [E]
If 15-30% of a warm list backs on day 1, then 1,000 subscribers gives about 150-300 backers, 3,000 gives about 450-900. Flipper/Kode-scale (10k+) needs a creator or press moment, not a list alone. I would plan on 1,500-3,000 combined waitlist + Kickstarter followers and a day-1 target of 300-600 backers. This is my arithmetic, not a sourced benchmark.

---

## 3. Cheap tactics for Piblo (all under the GBP300 budget)

1. **Two lists, not one.** Kickstarter pre-launch page (free, shows follower count after 10) plus piblo.co.uk email waitlist you own. Email the waitlist at the same minute the campaign goes live [S: waitlister guide].
2. **Refundable "reserve your early-bird" step.** CardputerZero locked prices with a US$1 reservation and had 5,000+ followers. Piblo can copy it cheaply: "reserve" on the site (no payment, or GBP1 via a free-tier tool) and promise the early-bird price in the launch-day email. Reservation counts also give social proof [S: cnx-software; M5Stack page].
3. **Tiny funding goal so "funded in minutes" happens.** Kode (EUR4,387), CardputerZero (HK$78,500), Flipper (US$60k), StackChan (US$10k). Gets the funded badge, Project We Love chance and Kickstarter Popularity ranking in the first hours. Pick a goal your list can hit in hour one, backed by a real production plan.
4. **Big, honest early-bird tier at 30-40% off.** Flipper 30% off, CardputerZero 40% off, SenseCAP 20% off. Fit to Piblo: if standard is about GBP99, launch Early Bird at about GBP69-79 for the first 72 hours or first N units; keep a "Founder's aluminium" tier as the upsell. Do not label it "limited" unless it truly sells out (Flipper's never did).
5. **Stretch goals that upgrade every unit for free**, ordered by backer vote. Kode fixed a stall by surveying comments and moving NFC down. Ask the waitlist in advance which 3 upgrades they want (for Piblo maybe: haptic buzz, IR/remote, Mac/Linux Core, more Buddy characters).
6. **Open the repos and a Discord before launch.** Flipper (Hackaday logs, GitHub 3D models, dev programme) and StackChan (public repos) both built trust before asking for money. Piblo being open source with free models is the proof.
7. **Founder short video, not ads.** Kode's winners were founder-on-camera reels (several over 1M views) and a Reddit presence. Post 2-3 short real-use clips a week from now: hold key, talk, approve a Claude Code action. Free.
8. **Free press and creator seeding.** CNX Software covered Kode, StackChan, CardputerZero and Claude Buddy; Hackster covered Kode and Claude Buddy-style builds. Send each a short kit (spec, GIF, pricing) at launch minus 48 h. Send 3-5 small relevant YouTubers a unit; several of Kode's creators kept units and posted unpaid [S: tcf].
9. **Ride the Anthropic Buddy wave honestly.** Anthropic's open BLE protocol, its recommendation of Cardputer, and Buddy's hardware-guide coverage make "works with Claude Code approvals" a free search topic. Support that protocol too, and say so. Also list on r/ClaudeAI, r/esp32, r/M5Stack, r/selfhosted, Hacker News "Show HN" [E: channels, not tested].
10. **Time it.** Kode launched 4 Nov and used Black Friday/Christmas bundles without heavy ad spend; ad costs spike late Oct onward [S: tcf]. Today is 9 Nov 2026, so a late January-March 2027 launch avoids Q4 noise [E].

---

## 4. Where Piblo can win (gaps)

1. **A keyboard-first approval device.** Anthropic Buddy and Vibe Buddy have two buttons and only talk to the Claude desktop app over BLE. Piblo has a keyboard, a voice key, webhooks and works with any agent, not just Claude. Nobody sells "approve/reject AI agent actions from any agent, with a key press" as a finished product.
2. **One-press reminders (yes / no / later).** None of the 22 rows does this. It is the non-developer hook, and it is what Stream Deck-style buyers understand.
3. **No subscription, free models, your own PC.** Plaud/Humane/Limitless trained buyers to expect monthly fees and cloud lock-in, and two of those are now dead. "Voice notes saved to your own PC, nothing in our cloud" is a clear contrast. Omi is the only open competitor and it needs a phone app.
4. **A character plus XP/streaks on a real-key device.** Flipper proved a mascot sells to hackers; Buddy proves developers like a pet. Piblo Buddy can go further (streaks, reminders).
5. **UK-first.** GBP pricing, UK-based support and no US import fuss. All big comps price in USD/HKD and ship from China or the US [E: not tested for duty costs].
6. **Price sits in a gap.** Cardputer ADV is about US$30 and Vibe Buddy is US$110; Rabbit US$199. Piblo at GBP79-129 must justify itself on finished software, not hardware.

### Risks to be straight about
- **Hardware is a US$30 board.** Hobbyists can flash Piblo themselves; the Kickstarter must sell the experience, polish and support (Founder's aluminium, ready-flashed, warranty).
- **Windows-only Piblo Core** shrinks the market; Kode/Flipper had no PC dependency. Mac/Linux Core is a natural stretch goal.
- **Anthropic is a platform competitor.** Its official Buddy is free; differentiate on any-agent, keyboard, voice, reminders.
- **Starbond Vox (22 backers)** shows that "Claude pet with approval" alone does not fund. Audience and video do.
- **AI hardware trust is low** after Humane and Rabbit; avoid hype, show working demos, state limits (as Kode's founders did on Reddit).
- Kode Dot's own page notes delivery slips and spec changes after the campaign; plan fulfilment honestly.

---

## Not checked / gaps
- Pre-launch list sizes: only CardputerZero (5,000+) is sourced. Flipper's, Kode's and StackChan's are not published.
- Exact day-1 backer counts for Kode, CardputerZero, StackChan not found; only Flipper (US$1M) and Kode ("5 minutes").
- Kode Dot super-early-bird price and the Kickstarter reward pages for Kode/CardputerZero (403). 
- UK retail price of Cardputer ADV (Pi Hut returned 429), current Flipper price, Tidbyt price, Bee/Friend/Rabbit prices from official sites (secondary sources only).
- Whether Bee, Plaud, Friend ran any crowdfunding: assumed none [E].
