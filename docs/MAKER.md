# Piblo Maker: first slice

Implemented and tested with simulated printers: plain-word status and temperatures,
EnderForge's next guided step, printer finish/failure/offline alerts, individually
approved Pause/Cancel, and three parametric accessories. No real printer or accessory
has been physically validated by this work. No firmware or device screen changes.

## Configure on the paired computer

- `MAZ_MAKER_ENDERFORGE_CMD`: trusted local command, e.g. `ef`, or `python "<path-to-ef.py>"`.
  Empty (the default) turns all Maker routes off. Only `status --json` and `next --json`
  are invoked, with a timeout and no shell. EnderForge remains an external, separately
  installed tool; none of its implementation is included here.
- `MAZ_MAKER_OCTOPRINT_URL`: your OctoPrint HTTP(S) base URL. Optional status fallback;
  required for Pause/Cancel. Local network addresses work. Redirects are not followed.
- `MAZ_MAKER_OCTOPRINT_KEY_FILE`: path to a local file containing the OctoPrint key.
  The key is read on the computer and never returned. Keep it out of the repository.
- `MAZ_DATA_DIR`: generated files go under `maker/accessories/` in Core's data directory.

All routes use Core's existing bearer token. EnderForge exit 3 means “Can't reach the
printer”; other CLI errors are shown without leaking stderr. OctoPrint status reads
only `/api/printer` and `/api/job`. EnderForge currently supplies no remaining-time
estimate; OctoPrint supplies one when used as the status source. There is no
`private_mode` module in this checkout; the HTTP client uses the configured endpoint,
no proxy environment, no redirects, and bounded timeouts.

## Use the routes

In a shell with `CORE_URL` set to your Core base URL and `PIBLO_TOKEN` set locally:

```sh
curl -H "Authorization: Bearer $PIBLO_TOKEN" "$CORE_URL/maker/printer"
curl -H "Authorization: Bearer $PIBLO_TOKEN" "$CORE_URL/maker/next"
curl -X POST -H "Authorization: Bearer $PIBLO_TOKEN" "$CORE_URL/maker/pause"
curl -X POST -H "Authorization: Bearer $PIBLO_TOKEN" "$CORE_URL/maker/cancel"
curl -X POST -H "Authorization: Bearer $PIBLO_TOKEN" "$CORE_URL/maker/poll"
curl -H "Authorization: Bearer $PIBLO_TOKEN" "$CORE_URL/maker/accessories"
curl -H "Authorization: Bearer $PIBLO_TOKEN" -H 'Content-Type: application/json' \
  -d '{"text":"make me a stand at 60 degrees"}' "$CORE_URL/maker/accessories/make"
```

Pause/Cancel return `{"status":"pending","id":"..."}` and create an Ask on Piblo
request in category `other`. Approve or deny on Piblo. Call `/maker/poll` to consume
the decision, or repeat the same action with JSON `{"request_id":"..."}`. Only an
unexpired `allow` permits the exact corresponding OctoPrint job action. The print
identity and progress are rechecked before sending. A changed print yields `stale`;
a deny/expired request yields `denied`. Each request is consumed once. An uncertain
network response yields `uncertain`, never an automatic retry. Inspect the printer
before making a fresh request. Approvals do not survive a Core restart.

Call `/maker/poll` periodically from the paired client while monitoring a print;
this slice does not install a background poller. It detects transitions after first
observing a print, posts through Buddy's existing alerts, and suppresses repeated
finish/failure/offline alerts for that print. Idle alone is not proof of success:
completion requires an explicit finished state or 100% progress. A cancelled print
with partial progress is not announced as successful. Events between polls can be
missed. As with any status-based check, a printer-side job change immediately after
the final observation cannot be made atomic by this client.

## Accessories

`hardware/accessories/stand.scad`, `mount.scad`, and `loop.scad` share the case's
unchanged dimensions in `hardware/case/case_dimensions.scad`. Existing case geometry
uses the same dimension file. Generated SCAD embeds those dimensions and all chosen
parameters, so the returned file can be opened independently.

- “make me a stand at 60 degrees”: `stand`, angle clamped to 30–80° (default 60°).
- “wall mount with screws” / “fridge mount with magnets”: `mount`, screw or magnet
  attachment. The magnet variant has four nominal 10 × 3 mm glue-in pockets; magnets
  and screws are separate hardware and must be selected and tested for the load.
- “lanyard loop” / “keyring loop”: `loop`, a case-edge clip with a 5 mm eye.

Parsing is rule-based; unknown or mixed accessory requests are rejected. No LLM,
new dependency, paid service, or automatic printer upload is involved. If `openscad`
is on PATH, Core runs it on the paired computer with a 90-second limit and returns
the STL path after a successful nonempty output. Otherwise (or on render failure),
it returns the filled-in SCAD and “Open this in OpenSCAD to export”. Paths refer to
the paired computer. These routes do not serve or download files.

Physical checks still required: real EnderForge/OctoPrint on the Ender 5; approval,
deny, timeout, pause and cancel on a supervised test print; finish/failure/offline
alerts and delivery/speech on Piblo. Print each accessory and check case fit, screen
angle, stand stability, port/vent access, layer strength, wall/fridge retention and
clip grip. The loop's upper jaw needs supports. Never rely on the untested loop to
secure Piblo or on untested magnets to hold it. The original case's estimated port
positions and fit limitations in `hardware/case/DIMENSIONS.md` still apply.

## Standard and Pro

Both get printer status, nudges, guided steps and the accessory library, with
rendering on the paired computer. Pro later adds camera print-watching and running
the slicer/renderer on its local AI box. Those later features are not implemented.
Starting a print, heating, motion, homing, tuning and firmware operations remain on
the computer in EnderForge, with its own confirmation prompts.
