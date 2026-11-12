# Device pairing: "Connect to computer" (no typed token)

Status: contract v1, shared by Core (`host/mazhost`), firmware (`src/`) and the Windows app (`app/`).
Change it only through the orchestrator, because all three build against it.

## What the person does
1. On Piblo: More -> Connect to computer (or the first-run screen). Piblo shows
   **"Code 482 913, click Allow on your computer"**.
2. On the PC: the Piblo app (or tray notification) shows **"Piblo wants to connect. Check Piblo shows
   482 913."** with **[Allow] [Not mine]**.
3. They click Allow. Piblo shows "Connected" within 2 s. Nothing is typed anywhere.

Nothing connects without a human clicking Allow on a PC that already holds Core's token.

## 1. Discovery (UDP, LAN only)
- Piblo sends the ASCII datagram `PIBLO-DISCOVER 1\n` to `255.255.255.255:8788` (and its subnet broadcast).
  It retries 3 times, 400 ms apart.
- Core listens on UDP `0.0.0.0:8788` (setting `MAZ_DISCOVERY_PORT`, default 8788, 0 = off) and replies
  **unicast to the sender** with one JSON line:
  `{"piblo":1,"port":8787,"name":"<hostname, max 32 chars>","version":"<core version>"}`
- Core ignores non-LAN sources (same `is_lan_ip` rule Core already uses) and anything that isn't exactly
  the discover line. Replies carry no secret.
- Piblo takes the **source IP of the reply** as the host address. When several Cores reply, it uses the
  first and shows its `name` on the code screen ("Code 482 913 for MAZPC").

## 2. Device asks (public, rate-limited)
`POST /pair/device/request`, body `{"device_id": "<[A-Za-z0-9_-]{4,32}>", "name": "<max 24 printable ASCII>"}`
- 200: `{"request_id": "<opaque, 22+ chars>", "code": "482913", "expires_in_seconds": 120}`
- The code is 6 digits from `secrets`. The `request_id` is `secrets.token_urlsafe(16)`.
- A new request from the same `device_id` replaces that device's older pending request.
- At most 4 pending requests at once, then 429 `too_many_requests`. Each IP gets at most 6 requests a
  minute, then 429. Bad body: 400.

## 3. Device waits (public, bound to the requesting IP)
`GET /pair/device/request/{request_id}`
- `{"status": "pending"}` while waiting
- `{"status": "denied"}` / `{"status": "expired"}` (terminal)
- `{"status": "approved", "token": "<Core token>", "port": 8787}` is returned **exactly once**, then the
  record is deleted and later reads give 404.
- 404 for an unknown or deleted id, **or when the caller's IP differs from the IP that made the request**
  (the same answer, so it gives nothing away).
- Piblo polls every 2 s and stops at 120 s or on any terminal status or 404.

## 4. The PC decides (bearer, `Authorization: Bearer <MAZ_TOKEN>`)
- `GET /pair/device/pending` returns
  `{"requests": [{"request_id", "code", "name", "device_id", "ip", "age_s"}]}` (pending only, oldest first).
- `POST /pair/device/{request_id}/approve` and `POST /pair/device/{request_id}/deny` return `{"ok": true}`.
  404 if it's unknown, expired or already decided.
- Never auto-approve. Approval is the only way the token leaves Core.

## 5. Piblo saves
On `approved`, it sets `Cfg.hostAddr = <reply source IP>`, `Cfg.hostPort = port`, `Cfg.hostToken = token`,
`Cfg.firstRunComplete = true`, then `Cfg.save()` (the same fields `MAZCOREPAIR` writes), and shows "Connected".

## Security notes
- The token travels once, over the home LAN, by plain HTTP. That's the same trust level as the existing
  device<->Core link. Remote Cores stay HTTPS-only.
- The person compares the 6-digit code shown on both screens. A rogue LAN device would show up as an extra
  request with a code that doesn't match what's on Piblo.
- v1 hands out Core's single shared token. Per-device tokens (revoke one Piblo) are a later step.
- Pairing never touches approvals: a pending pairing can't approve or deny any agent request.

## Live View (already exists, unchanged)
- `GET /core/cardputer/screen.png`, `POST /core/cardputer/key {"keys": "..."}`, `POST /core/cardputer/action {"action": "..."}`.
- The firmware frame is declared `RGB565LE`. Firmware before this change sent big-endian bytes (red and blue
  looked swapped). This change makes the firmware send little-endian, as declared.
