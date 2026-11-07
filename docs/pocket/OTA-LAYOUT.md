# OTA and the real flash layout

`partitions.csv` is NOT what runs on the device. M5Launcher owns the partition table; nod only sees it.
Layout read from Launcher's Web UI (8 MB flash):

| Name | Type | Offset | Size |
|---|---|---|---|
| app0 | app / test (Launcher itself) | 0x10000 | 0x150000 |
| coredump | data | 0x160000 | 0x10000 |
| mazdata | data / littlefs | 0x170000 | 0x200000 |
| nodfw0 | app / ota_0 | 0x370000 | 0x170000 (1,507,328 B) |
| nodfw1 | app / ota_1 | 0x4e0000 | 0x170000 |

nvs (0x9000) and otadata (0xe000) are required by Launcher's own table builder (`kRequiredBootPartitions`) so they exist, the Web UI just hides system partitions.

How Launcher boots an app: it writes the image into the slot, verifies it, then calls the standard `esp_ota_set_boot_partition()` (otadata). So nod's standard `esp_ota_*` self-update is the same mechanism. Update image must stay under 1,507,328 bytes.

Self-update (`fwUpdate`): the 30% battery precheck was removed in PR #20 (commit 57c6161, open at time of writing, not yet on main); it erases the spare slot, downloads `/fw/latest.bin`, SHA-256 + `esp_ota_end` verify, `esp_ota_set_boot_partition`, 3-boot rollback guard (`fwBootGuard`).

## Layout seen 7 Nov 2026 (Launcher partition manager)

Read from Launcher's Partition Manager on the device, 7 Nov 2026. This is newer than the table above and differs from it; treat this section as the latest observation.

| Name | Type | Offset | Size |
|---|---|---|---|
| app0 | app / test (Launcher, protected) | 0x10000 | 1,376,256 B |
| coredump | data | 0x160000 | 64 KB |
| spiffs | data | 0x170000 | 448 KB |
| nodfw1 | app / ota_0 (Nod) | 0x1e0000 | 1,507,328 B |

- Only ONE Nod OTA slot exists, so Nod's own Update fails with "No free slot: reinstall via Launcher" (code 5377).
- Nod was installed via Launcher Web UI OTA; the install took about 13 s.
- Free space starts at 0x350000.
- To update: Launcher Web UI -> OTA Update -> choose the .bin -> Start Update.
- For on-device Update to work: add a second OTA App partition in Launcher's Partition Manager (uses the free space from 0x350000).

## Remote diagnosis (no cable)

- `GET http://<device>/api/status`: `fw_build`, `fw_running_slot`, `fw_next_slot`, `fw_slot_size`, `fw_ota_state`, `fw_otadata_present`, `fw_last_stage`, `fw_last_error`, `fw_last_error_code` (ESP error code; name is inside `fw_last_error`; 0 = none).
- Core: every failed (and successful) update POSTs `/fw/report`; log line `fw report: ...`; last one at `GET /core/update` under `fw_report`.
- Stages: precheck, manifest, begin, download, write, verify, boot, ok.
