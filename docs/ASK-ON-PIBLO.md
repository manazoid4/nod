# Ask on Piblo

Ask Core before carrying out a consequential action. Treat every HTTP answer except `allow` (or MCP answer except `approved`) as a refusal; check the returned digest against the request you submitted. The host requires an HMAC proof for `allow`, bound to the request id, canonical digest, decision and fresh nonce. Bearer authentication alone does not satisfy that check. Deny, cancel and edit never approve an action. Requests in the `purchase` and `delete` categories are denied by default; the owner can enable each with `MAZ_ASK_UNLOCK_PURCHASE=1` or `MAZ_ASK_UNLOCK_DELETE=1` in Core's environment. Keep these owner settings and device keys out of agents' control.

## Firmware follow-up

**The host-side proof check is enforced now; the guarantee that only a physical press approves an action is not yet achieved.** Today's firmware sends unsigned decisions and accepts computer-injected key events. It therefore cannot approve with the default settings. Firmware must securely store its per-device key, sign decisions with that key, and refuse key events that arrived over the network on approval screens. It must also render the complete card; the current screen clips text and does not display every field. Do not rely on the computer being unable to approve until these changes, the pairing trust model and the complete display have been reviewed and tested together.

The optional `MAZ_ASK_LEGACY_DEVICE_DECIDE=1` restores unsigned allows for compatibility and defeats the proof check. It is off by default. Anyone who can change Core's environment or read its local key file can defeat host-side proof. Pairing is currently approved using the shared bearer token and sends credentials over LAN HTTP, so a bearer holder able to authorize a new pairing or observe that traffic can acquire a device key. This also requires a stronger pairing design before claiming a physical-only guarantee.

Future firmware may request `approval_proof: true` when pairing. After the owner approves, the one-time pairing response includes `device_id` and `approval_key`; Core stores its copy in its local data directory. The verifier expects `X-Piblo-Device-Id` and a lowercase hex HMAC-SHA256 using the UTF-8 key string over `id:digest:decision:nonce`. The digest is SHA-256 of compact, UTF-8, sorted-key JSON containing `agent`, `tool`, `summary`, `amount`, `recipient`, `category` (missing fields are empty strings). Never send the device key with a decision. Re-pairing rotates that device's key.

## HTTP example

Use the Core address and token configured on your computer:

```sh
curl -X POST "$PIBLO_CORE/buddy/request" -H "Authorization: Bearer $PIBLO_TOKEN" -H 'Content-Type: application/json' -d '{"agent":"Assistant","tool":"Send email","summary":"Send the draft","recipient":"Team","category":"email"}'
```

Poll `GET /buddy/state?id=...` for the result. `GET /buddy/summary` and `/buddy/pending` provide the nonce and digest for the device. `POST /buddy/decide` accepts `allow`, `deny`, `cancel`, `edit` (with `instruction`), or `undo`. An edit is terminal and needs a new request and proof. Declare `undo` as a short description to offer a 30-second recording window after allow; undo records `undone`, it does not reverse an action. `POST /ask/pause` with `{"on":true}` denies current and future requests until resumed or the halt expires; it cannot stop already running actions. Non-urgent requests are held during Focus, while urgent requests pass. A client with a shorter wait can still cancel a held request; it must not treat that as approval.

## MCP example

Call the existing `piblo_request_approval` MCP tool with:

```json
{"action":"Send email","summary":"Send the draft","sensitive":true}
```

The MCP tool waits up to 55 seconds and fails closed if no approval arrives. The tool accepts `category`, `amount`, `recipient`, `undo` and `urgent`, and returns the digest and any edit instruction. It returns once a decision arrives; use the HTTP state endpoint to check for a later Undo.
