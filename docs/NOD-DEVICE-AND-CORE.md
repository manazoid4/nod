# Piblo: device firmware + Piblo Core (imported from MAZ Pocket)

Imported 6 Nov 2026 from `manazoid4/maz-pocket` @ `f59d3a4` (v0.8.0, MIT, same owner).
Layout is deliberately the same as the source repo so the release scripts and CI keep working.

| Path | What |
|---|---|
| `src/`, `platformio.ini`, `partitions.csv` | Cardputer ADV firmware (M5Launcher app-only image) |
| `host/` (`mazhost`) | **Piblo Core** - Windows/PC host: voice, models, pairing, executor, portal |
| `scripts/`, `.github/workflows/` | version check, release packaging, CI |
| `web-flasher/` | browser flasher + its tests |
| `firmware/nod/` | device-independent headers: charging mode, display profiles, Home layout |
| `docs/pocket/` | all MAZ Pocket docs, release rules, audits |
| `site/`, `firmware/draft/` | Kickstarter site, Claude Buddy draft (unchanged) |

## Added on top of v0.8.0
- **Charging mode** (`src/apps/charging.cpp`, `firmware/nod/include/charge_monitor.h`): `M5.Power.isCharging()` is unreliable on the Cardputer, so charging is inferred from the battery-voltage trend; a positive M5 reading still wins. Plugging in at Home opens a calm screen (big %, status, time-to-full from observed rise only, dims, any key wakes, blanks when full). ESC leaves.
- **Two screen sizes** (`firmware/nod/include/display_profiles.h`): `standard` 240x135 (built-in) and `large` ~3.5in 480x320 (template until a sample arrives). Layout code scales to either.

## Verified here (6 Nov 2026)
| Check | Result |
|---|---|
| Piblo Core tests (`pytest host/tests`) | 65 pass, 1 fail: needs PowerShell `pwsh`; same failure in the original repo on Linux. Expect pass on Windows. |
| Web flasher tests | pass |
| `scripts/check-version.py` | pass |
| Firmware compile, Cardputer ADV (PlatformIO) | **pass**, 1,460,865 B of the 1,572,864 B (0x180000) limit, using the repo's own `platformio.ini`. M5GFX pin moved `0.2.26` -> `0.2.27` because 0.2.26 is no longer in the PlatformIO registry (CI broke on it). Not yet confirmed on hardware. |
| `firmware/nod` unit tests | 313 checks pass |

## NOT verified
- **Nothing has run on a physical Cardputer.** No flash, no charging test, no display check.
- Large-screen driver, wiring and offsets are unknown until a sample is bought.
- Still named MAZ Pocket inside the firmware and Core (strings, `mazpocket.local`, API names, release file names). Renaming to Piblo is a separate, careful pass.
- The new SUBTITLES / ROUTINES / SAVE THIS Home is a layout only; the firmware Home is still the six-surface MAZ Pocket Home.

## First physical test
Flash the build, plug in USB-C at Home. Expect the Charging screen within ~90 s. Unplug: expect it to stop saying Charging within ~90 s.
