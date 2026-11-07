# Nod status

🟢 done with evidence · 🔵 building now · 🟠 needs Maz · ⚪ later
Every feature: [FEATURE_INVENTORY.md](FEATURE_INVENTORY.md) · Device tests: [test ledger](docs/evidence/TEST-LEDGER-2026-10-11.md)

## Level 1: Recover Nod
- [x] 🟢 Import MAZ Pocket firmware + Core: [PR #14](https://github.com/manazoid4/nod/pull/14)
- [x] 🟢 Find the real device build: v1.0.2 (`nod-v1.0.2-b25`), not v0.8.0 ([ledger #1](docs/evidence/TEST-LEDGER-2026-10-11.md))
- [x] 🟢 Save unpushed GTX PC work to GitHub: `maz-pocket` branches `recovery/mazpc-*`
- [x] 🟢 Feature inventory, nothing retired: [FEATURE_INVENTORY.md](FEATURE_INVENTORY.md)
- [ ] 🔵 Bring v1.0.2 into Nod, CI green: [PR #16](https://github.com/manazoid4/nod/pull/16)
- [ ] ⚪ Rename MAZ Pocket → Nod in screens and Core (keep API compatible)

## Level 2: Bring Nod to life
- [x] 🟢 Device boots v1.0.2 and talks to Core over Wi-Fi ([ledger #1–2](docs/evidence/TEST-LEDGER-2026-10-11.md))
- [x] 🟢 Brain dump reaches the inbox ([ledger #5](docs/evidence/TEST-LEDGER-2026-10-11.md))
- [ ] 🟡 Voice: right answer, but 4.4 s and robotic ([ledger #4](docs/evidence/TEST-LEDGER-2026-10-11.md)) → fix: local Kokoro, streamed ([research](docs/evidence/VOICE-RESEARCH-2026-11.md))
- [ ] ⚪ Saved notes survive a restart
- [ ] ⚪ One useful PC action end to end, with approval
- [ ] ⚪ New Home: big colourful talk circle (on device)

## Level 3: Make it beautiful
- [ ] 🔵 Nod Core: real Windows app (Electron, tray, onboarding)
- [ ] 🔵 Website: two design concepts
- [ ] 🟠 Maz picks concept A or B
- [ ] ⚪ One design language across site, app and device

## Level 4: Show the world
- [ ] ⚪ Real device clips (film plan in PR #15)
- [ ] ⚪ Teaser + demo video
- [ ] ⚪ Exploded hardware + case visuals

## Level 5: Kickstarter ready
- [ ] ⚪ Open-source release with downloads anyone can follow
- [ ] ⚪ Community: feature voting, case gallery
- [ ] ⚪ Campaign page, costs, rewards

Firmware ticks only go green when the feature works on the real Cardputer, not just in the build.
