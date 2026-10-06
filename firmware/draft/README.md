# Firmware draft (not compiled)

Draft Bluetooth Buddy module written inside the MAZ Pocket firmware. It still
includes MAZ Pocket headers (`apps.h`, `common.h`, `../core/*`, `../audio/*`),
so it will not build on its own. Kept here as the starting point for the
standalone nod firmware and the upstream Cardputer port.

- `buddy/ble_link.*` - encrypted BLE link, adapted from Anthropic's reference (see NOTICE)
- `buddy/buddy.*` - protocol state: sessions, pending prompt, approve/deny
- `apps/claude_buddy.cpp` - screen with Y/N approvals
