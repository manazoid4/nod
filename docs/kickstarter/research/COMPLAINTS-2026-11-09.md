# Research B: what users and backers complain about in Piblo's competitors

Date: 9 Nov 2026. Method: open-websearch (DuckDuckGo) plus page fetches. No posting, no sign-ups.

## Read this first: evidence quality

- Reddit, Kickstarter comments and Facebook blocked my fetcher (Reddit returned an empty page; Kickstarter needs a browser). Where a complaint comes from a Reddit thread, I saw only the search snippet, or a third party quoting it. I mark those "(snippet)" or "(via X)".
- Kode Dot has NO direct backer comments in this report. Its complaints come from two secondary articles (ic.work, BackerGuardian) plus Kode's own news page. Treat Kode Dot findings as thin. The best next step is a human reading the Kickstarter comments tab and r/KodeDot by hand (10 minutes).
- Several review sites (sekin.in, sortwell.net, layer3labs.io, tldv.io) are SEO or affiliate sites. I used them for facts that match other sources and flagged them. Primary or reputable sources: Engadget, Fortune, TechCrunch, ZDNET, SlashGear, Kickstarter's own blog, M5Stack's community forum, Kode's own site.
- Frequency key: "1" = one mention found. "Few" = 2 to 3 independent mentions. "Many" = repeated pattern across sources.
- Cost key: FREE = costs nothing but time. MONEY = needs spend.
- Where Kode's numbers conflict, I show both. Kode's own page says 16,144 backers and 2,943,475 euros. BackerGuardian (quoting Kicktraq) says 8,646 backers and $1,751,547. ic.work says 15,580 and $3.23m. I cannot tell which is right. This is itself a trust lesson: publish one number and link the source.

---

## 1. Kode Dot (top priority)

| # | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|
| K1 | Ship date slipped from July to September 2026. Annoyance was less the delay than that earlier updates said "on track" right before it. | Few (one article citing Reddit; BackerGuardian confirms July window expiring with no confirmed deliveries on 27 Jul) | https://www.ic.work/article/kode-dot-kickstarter-backer-count-discrepancy-delay and https://backerguardian.com/campaign/kode-dot | Communication rule: never say "on track" for a gate not yet passed. Publish a dated milestone list with "done / at risk / late" labels, and announce a slip the day you know, with the reason and a new date with a buffer. | FREE |
| K2 | Product changed after the campaign: ESP32-S3 became P4 plus C6, later C5. Enclosure redesigned. Kode's site labels the campaign video "OLD DESIGN" and says that version will not be sold. | Few (BackerGuardian; Kode's own story page confirms the chip swaps as stretch goals) | https://backerguardian.com/campaign/kode-dot and https://kode.diy/news/kode-dot-kickstarter-campaign-story | Freeze the spec before launch. Show only photos of the real unit. Put "what you will receive" in one box on the campaign page, and note anything that may change plus how you will tell backers. | FREE |
| K3 | Docs lag the product. Official docs still said "ESP32-S3" on 27 Jul 2026 after the chip changed. | 1 | https://backerguardian.com/campaign/kode-dot | Docs are a release gate: no firmware release without matching docs. Keep a public changelog. | FREE |
| K4 | Headline "hacker" features (Sub-GHz, GNSS) need a separately bought Hacking Module. Product page mentions it quietly. Reviewers say it is not a turnkey Flipper replacement. | Few (ic.work and BackerGuardian agree) | https://www.ic.work/article/kode-dot-kickstarter-backer-count-discrepancy-delay | State "What you need to bring / buy" at the top. For Piblo: Windows PC running Piblo Core, same Wi-Fi, a Cardputer ADV (if not bundled). Show total cost in pounds. | FREE |
| K5 | Marketing numbers rounded up ("16,000 backers" vs 15,580 on trackers) and conflicting totals between sources. Small, but read as sloppy by sceptics. | 1 (a single article) | https://www.ic.work/article/kode-dot-kickstarter-backer-count-discrepancy-delay | Quote exact figures with a source link. Never round up. | FREE |
| K6 | Not turnkey: full use needs coding (Arduino/C++). Non-programmers should wait. | Few (513.toys via BackerGuardian; same theme for Cardputer) | https://backerguardian.com/campaign/kode-dot | Piblo's pitch is "press a key and talk". Lead with 5 no-code things it does out of the box and show a 2-minute first-run video. | FREE |
| K7 | Price jump and wait: $129 backer price, shop price $199, next batch January 2027. | 1 | https://backerguardian.com/campaign/kode-dot | State planned retail price on the campaign page so early backers can see their saving, and say how late-pledge and post-campaign orders ship. | FREE |
| K8 | "Open source" is partial: firmware is public (Apache-2.0 / GPL-3.0) but hardware design files were not visible. | 1 | https://backerguardian.com/campaign/kode-dot | If Piblo says open source, publish firmware, Core and (if possible) the case files and wiring/BOM on day one. List exactly what is open. | FREE |

Fair note for balance: BackerGuardian scores Kode's communication 80/100 and Kode posts roughly monthly production updates (https://kode.diy/news). Regular updates did not stop the sting of a slip announced after "on track" messages. Frequency is not the same as honesty about risk.

---

## 2. M5Stack Cardputer / Cardputer ADV (Piblo's base hardware, so these are Piblo's weaknesses)

I found no sourced complaints about speaker loudness, case durability or screen quality specifically for the ADV. Reviewers call the keyboard "surprisingly usable" (ZDNET) and the screen "surprisingly readable". Absence of evidence is not proof, so test these ourselves.

| # | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|
| C1 | ADV keyboard dead after flashing: ADV reads the keyboard through an I/O multiplexer, so older Cardputer apps and firmware do not work on it. A new user thought they had broken it. | Few (forum thread with 9.9k views; repeated in ADV firmware chatter) | https://community.m5stack.com/topic/7940/having-problems-with-my-cardputer-adv | Web flasher that detects ADV vs original and refuses the wrong build. Label "ADV only" everywhere. First-run screen: "Keyboard not responding? Reflash here". | FREE |
| C2 | Brand-new ADV died on first charge with a spark and burning smell on a USB-C charger the user had used before. Also dreaded "waiting weeks" for a replacement. | 1 (safety issue, so weigh it above its count) | https://community.m5stack.com/topic/7977/brand-new-cardputer-adv-fails-on-first-charging | Safety page: recommended chargers (5V only), no fast-charge/PD warning, and a fast replacement promise. Inspect and bench-test every unit's first charge before shipping. | FREE (advice); MONEY (testing each unit) |
| C3 | Charging not documented: the device must be switched on to charge fully. Plugged in while off it trickle-charges or stalls. Reviewer lost several charge cycles. (Original Cardputer; check ADV.) | 1 (but a classic) | https://nepamesh.com/m5stack-cardputer-review/ | Put one line in the quick-start card and on screen: "Charging: leave on / off". Test ADV and state the truth. | FREE |
| C4 | Battery life average: about 6 to 8 hours in normal use (original). For ADV, 1,750 mAh is bigger but no one has published a controlled runtime test. | Few | https://nepamesh.com/m5stack-cardputer-review/ and https://sekin.in/m5stack-cardputer-adv-review-a-pocket-esp32-s3-tool-not-a-tiny-laptop/ | Measure and publish hours for Piblo's real modes (idle, listening, Wi-Fi on, screen dim). Add aggressive sleep, wake on key press, a "battery saver" mode. Promise a number we have measured. | FREE (engineering) |
| C5 | Battery drained fast when running a Bluetooth keyboard program, and the device boots when plugged in so the program keeps running while you try to charge. | 1 (snippet only; Reddit blocked) | https://www.reddit.com/r/M5Stack/comments/1b0ha4r/how_long_does_your_cardputer_last_on_battery/ | Charging mode: when USB power is sensed while off, show charging screen and do not start the radio. Show battery percentage and "time left" on the home screen. | FREE |
| C6 | Battery is proprietary. A Facebook group member says M5Stack will not sell a replacement. | 1 (Facebook snippet) | https://www.facebook.com/groups/960129956410838/posts/1023291236761376/ | Document how to replace the cell and which spec. Offer a "run on USB power bank" tip. Consider a spare-battery add-on. | FREE (docs); MONEY (spares) |
| C7 | Keyboard is cramped: key pitch is tight enough that typos are frequent for larger hands. Long typed text gets tedious. | Few (nepamesh; saipien lists "small keyboard" limits; ZDNET disagrees, calling it usable) | https://nepamesh.com/m5stack-cardputer-review/ | This supports Piblo's "hold a key to talk" design: voice for long input, keys only for yes/no/later. Say so openly. Add key-repeat and shortcut keys for common replies. | FREE |
| C8 | Steep learning curve and driver friction: M5Burner took fiddling, Mac users needed a driver, community firmware needs manual tweaks. | Many (ZDNET, saipien) | https://www.zdnet.com/article/m5stack-cardputer-adv-review/ and https://saipien.org/m5stack-cardputer-adv-review-pocket-pc-for-edge-ai-agents-prototyping-field-demos/ | One-click Windows installer for Piblo Core plus a browser-based flasher. Test the first-run path on a non-technical person and time it (target under 10 minutes). | FREE |
| C9 | Limits against Flipper: IR is transmit-only, no sub-GHz, no NFC/RFID, cannot act as a USB keyboard. | Many (ZDNET) | https://www.zdnet.com/article/m5stack-cardputer-adv-review/ | Do not compete here. Say plainly: "Piblo is not a hacking tool." Avoid a Flipper-style comparison table. | FREE |
| C10 | Audio is poorly documented. Users ask how to use the speaker; a Home Assistant user could not get the microphone working; a Facebook user asks which pins the ADV's ES8311 audio chip uses for push-to-talk. | Few (all snippets) | https://www.reddit.com/r/CardPuter/comments/1algq9z/how_use_speaker/ and https://community.home-assistant.io/t/did-some-work-on-the-m5stack-cardputer-public-yaml-still-no-progress-on-the-microphone-sadly/866914 and https://www.facebook.com/groups/276059605530869/posts/744268498709975/ | Publish Piblo's working audio code, pinout and sample rates as a reference. This also makes Piblo the go-to project for ADV voice. A community project (Cardmic, https://github.com/Yueze/Cardmic) already uses the Cardputer as a hold-to-talk USB mic, which shows demand. | FREE |
| C11 | LoRa is not built in. It is an add-on module stacked on top, and the screw fix was found on Reddit, not M5Stack docs. | 1 | https://nepamesh.com/m5stack-cardputer-review/ | Piblo does not use LoRa; keep it that way. Lesson: put every "gotcha" in the box insert, not a forum. | FREE |
| C12 | "Prototype not product": needs plans for OTA updates, signed firmware and long battery testing before real deployment. | 1 | https://saipien.org/m5stack-cardputer-adv-review-pocket-pc-for-edge-ai-agents-prototyping-field-demos/ | Ship OTA updates over Wi-Fi from Piblo Core with signed images and a safe fallback partition. | FREE (engineering) |
| C13 | Tiny screen (1.14 inch, 240x135) limits what you can show. | Few | https://sekin.in/m5stack-cardputer-adv-review-a-pocket-esp32-s3-tool-not-a-tiny-laptop/ | Design for glanceable cards: one sentence, 3 big choices. Test in daylight. Put long text on the PC. | FREE |

---

## 3. LilyGo T-Deck (thin evidence)

| # | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|
| T1 | Examples break when libraries auto-upgrade; LilyGo tested against arduino-esp32 2.0.14 and warns upgrades cause incompatibilities. | 1 (affiliate site paraphrasing LilyGo docs) | https://sekin.in/lilygo-t-deck-support-setup-upload-and-troubleshooting/ | Pin versions. Ship a lockfile and a tested toolchain. State "tested with X". | FREE |
| T2 | Pin conflicts: some examples reserve pins also used by trackball or other peripherals. | 1 | https://sekin.in/lilygo-t-deck-support-setup-upload-and-troubleshooting/ | Keep a pin map in the repo and a CI check against double use. | FREE |
| T3 | T-Deck Plus has a "Touch Fix Record" and "touch repair" discussion in the maker's own repo, so there were touch defects. (I did not read the thread.) | 1 | https://github.com/Xinyuan-LilyGO/T-Deck/blob/master/firmware/README.MD | Publish a known-issues list with fixes, rather than burying it. | FREE |

---

## 4. Flipper Zero

| # | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|
| F1 | Firmware development slowed after 1.0 once the Kickstarter promises were done. Community accused the maker of abandoning it. In July 2026 they promised GitHub voting, weekly review and public tests. | Many (over a million users, "sustained" criticism) | https://securebulletin.com/flipper-zero-maker-overhauls-firmware-contribution-rules-after-community-backlash/ | Publish a maintenance promise: bug-fix releases for N years, public roadmap, public issue tracker with weekly triage. | FREE |
| F2 | Postage trouble: USPS treats the device as hazmat because of its battery, delaying delivery by a week or more. | Few (snippets) | https://www.reddit.com/r/flipperzero/comments/1bl10ky/shipping_delays/ | Plan battery-shipping rules (lithium) for UK/EU/US before launch and tell backers the likely delays. | FREE (planning) |
| F3 | Orders sat unshipped for weeks with no update. | 1 | https://forum.flipper.net/t/shipping-delays/23292 | Give each backer an order-status page with a stage (paid, built, packed, posted, tracking). | FREE (simple page) |
| F4 | Early battery life poor; the maker later claimed up to one month after firmware 0.82. | 1 (maker's own blog) | https://blog.flipper.net/1-month-battery-life-with-firmware-update/ | Battery fixes through firmware are possible; plan sleep tuning as an early update. | FREE |

---

## 5. Rabbit R1

| # | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|
| R1 | Promise vs product: launch demo showed an agent driving any app. On day one only four integrations (Uber, DoorDash, Spotify, Midjourney) existed, and Uber often failed. | Many | https://www.engadget.com/rabbit-r1-review-a-199-ai-toy-that-fails-at-almost-everything-161043050.html and https://www.layer3labs.io/gear/reviews/rabbit-r1 | Campaign promise: "What works on day one" list, with a 'planned, not promised' section clearly separate. Demo only what ships. | FREE |
| R2 | Terrible battery at launch; a fix a week after first deliveries reportedly improved it up to 5 times (snippet). | Many | https://www.engadget.com/rabbit-r1-review-a-199-ai-toy-that-fails-at-almost-everything-161043050.html | See C4: measure and publish before launch. | FREE |
| R3 | Voice requests misheard or ignored (asked for traffic, got weather; sometimes did nothing). Slow replies of roughly 8 to 15 seconds in one lab test. | Many (Engadget first-hand; the latency number is from a lower-trust site) | https://www.engadget.com/rabbit-r1-review-a-199-ai-toy-that-fails-at-almost-everything-161043050.html and https://sortwell.net/en/gadgets/rabbit-r1-review | Show instant feedback ("listening", "thinking", "got it") and a visible timer. Publish measured round-trip times on a home network. Use a fast free model by default. | FREE |
| R4 | Awkward controls (scroll wheel), tiny on-screen keyboard, useless 2-watt speaker. | Few | https://www.engadget.com/rabbit-r1-review-a-199-ai-toy-that-fails-at-almost-everything-161043050.html | Piblo's real keyboard is the advantage. Make the single-key flows (Y/N/L) the hero demo. | FREE |
| R5 | Fragile cloud logins: Spotify/Uber sessions expire or hang. | Few (lower-trust source) | https://sortwell.net/en/gadgets/rabbit-r1-review | Piblo's agent approvals run on a local PC, so say that: no stored third-party passwords on a cloud. | FREE |

---

## 6. Humane AI Pin

| # | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|
| H1 | Shut down 28 Feb 2025; servers off, device bricked; HP bought assets for about $116m. | Many (well documented) | https://www.slashgear.com/1794149/humane-ai-pin-shutdown-timeline-refund-details/ | Written pledge: "Piblo still works if our company disappears" (Core is open source and local). Publish the escrow or "last firmware" plan. | FREE |
| H2 | Refunds only for devices shipped in the last 90 days. Everyone else got nothing and was told to recycle it. | Many | https://www.slashgear.com/1794149/humane-ai-pin-shutdown-timeline-refund-details/ | Set a clear refund and guarantee policy in plain English before launch, including what happens if the company stops. | FREE (policy) |
| H3 | $24 a month subscription on top of $699 (later $499). | Many | https://www.slashgear.com/1794149/humane-ai-pin-shutdown-timeline-refund-details/ | Write "No subscription, ever, for core features" on the page and in the terms. Name exactly what free models cost (nothing) and what a paid model would cost, if the user chooses one. | FREE |
| H4 | Charging case recalled for overheating; poor battery life and sluggish responses. | Many | https://www.slashgear.com/1794149/humane-ai-pin-shutdown-timeline-refund-details/ | Same as C2: charger safety, third-party battery tests, recall plan stated up front. | FREE (plan) |

---

## 7. Plaud NotePin (also had a crowdfunding phase)

Most of this comes from one aggregator, tl;dv (a competitor selling a software notetaker, so slightly biased), which quotes Reddit threads. Reddit links are as listed by tl;dv; I did not open them.

| # | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|
| P1 | Hard to start or stop recording; touch controls finicky; "near impossible to trigger". | Many | https://tldv.io/blog/plaud-notepin-review/ (quotes https://www.reddit.com/r/PlaudNoteUsers/comments/1h8jurx/plaud_notepin_review_its_not_ready_for_prime_time/) | Use real, clicky keys and clear on-screen "REC" state with a beep. Piblo's hold-to-talk is a plus; test it for false triggers and add a short buzz or tone on start/stop. | FREE |
| P2 | Syncing fails; recordings do not appear or need an app restart. | Many | https://tldv.io/blog/plaud-notepin-review/ | Voice notes saved locally on the microSD first, then synced to the PC with retries and a visible "saved on device / saved to PC" tick. | FREE |
| P3 | A firmware update made it worse: one user said they got under a third of recordings after updating, and rolled back to an older device. | 1 (but a serious pattern) | https://tldv.io/blog/plaud-notepin-review/ | Staged firmware rollout, a beta channel, and one-key rollback to the last good version. | FREE |
| P4 | Support slow or ghosted ("two weeks since they expedited my request"). Hardware dying after 8 to 9 months. | Few | https://tldv.io/blog/plaud-notepin-review/ | Public support promise (e.g. reply within 2 working days), a UK contact, and a repair/replace policy. | MONEY (time and spares) |
| P5 | Shipping "awful" for some orders. Plaud's own backers complained about delays (one user said they missed 10 important meetings waiting). | Few | https://www.reddit.com/r/PlaudNoteUsers/comments/1819by2/frustrated_backer_re_shipping_delays/ (snippet) | See K1. Also pre-warn backers about customs/VAT on post-Brexit shipping (my inference; I have not sourced UK-specific complaints). | FREE |
| P6 | Subscription pressure: 300 free minutes a month, then $99.99 a year or $17.99 a month, and the app keeps pushing the upgrade. | Many | https://tldv.io/blog/plaud-notepin-review/ | Piblo: voice notes saved as audio on your PC, transcription with a free model or local Whisper. No upsell screens. Put "no ads, no upgrade nags" in the FAQ. | FREE |
| P7 | Battery shorter than expected (flat a couple of hours after a 30-minute meeting). | Few | https://tldv.io/blog/plaud-notepin-review/ | See C4. | FREE |

---

## 8. Bee (Amazon), Limitless, Friend

| # | Product | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|---|
| B1 | Bee | Always recording; needs location, photos, contacts, calendar and notification permissions; data stored in the cloud. TechCrunch reviewer would not want it recording their personal life. Amazon has not delivered a promised local-only version. | Many | https://techcrunch.com/2026/05/24/i-tried-amazons-bee-wearable-and-am-both-intrigued-and-slightly-creeped-out/ | Press-to-talk only; no always-on mic. Publish a one-page "what Piblo can see" list: nothing leaves your Wi-Fi unless you pick a cloud model. | FREE |
| B2 | Bee | Transcripts messy: speakers need manual naming and chunks are missing. | Few | https://techcrunch.com/2026/05/24/i-tried-amazons-bee-wearable-and-am-both-intrigued-and-slightly-creeped-out/ | Keep the raw audio file next to every transcript so users can check. | FREE |
| L1 | Limitless | Meta bought it on 5 Dec 2025, sales stopped the same day, the Rewind app stopped capturing on 19 Dec. | Many | https://limitlessalternative.com/what-happened | See H1: "works without us". | FREE |
| L2 | Limitless | Service ended immediately in the UK, EU and five other regions. Users there got two weeks to export before permanent deletion. Directly relevant to a UK launch. | Many | https://limitlessalternative.com/what-happened | Put "your data stays on your PC; delete or export any time" on the page. Never require an account. | FREE |
| L3 | Limitless | Support promised only "throughout 2026"; no word on 2027. Staying means accepting new terms. | Few | https://limitlessalternative.com/what-happened | Commit publicly to a support horizon (e.g. security fixes for 3 years). | FREE |
| FR1 | Friend | Barely heard the user; 7 to 10 second lag; sometimes disconnected or did not answer. The founder's reply to each point was "we're working on it". | Many | https://fortune.com/2025/10/03/friend-ai-necklace-review-avi-schiffmann/ | Never answer a review problem with "we're working on it" without a date. Publish a known-issues page with a fix date. | FREE |
| FR2 | Friend | Slow shipping: about 3,000 sold, only about 1,000 shipped, and the founder admitted users were upset. | Many | https://fortune.com/2025/10/03/friend-ai-necklace-review-avi-schiffmann/ and https://www.layer3labs.io/gear/reviews/friend-ai-necklace | Only take as many pledges as you can build. Print "units built / units shipped" on the update page. | FREE |
| FR3 | Friend | Public backlash against "always listening"; no audible consent chime for people nearby. | Many | https://fortune.com/2025/10/03/friend-ai-necklace-review-avi-schiffmann/ and https://www.layer3labs.io/gear/reviews/friend-ai-necklace | Recording indicator on screen and a short tone, and say "Piblo records only while you hold the key". | FREE |

---

## 9. General crowdfunded-hardware backer complaints

| # | Complaint | How common | Source | Piblo fix | Cost |
|---|---|---|---|---|---|
| G1 | Shipping late is the norm: one study of 288 funded Kickstarter projects found 61 percent shipped late. Another estimates 5 to 14 percent never deliver. Realistic window from campaign end to last reward is about twelve months for overseas manufacture. | Many | https://updates.kickstarter.com/why-kickstarter-campaigns-fail-after-funding-and-how-to-avoid-it/ | Quote a date with slack built in at every stage (funds, manufacture, freight, customs). Aim to deliver early. | FREE |
| G2 | Worst trust damage comes when dates pass with no explanation or no updates are sent. Backers forgive delays when they understand them. | Many | https://updates.kickstarter.com/why-kickstarter-campaigns-fail-after-funding-and-how-to-avoid-it/ and https://updates.kickstarter.com/how-to-communicate-kickstarter-delays-without-losing-backer-trust/ | Fixed update rhythm (e.g. every second Friday) even if the news is "nothing changed". | FREE |
| G3 | Under-budgeted shipping and fulfilment; complicated stretch goals multiply the number of items to build and ship (Coolest Cooler: more than 20,000 backers never got a unit; FunForge absorbed about $250k and ran three years late). | Many | https://updates.kickstarter.com/why-kickstarter-campaigns-fail-after-funding-and-how-to-avoid-it/ | Few tiers; no stretch goals that change hardware; get written shipping quotes first, add a 20 to 30 percent contingency. | FREE |
| G4 | Only about 30 percent of tech projects deliver on time or within six months; about 40 percent deliver nothing. (Older academic figure, more pessimistic than Kickstarter's own.) | Many | https://ictinstitute.nl/fulfilment_rate_crowdfunding/ | Show a prototype-to-production proof: 50 hand-built units already tested by outsiders. | FREE |
| G5 | Abandoned software after delivery (Humane, Limitless, Flipper firmware stagnation). | Many | see H1, L1, F1 | Open source plus a support-horizon pledge. | FREE |

---

## Count check

- Sourced complaints: K1-K8 (8), C1-C13 (13), T1-T3 (3), F1-F4 (4), R1-R5 (5), H1-H4 (4), P1-P7 (7), B1-B2 (2), L1-L3 (3), FR1-FR3 (3), G1-G5 (5) = 57 rows.
- Products covered: Kode Dot, Cardputer/ADV, T-Deck, Flipper Zero, Rabbit R1, Humane, Plaud, Bee, Limitless, Friend = 10.
- Kode Dot plus Cardputer = 21 rows, but Kode Dot is secondary-source only (see warning at the top).
- Not found: direct Kickstarter/Reddit comments for Kode Dot; any complaint about Cardputer speaker, screen or case durability; Trustpilot or Amazon review text for any product (the fetcher returned summaries, not review lists).

---

## Top 10 fixes, ranked by impact on backer trust and usefulness

1. **Honest, regular, dated update rhythm** (K1, G1, G2, FR1, FR2). Fixed schedule, a milestone board with "done / at risk / late", never say "on track" before the gate passes, announce slips the day you know with a buffered date. FREE. Highest impact because it is the most repeated backer complaint and the only one Piblo fully controls.
2. **"Works without us" pledge** (H1, L1, L2, R5, G5). Device and Core keep working if the company stops; Core is open source and local; no account needed; user can export and delete data. Write it on the campaign page and in the terms. FREE (partly built already by design).
3. **Written "no subscription, no upsell" promise plus a plain "what you need" box** (H3, P6, K4). Total cost in pounds including a Cardputer ADV, a Windows PC and Wi-Fi, and what free models cost (nothing) versus any optional paid model. FREE.
4. **Reliable core loop: nothing lost** (P1, P2, P3). Voice notes saved to microSD first with retries and a visible "saved to PC" tick; a clear start/stop tone for hold-to-talk; yes/no/later always confirmed on screen. FREE.
5. **Measure and publish real battery life, and fix charging behaviour** (C3, C4, C5, R2). Hours for each mode, battery saver, charge screen that does not start the radio, one-line charging instruction. FREE (testing time).
6. **Fast, visible feedback and published latency** (R3, FR1). "Listening / thinking / done" states and a measured round-trip time on a typical home network. FREE.
7. **Privacy by design, said loudly** (B1, FR3, L2). Push-to-talk only, on-screen record light and tone, data stays on your PC unless you choose a cloud model, one-page "what Piblo can see". FREE.
8. **Safe firmware: signed OTA, staged rollout, one-key rollback, versions pinned, docs shipped with every release** (P3, F1, C12, T1, K3). FREE (engineering).
9. **Painless first run on ADV: web flasher that rejects the wrong build, one-click Windows Core installer, 10-minute target, "ADV only" labels** (C1, C8, K6). Web flasher and installer FREE; pre-flashed units cost MONEY.
10. **Support, safety and returns policy: stated reply times, UK contact, replacement promise, charger safety guidance, first-charge bench test** (C2, C6, H2, H4, P4). Policy and guidance FREE; testing units, spares and support time cost MONEY.

Cheap extras worth doing: freeze spec and show only real-unit photos (K2); publish exact backer and funding figures with source links (K5); few reward tiers and no hardware-changing stretch goals (G3); lithium-battery shipping plan (F2).

## Things I did not verify

- UK-specific issues (VAT, customs, UKCA marking for a battery device): not researched or sourced. Treat any UK compliance claim in the campaign as needing a check.
- Real Kode Dot backer comments, and Trustpilot and Amazon review text, because those pages were not reachable with my tools.
