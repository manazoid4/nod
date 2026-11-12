# Piblo implementation priorities

Acceptance tests below are targets; none imply the behavior is already verified on the physical device.

## P0 — prove the three buyer moments

| Existing path | Buyer outcome | Minimal change | Acceptance test | 10-second video idea |
|---|---|---|---|---|
| `src/apps/voice_apps.cpp`; `host/mazhost/braindump.py`; `host/tests/test_braindump.py` | Capture a thought before it is lost and find it later. | Close the capture-to-inbox gaps; preserve retry and avoid duplicate notes. | Physical capture reaches the inbox twice; restart and confirm both notes remain; disconnect/reconnect shows clear failure and retry without loss or duplicates. | Speak one thought, open the inbox, restart, show it still there. |
| `src/core/approvals.cpp`; `host/mazhost/authority.py`; `docs/ASK-ON-PIBLO.md` | Safely approve one useful computer action from the device. | Bind signed decisions to the request; reject injected keys on approval screens; render the whole request. | Safe allow-listed action runs after a physical approval only; deny, expiry, disconnect, altered request and injected key never run it. | Show a named safe action, press the device key, show the actual result. |
| `src/apps/focus_time.cpp`; `host/mazhost/focus.py`; `host/tests/test_focus.py` | Know how much focus time remains with one glance. | Make remaining time and completion clear on the existing timer screen. | On-device remaining time is legible without navigation, updates through a full session and shows completion; record behavior without network if supported. | Start the timer, glance at the countdown, show completion. |

## P1 — improve comfort and maker proof

| Existing path | Buyer outcome | Minimal change | Acceptance test | 10-second video idea |
|---|---|---|---|---|
| `src/input/keyboard.cpp`; `src/input/keyboard.h` | Type and trigger shortcuts comfortably. | Compare two key-spacing or overlay prototypes; keep the better layout. | Run the same short tasks on both; record comfort, errors and completion time from real users. | Side-by-side layouts; same task typed on each. |
| `hardware/case/README.md`; `hardware/case/DIMENSIONS.md` | Hold or place the device securely. | Make one printable stand or grip that fits the current prototype. | Print, fit and remove repeatedly; no interference with keys, ports or charging. | Print comes off the bed, clips on, device stands securely. |
| `src/ui/buddy_face.cpp`; `src/core/alerts.cpp` | Understand success, waiting and failure without confusion. | Make three existing status states visually distinct; preserve silent/reduced-motion behavior. | Show each real state on-device; users identify all three; verify silent mode. | Trigger success, waiting and failure; show the three distinct cues. |
| `docs/launch/DEMO-SHOTLIST.md`; `docs/launch/KICKSTARTER-READY.md` | Judge the actual prototype and its limits before backing. | Record real flows and replace unsupported campaign claims with proven ones. | Each advertised function has real footage or an explicit disclosure; no concept render is presented as built hardware. | Three quick real-device moments, with dependencies in frame. |
