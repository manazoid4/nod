# Piblo Companion (Android) — handover

`android/` only. Compose app `uk.mazworks.piblo`, minSdk 26 / targetSdk 36.

## Done

- Single-activity Compose app: Home (simulator + Approve/Reject/Snooze/Ack), Messages, My Tools
  (notes, reminders, timers, **Type on Piblo**), Connections (simulator / computer / BLE stub),
  Settings (privacy, notification forwarding, background watch, Find my phone).
- Built-in simulator (`Hub` + `PibloScreen`): a 240×135 Piblo that works fully offline with local
  demo events.
- Room (notes, reminders, messages) + DataStore prefs + Keystore-encrypted Core token (`SecretBox`).
- Core client (`CoreClient` + `Proto`): summary/events/decide/alert/ack over piblo-proto v1 with
  `X-Piblo-Client: android/<ver>`, fail-closed, bounded queue, back-off reconnect (`CoreLink`).
- Opt-in notification forwarding (`NotificationListenerService`) to `POST /buddy/alert`.
- Find my phone (ring until stopped) on the `find_phone` kind / interim `source: find_phone`.
- **Phone keyboard sender**: `POST /buddy/text` (insert / replace / send), polls `GET /buddy/text/{id}`
  until the device acks `inserted` / `no_field` / `too_long`. Text is always literal characters.
- CI `.github/workflows/android.yml` (build + unit tests + debug APK artifact, path-filtered to `android/**`).

## How tested (exact commands)

- `cd android && JAVA_HOME=… ANDROID_HOME=… ./gradlew assembleDebug testDebugUnitTest` → **BUILD SUCCESSFUL, 16 tests, 0 failures** (`ProtoTest`: protocol parsing from real Core fixture JSON, truncation by code point, alert/decide/text JSON builders, address normalisation).

## Simulated / untested

- No emulator or physical phone was used. UI behaviour is compile-verified only; the simulator +
  reminders/forwarding/FindPhone paths are **not** run on a device.
- The computer link was exercised against the same Core routes in `host/tests/test_mcp_e2e.py`
  (that test drives a headless simulator, not this app).
- BLE transport is an explicit stub — the firmware has no BLE GATT service yet.

## Next actions

- Install the debug APK (`app/build/outputs/apk/debug/app-debug.apk`) and pair with a running Core.
- When firmware BLE ships, implement the `Transport` seam with the same v1 JSON over BLE framing.

## Proposed BLE framing (for the future Transport)

Carry piblo-proto v1 JSON messages over a GATT characteristic: length-prefixed UTF-8
(2-byte big-endian length + JSON body), one message per write/notification. Device → phone events and
phone → device decides/alerts/text reuse the exact same JSON as the HTTP routes.
