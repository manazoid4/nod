from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from mazhost.accessories import Accessories, parse_request


@pytest.mark.parametrize("text,accessory,params", [
    ("make me a stand at 60 degrees", "stand", {"angle": 60}),
    ("stand at 200 degrees", "stand", {"angle": 80}),
    ("stand at -20 degrees", "stand", {"angle": 30}),
    ("wall mount with screws", "mount", {"attachment": "screw"}),
    ("fridge mount with magnets", "mount", {"attachment": "magnet"}),
    ("lanyard loop", "loop", {"hole_d": 5}),
    ("keyring loop", "loop", {"hole_d": 5}),
])
def test_parse(text, accessory, params):
    assert parse_request(text) == {"accessory": accessory, "params": params}


def test_unknown_and_ambiguous_request_rejected():
    for text in ["make a dragon", "", "stand and fridge mount"]:
        with pytest.raises(ValueError):
            parse_request(text)


def test_standalone_scad_uses_case_dimensions(tmp_path, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    result = Accessories(tmp_path).make("stand at 60 degrees")
    source = Path(result["path"]).read_text()
    assert result["format"] == "scad" and "Open this in OpenSCAD to export" in result["text"]
    assert "angle = 60;" in source
    assert "dev_L = 84.0;" in source and "wall = 2.4;" in source
    assert "include <" not in source
    assert Path(result["path"]).is_relative_to(tmp_path)
    assert "print-tested" not in result["text"]


def test_fake_openscad_on_path(tmp_path, monkeypatch):
    fake = tmp_path / "openscad.exe"
    fake.touch()
    monkeypatch.setenv("PATH", str(tmp_path))
    def render(args, **kwargs):
        assert Path(args[0]) == fake
        assert kwargs["timeout"] > 0
        Path(args[2]).write_text("solid fixture\nendsolid fixture\n")
        return subprocess.CompletedProcess(args, 0, "", "")
    monkeypatch.setattr(subprocess, "run", render)
    result = Accessories(tmp_path).make("fridge mount")
    assert result["format"] == "stl"
    assert Path(result["path"]).suffix == ".stl" and Path(result["path"]).exists()
    assert 'attachment = "magnet";' in Path(result["scad_path"]).read_text()


def test_render_failure_returns_scad_without_claiming_success(tmp_path, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "openscad")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "failed"))
    result = Accessories(tmp_path).make("keyring loop")
    assert result["format"] == "scad" and "Open this in OpenSCAD to export" in result["text"]
