#!/usr/bin/env python3
"""Piblo firmware size report: flash/RAM per build, top contributors, diff vs a baseline.

    pio run -e cardputer-adv
    python scripts/fw-size-report.py                       # print report
    python scripts/fw-size-report.py --save docs/perf/fw-baseline.json
    python scripts/fw-size-report.py --baseline docs/perf/fw-baseline.json --min-headroom 32768

Reads only .pio/build/<env>/firmware.bin and firmware.map (no toolchain needed), so it runs in CI
and on any laptop. Exit 1 when --min-headroom is not met or the image does not fit the OTA slot.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SLOT = 0x170000  # nodfw OTA app slot (docs/OTA-LAYOUT.md); same limit as the CI size gate
# Output sections stored in firmware.bin (flash footprint) vs sections living in RAM.
IMAGE = {".iram0.vectors", ".iram0.text", ".dram0.data", ".flash.text", ".flash.rodata", ".flash.appdesc"}
RAM = {".iram0.vectors", ".iram0.text", ".dram0.data", ".dram0.bss"}

_SECTION = re.compile(r"^(\.\S+)(?:\s+0x[0-9a-f]+\s+0x([0-9a-f]+))?\s*$")
_ENTRY = re.compile(r"^\s+(?:(\.\S+)\s+)?0x[0-9a-f]+\s+0x([0-9a-f]+)\s+(\S.*)$")
_PENDING = re.compile(r"^\s+(\.\S+)\s*$")


def owner(path: str) -> str:
    """Archive name for library members, containing dir for our own objects."""
    path = path.replace("\\", "/").strip()
    m = re.search(r"([^/]+\.a)\(", path)
    if m:
        return re.sub(r"@src-[0-9a-f]+", "", m.group(1))
    m = re.search(r"/(src/[^/]+(?:/[^/]+)?)/[^/]+\.o$", path)
    if m:
        return m.group(1)
    return path.rsplit("/", 1)[-1]


def parse_map(text: str):
    """Return ({owner: image_bytes}, {section: bytes})."""
    owners, sections = {}, {}
    sec, pending, in_map = None, False, False
    for line in text.splitlines():
        if not in_map:
            in_map = line.startswith("Linker script and memory map")
            continue
        m = _SECTION.match(line)
        if m and not line.startswith(" "):
            sec = m.group(1)
            if m.group(2):
                sections[sec] = sections.get(sec, 0) + int(m.group(2), 16)
            continue
        if sec is None or (sec not in IMAGE and sec not in RAM):
            continue
        m = _ENTRY.match(line)
        if m and (m.group(1) or pending):
            size, obj = int(m.group(2), 16), m.group(3)
            pending = False
            if size and not obj.startswith("*"):
                o = owner(obj)
                if sec in IMAGE:
                    owners[o] = owners.get(o, 0) + size
            continue
        pending = bool(_PENDING.match(line))
    return owners, sections


def build(env_dir: Path):
    binary = env_dir / "firmware.bin"
    mapfile = env_dir / "firmware.map"
    if not binary.exists():
        sys.exit(f"missing {binary} - run: pio run -e cardputer-adv")
    owners, sections = parse_map(mapfile.read_text(errors="replace")) if mapfile.exists() else ({}, {})
    return {
        "bin": binary.stat().st_size,
        "headroom": SLOT - binary.stat().st_size,
        "ram_static": sum(sections.get(s, 0) for s in RAM),
        "dram_data": sections.get(".dram0.data", 0),
        "dram_bss": sections.get(".dram0.bss", 0),
        "iram": sections.get(".iram0.text", 0) + sections.get(".iram0.vectors", 0),
        "flash_text": sections.get(".flash.text", 0),
        "flash_rodata": sections.get(".flash.rodata", 0),
        "owners": dict(sorted(owners.items(), key=lambda kv: -kv[1])[:60]),
    }


def fmt_delta(now, then):
    d = now - then
    return f"{d:+,}" if d else "0"


def report(cur, base=None, top=15):
    rows = [("firmware.bin", "bin"), ("OTA headroom", "headroom"), (".flash.text", "flash_text"),
            (".flash.rodata", "flash_rodata"), ("IRAM", "iram"), ("static RAM (data+bss+iram)", "ram_static"),
            (".dram0.data", "dram_data"), (".dram0.bss", "dram_bss")]
    out = [f"{'metric':32}{'now':>12}" + (f"{'baseline':>12}{'delta':>10}" if base else "")]
    for label, key in rows:
        line = f"{label:32}{cur[key]:>12,}"
        if base and key in base:
            line += f"{base[key]:>12,}{fmt_delta(cur[key], base[key]):>10}"
        out.append(line)
    out.append(f"\nslot use: {cur['bin'] * 100 / SLOT:.1f}% of {SLOT:,} bytes")
    if cur["owners"]:
        out.append(f"\ntop {top} flash contributors (image bytes)")
        for name, size in list(cur["owners"].items())[:top]:
            line = f"  {name:44}{size:>10,}"
            if base and name in base.get("owners", {}):
                line += f"{fmt_delta(size, base['owners'][name]):>10}"
            out.append(line)
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", default="cardputer-adv")
    ap.add_argument("--build-dir", default=".pio/build")
    ap.add_argument("--baseline", help="JSON written by --save; prints deltas")
    ap.add_argument("--save", help="write this build's numbers as JSON")
    ap.add_argument("--min-headroom", type=int, default=0, help="exit 1 if OTA headroom is lower (bytes)")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args(argv)

    cur = build(Path(args.build_dir) / args.env)
    base = json.loads(Path(args.baseline).read_text()) if args.baseline else None
    print(report(cur, base, args.top))
    if args.save:
        Path(args.save).write_text(json.dumps(cur, indent=1) + "\n")
    if cur["headroom"] < 0 or cur["headroom"] < args.min_headroom:
        print(f"\nFAIL: headroom {cur['headroom']:,} < required {max(args.min_headroom, 0):,}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
