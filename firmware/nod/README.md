# nod firmware core (device-independent)

Dependency-free C++11 headers the Cardputer firmware includes. Tested on a
normal computer, so logic is proven before it ever touches hardware.

| Header | What it does |
|---|---|
| `charge_monitor.h` | **Charging mode.** Works out Charging / Full / On battery from battery-voltage trend (the Cardputer under M5Launcher doesn't report charging reliably). Optional VBUS hint overrides. Dims the screen while charging, wakes on any key, blanks when full. ETA comes from the observed rise only, never an assumed battery size. |
| `battery_curve.h` | LiPo voltage to percent. Capped at 99% while charging until Full is proven. |
| `display_profiles.h` | **Swappable screens.** One entry per panel (size, offsets, invert). UI adapts; bad saved id falls back to the stock panel. |
| `home_layout.h` | **Simpler Home:** SUBTITLES, ROUTINES, SAVE THIS, MORE as 4 big cards, arrow keys / 1-4. |

```
make test      # 343 checks
make preview   # regenerates preview/layouts.js from the headers
```
Open `preview/index.html` to see Home + charging screens for every profile.

## Status (honest)
- Logic: **host-tested PASS.** UI preview: **mockup only**.
- Hardware: **NOT TESTED on a real Cardputer.** Every display profile is `verified=false`; the stock offsets come from M5GFX and need a physical check. The other panels are templates.
- Not yet wired into the MAZ Pocket firmware, and no host-side SUBTITLES / ROUTINES / SAVE THIS yet.

## Firmware hooks needed (on-device)
1. Every ~10 s call `monitor.feed(millis(), batteryMv, vbus)`; pass `-1` if VBUS can't be read.
2. Each frame apply `chargeScreenPolicy(...)` (backlight, redraw rate).
3. Load the saved profile id via `profileOrDefault()`; lay out with `computeHome(p.w, p.h)`.
Physical test: plug in, watch for Charging within ~90 s; unplug, expect On battery within ~90 s.
