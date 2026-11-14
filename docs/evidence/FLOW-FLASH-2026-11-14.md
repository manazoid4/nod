# Piblo Flow: flash record, 14 Nov 2026

- Flashed over USB (COM3): app image to `ota_0` (0x10000) + `boot_app0` (otadata reset). Partition table read from the device first and matched `partitions.csv` exactly (ota_0/ota_1 0x300000, no Launcher). `ota_1` (df1b939) untouched.
- Device after flash (Core `/core/device`): `fw_running_slot=ota_0`, `fw_build=e71e1ee` (sha of HEAD at build time; image includes the review fixes), Wi-Fi up, host_worker IDLE, charging 76%.
- Live View: Type on PC opens via hotkey Y and shows "Hold SPACE / speak, release: it types on your PC" with the PC link up (`flow-type-on-pc-live-2026-11-14.png`).
- NOT yet verified: physical SPACE hold -> text appearing in a normal Windows window. The key API only sends taps, so a hold cannot be simulated.

## Rollback (kept on Desktop\MazWorks\PIBLO-RC-FIRMWARE)
- Fast: write the saved `rollback-otadata-boot-ota1.bin` back to 0xe000 -> boots ota_1 (df1b939):
  `python esptool.py --chip esp32s3 -p COM3 --no-stub write_flash 0xe000 rollback-otadata-boot-ota1.bin`
- Full: `rollback-df1b939-v1.5.1.bin` (sha256 b334eeac...f4c5) to 0x10000.
