# Agent Device Control (Cardputer)

Everything goes through Core (`http://host:8787`), so an agent only needs `MAZ_TOKEN`.
Token travels in the `X-MAZ-Token` header.

- `scripts/piblo_remote.py status` — app, volume/brightness %, battery, Wi-Fi.
- `scripts/piblo_remote.py screen out.png` — PNG of the 240x135 LCD.
- `scripts/piblo_remote.py keys "down right*7 esc"` — press keys; `*N` repeats.
- `scripts/piblo_remote.py open settings` — open an app/surface by id.
- `scripts/piblo_remote.py volume 100` / `brightness 50` — set percent, applied + saved.

Key names: `up down left right enter esc space tab backspace del`, and single chars
`a-z 0-9 . , / ; ' - = \` \ ``. The Cardputer arrows are Fn-combos on the ADV legend:
`;` = up, `.` = down, `,` = left, `/` = right — plain `; . , /` work too.

Example "set volume to 100 via the menus": `open settings`, `keys "down*2 enter"`,
`keys "up*9"`, `screen out.png` (verify), or just `volume 100`.