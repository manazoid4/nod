"""scripts/fw-size-report.py: map parsing, owner grouping, headroom gate (no toolchain needed)."""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "fw-size-report.py"
spec = importlib.util.spec_from_file_location("fw_size_report", SCRIPT)
fsr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fsr)

MAP = """Archive member included to satisfy reference by file (symbol)

.pio/build/cardputer-adv/libbfc/libSPI.a(SPI.cpp.o)
                              src/x.o (SPIClass::begin)

Linker script and memory map

LOAD src/net/core_client.cpp.o
.iram0.text     0x40374000     0x100
 .iram0.text.a  0x40374000      0x40 .pio/build/cardputer-adv/libfoo/libFoo@src-0123abcd.a(Foo.cpp.o)
 *(.iram0.text)
.flash.text     0x42000020    0x2000
 .text.setup    0x42000020     0x60 .pio/build/cardputer-adv/src/net/core_client.cpp.o
 .text.long_name_split_over_two_lines
                0x42000080     0x30 .pio/build/cardputer-adv/src/core/alerts.cpp.o
 .text.zero     0x420000b0      0x0 .pio/build/cardputer-adv/src/core/alerts.cpp.o
 .text.lib      0x420000b0     0x90 C:/x/.platformio/packages/f/sdk/lib/liblwip.a(tcp.c.o)
.dram0.bss      0x3fc90000    0x500
 .bss.buf       0x3fc90000    0x500 .pio/build/cardputer-adv/src/core/alerts.cpp.o
.debug_info     0x0           0x999
 .debug_info    0x0           0x999 .pio/build/cardputer-adv/src/core/alerts.cpp.o
"""


def test_owner_groups_archives_and_our_dirs():
    assert fsr.owner(r".pio\build\cardputer-adv\lib1\libFoo@src-0123abcd.a(Foo.cpp.o)") == "libFoo.a"
    assert fsr.owner(".pio/build/cardputer-adv/src/core/alerts.cpp.o") == "src/core"
    assert fsr.owner(".pio/build/cardputer-adv/src/main.cpp.o") == "main.cpp.o"


def test_parse_map_counts_image_sections_only():
    owners, sections = fsr.parse_map(MAP)
    assert owners["libFoo.a"] == 0x40  # iram0.text counts toward the image
    assert owners["src/net"] == 0x60
    assert owners["src/core"] == 0x30  # split-line entry counted, 0-byte and bss/debug entries not
    assert owners["liblwip.a"] == 0x90
    assert sections[".dram0.bss"] == 0x500 and ".debug_info" in sections


def make_build(tmp_path, size, text=MAP):
    d = tmp_path / "b" / "cardputer-adv"
    d.mkdir(parents=True)
    (d / "firmware.bin").write_bytes(b"\0" * size)
    (d / "firmware.map").write_text(text)
    return str(tmp_path / "b")


def test_headroom_gate_and_baseline(tmp_path, capsys):
    build_dir = make_build(tmp_path, fsr.SLOT - 20000)
    base = tmp_path / "base.json"
    assert fsr.main(["--build-dir", build_dir, "--save", str(base)]) == 0
    saved = json.loads(base.read_text())
    assert saved["headroom"] == 20000 and saved["ram_static"] == 0x100 + 0x500
    assert fsr.main(["--build-dir", build_dir, "--baseline", str(base), "--min-headroom", "16384"]) == 0
    assert "baseline" in capsys.readouterr().out
    assert fsr.main(["--build-dir", build_dir, "--min-headroom", "32768"]) == 1


def test_image_larger_than_slot_always_fails(tmp_path):
    assert fsr.main(["--build-dir", make_build(tmp_path, fsr.SLOT + 1)]) == 1
