# Piblo keys — final map for both modes

Cardputer ADV has no dedicated arrow keys: arrows are Fn+`;` (up), Fn+`,`
(left), Fn+`.` (down), Fn+`/` (right). Menus also accept the plain keys
`;` `,` `.` `/` (the shell fallback), so **essential navigation needs no
Fn at all**. The approval overlay always sits above everything: only
**Y / ENTER approve** (held 800 ms for Nod items), **N / ESC reject**; a
timeout or lost connection is a rejection. No Easy Mode key, remap,
auto-repeat, phone text or "any key" path can approve — enforced by
`firmware/nod/include/easy_keys.h` + native tests.

## Easy Mode (Home = plain list; default on)

| Key | Action |
|---|---|
| UP / DOWN, or `;` / `.` | choose |
| ENTER | open the selected row: Notes, Reminders, Messages (results inbox), Tasks, Shortcuts (snippets), Settings, Help |
| ESC | back (nothing at Home itself); inside a text field ESC abandons the edit |
| 1–4 | run a quick action (advanced, still works) |
| SPACE (hold) | brain dump (advanced, still works) |

Rows are plain words only (no "MCP", no "Core"). Only working screens are
listed. Toggle in **Settings → Easy Mode** (persisted; classic home is
unchanged when off).

## In any text field (both modes)

| Key | Action |
|---|---|
| printable | insert at the cursor (Shift gives capitals/symbols) |
| LEFT / RIGHT (Fn+`,` / Fn+`/`) | move the cursor |
| BACKSPACE | delete before the cursor |
| DELETE (Fn+DEL) | delete at the cursor |
| double Shift (two presses, nothing between) | CAPS on/off (shown as CAPS) |
| Ctrl+SPACE (hold) | phone-side dictation is invisible here: talk; the transcript lands in the field |
| Ctrl+P | insert the next saved shortcut (Snippets) |
| Ctrl+H | insert the next recent submitted phrase |
| | the field shows KEYS / CAPS / PHONE and brief messages ("phone text in", "too long") |

Caps letters are the keyboard decoder's normal Shift behaviour; the double
Shift toggle never fires while typing normally. The TCA8418 reports
transitions only (held key = one down + one up, no auto-repeat), plus a
30 ms bounce guard, so keys never duplicate.

## Phone keyboard mode

Type in a phone keyboard (or use phone dictation), send to any open field.
Phone text lands literally at the cursor; `insert`/`replace`/`send` differ
only in whether the buffer is kept — `send` never presses ENTER for you.
No field open = hint + "no field" answer. See
`docs/protocol/PHONE-KEYBOARD.md`.

## Unchanged (both modes)

Ctrl+K palette, Ctrl+L back to launcher, Fn+SPACE context ask, Fn+F field
mode, Fn+Q quiet/silent/normal, Fn+H pause asks, ENTER backspace semantics
outside fields, hold ESC to go home, alert keys (A/ENTER ack, S snooze,
ESC hide), notes/reminders/tasks/snippet behaviour, voice (hold SPACE,
Ctrl+SPACE in fields). Existing simulator key mapping (MCP lane) is
unchanged; the simulator follows this map after merge.
