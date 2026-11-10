# Firmware baseline (before optimisation)

Measured on `origin/main` @ `c9388f9` (v1.5.1), `pio run -e cardputer-adv`, PlatformIO 6.x,
espressif32@6.9.0 (arduino-esp32 2.0.17, gcc 8.4.0 xtensa), built on a Windows laptop. Re-measure with
`python scripts/fw-size-report.py --baseline docs/perf/fw-baseline.json`.

| metric | bytes |
|---|---:|
| `firmware.bin` (what OTA ships) | **1,490,896** |
| OTA app slot (`nodfw`, 0x170000) | 1,507,328 |
| **Headroom** | **16,432** (CI gate: >= 16,384) |
| `.flash.text` | 1,098,779 |
| `.flash.rodata` | 302,744 |
| IRAM (`.iram0.text` + vectors) | 69,358 |
| `.dram0.data` / `.dram0.bss` | 19,656 / 52,128 |
| PlatformIO "RAM" (data + bss) | 71,784 of 327,680 (21.9%) |
| PlatformIO "Flash" (ELF image) | 1,490,537 |

Free heap at runtime is not measurable without a device (`needs device`: portal `/api/status` reports `free_heap`).

## Where the 1.49 MB goes (map file, image bytes)

| owner | bytes | note |
|---|---:|---|
| our code, `src/net` | 135,117 | `portal_v3.cpp` 37.8 KB (14.4 KB is the embedded HTML page), `core_client` 25.4 KB, `field_host` 21.1 KB, `mazhost` 17.1 KB (ArduinoJson templates inlined) |
| our code, `src/apps` | 123,767 | 20 apps |
| our code, `src/core` / `audio` / `storage` / `ui` | 42,044 / 17,489 / 15,533 / 8,608 | |
| `libnet80211` + `liblwip` + `libpp` + `libphy` + `libwpa_supplicant` | 335,000 | Wi-Fi stack, prebuilt, not tunable without a custom sdkconfig |
| `libM5GFX` + `libM5Unified` | 98,051 + 55,443 | display, speaker, mic, IMU |
| `libc` | 90,048 | newlib printf/scanf/strtod (float and int variants both linked) |
| `libmbedcrypto` + `libmbedtls_2` + `libmbedx509` | 76,930 + 35,074 + 8,286 | remote HTTPS link and OTA hash; `--wrap` already drops the server handshake |
| `libesp_littlefs`, `libfatfs` | 28,174, 17,990 | internal storage, SD card |
| `libmdns` | 23,342 | `piblo.local` for the setup portal |
| `libWebSockets` | 10,631 | live screen |

Full table: `python scripts/fw-size-report.py --top 60`.

## Existing flags (already good)

`-Os`, `-ffunction-sections`, `-fdata-sections`, `-Wl,--gc-sections` (framework defaults),
`-DCORE_DEBUG_LEVEL=0`, `-fno-rtti`, `--wrap=mbedtls_strerror`, `--wrap=mbedtls_ssl_handshake_server_step`,
`--wrap=esp_core_dump_*`, M5Unified pinned to 0.2.20 (0.2.22 costs +22 KB), unused portal variants
(`portal.cpp`, `portal_v2.cpp`) excluded by `build_src_filter`. The CA bundle is only 3,439 B.
The framework also passes `-fexceptions` and `-fstack-protector`, which is where the big wins were
(see `FIRMWARE-OPTIMISATION.md`).

## Native tests (baseline)

CI runs `make -C firmware/nod test` (g++, `-std=c++11 -Wall -Wextra -Werror -O1`). This laptop has no
g++/make, so the same command line was run with Zig's bundled clang:
`uvx --from ziglang python -m ziglang c++ -std=c++11 -Wall -Wextra -Werror -O1 firmware/nod/tests/test_nod.cpp -o nod_test && ./nod_test`
-> `1487 checks, 0 failed` on main.
