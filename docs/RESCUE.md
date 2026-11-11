# Piblo Rescue

Core stores a small Rescue card locally in `data_dir/rescue.json`. No cloud,
subscription, external lookup or new dependency is involved. Use the existing
Core bearer authentication for all three routes:

| Route | Result |
| --- | --- |
| `GET /rescue` | Saved JSON, or an empty card before the first save. |
| `PUT /rescue` | Validate and replace the complete card; return the saved JSON. |
| `GET /rescue/compact` | UTF-8 `text/plain` for a device cache. |

Example JSON (all fields are optional; omitted fields become empty):

```json
{
  "contacts": [{"name": "Alex", "phone": "+00 000 000"}],
  "travel": "Return train: platform 4",
  "notes": "Spare key with Alex",
  "emergency_instructions": "Contact Alex if help is needed"
}
```

Up to eight contacts are accepted. Names have at most 64 characters; phone
numbers have at most 40 and accept digits, spaces and common dialling punctuation
(`+ ( ) . # * - x X`). Travel and emergency instructions allow 4096 characters
each; notes allow 8192. The complete, compactly serialized JSON must also fit
16 KiB in UTF-8. Invalid fields, unknown fields and oversized updates return 422
without changing the previous card. Writes replace the saved file atomically.
Unreadable or invalid stored data returns 503; it is never silently replaced by
an empty card.

The compact copy is at most **2048 UTF-8 bytes**, with lines of at most 96 bytes.
Contacts appear first, followed by emergency instructions, travel and notes.
Contact names are shortened to 40 UTF-8 bytes; phone numbers remain complete.
Whitespace is flattened, long text wraps, and trailing lines are omitted when
the buffer is full. JSON retains the full saved text. Compact text never cuts a
UTF-8 character. An empty card produces empty text.

Rescue contains personal information: the file stays in the configured local
data directory and is not encrypted by this feature. Authentication and Core's
existing network policy still apply; this feature does not publish the card.

## Firmware follow-up

This slice supplies Core storage and the download endpoint only. Firmware must
later download the compact copy while paired, store the last successful copy
persistently, and show it without a phone, network or Core connection. Retain the
previous device copy if a refresh fails, and provide a way to clear it. Confirm
the byte budget, screen navigation, Unicode glyph support and offline behavior
on real hardware before calling Rescue available on the device. No firmware or
protocol contract changes are included here.
