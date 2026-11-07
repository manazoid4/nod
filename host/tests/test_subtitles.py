from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time
import wave
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from mazhost.app import create_app
from mazhost.config import Settings
from mazhost.subtitles import (
    SubtitleError,
    SubtitleJobs,
    build_srt,
    format_timestamp,
    resolve_video,
    subtitle_target,
)

TOKEN = "test-token-that-is-not-default"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def seg(start, end, text):
    return SimpleNamespace(start=start, end=end, text=text)


class FakeTranscriber:
    """Yields segments lazily, optionally slowly, like faster-whisper."""

    def __init__(self, segments=None, duration=10.0, delay=0.0, gate=None):
        self.segments = segments if segments is not None else [
            seg(0.0, 2.5, " Hello there."),
            seg(2.5, 6.0, " Second line, ünïcode ✓"),
            seg(6.0, 10.0, " The end."),
        ]
        self.duration = duration
        self.delay = delay
        self.gate = gate
        self.calls = []

    def transcribe(self, media, language):
        self.calls.append((Path(media), language))

        def gen():
            for item in self.segments:
                if self.gate is not None:
                    self.gate.wait(5)
                if self.delay:
                    time.sleep(self.delay)
                yield item

        return gen(), self.duration, language or "en"


def settings_for(root: Path, **extra) -> Settings:
    return Settings(_env_file=None, token=TOKEN, media_roots=str(root), **extra)


def make_jobs(root: Path, transcriber=None, **kwargs) -> SubtitleJobs:
    kwargs.setdefault("ffmpeg", None)
    kwargs.setdefault("vlc_finder", lambda: None)
    return SubtitleJobs(settings_for(root), transcriber or FakeTranscriber(), **kwargs)


def wait_final(jobs: SubtitleJobs, job_id: str, timeout: float = 5.0) -> dict:
    end = time.time() + timeout
    while time.time() < end:
        status = jobs.status(job_id)
        if status["state"] in {"done", "failed", "cancelled"}:
            return status
        time.sleep(0.02)
    raise AssertionError(f"job did not finish: {jobs.status(job_id)}")


@pytest.fixture()
def media(tmp_path):
    root = tmp_path / "Videos"
    root.mkdir()
    video = root / "clip.mp4"
    video.write_bytes(b"not really a video")
    return root, video


# ------------------------------------------------------------------ SRT
def test_format_timestamp():
    assert format_timestamp(0) == "00:00:00,000"
    assert format_timestamp(1.25) == "00:00:01,250"
    assert format_timestamp(61.5) == "00:01:01,500"
    assert format_timestamp(3725.007) == "01:02:05,007"
    assert format_timestamp(-3) == "00:00:00,000"
    assert format_timestamp(59.9996) == "00:01:00,000"


def test_build_srt_sequential_and_skips_empty():
    text = build_srt([
        seg(0, 1.5, " Hi "),
        seg(1.5, 2.0, "   "),
        seg(2.0, 2.0, "Zero length\r\n second row"),
    ])
    assert text == (
        "1\n00:00:00,000 --> 00:00:01,500\nHi\n"
        "\n"
        "2\n00:00:02,000 --> 00:00:02,001\nZero length\nsecond row\n"
    )


# ------------------------------------------------------- confinement
def test_resolve_accepts_inside_and_relative(media):
    root, video = media
    assert resolve_video(str(video), [root.resolve()]) == video.resolve()
    assert resolve_video("clip.mp4", [root.resolve()]) == video.resolve()


def test_resolve_rejects_traversal(media, tmp_path):
    root, _ = media
    outside = tmp_path / "secret.mp4"
    outside.write_bytes(b"x")
    with pytest.raises(SubtitleError, match="path_outside_media_folders"):
        resolve_video(str(root / ".." / "secret.mp4"), [root.resolve()])
    with pytest.raises(SubtitleError, match="path_outside_media_folders"):
        resolve_video("../secret.mp4", [root.resolve()])
    with pytest.raises(SubtitleError, match="path_outside_media_folders"):
        resolve_video(str(outside), [root.resolve()])


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_resolve_rejects_symlink_escape(media, tmp_path):
    root, _ = media
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (outside / "movie.mkv").write_bytes(b"x")
    (root / "link.mkv").symlink_to(outside / "movie.mkv")
    (root / "linkdir").symlink_to(outside, target_is_directory=True)
    for raw in (str(root / "link.mkv"), str(root / "linkdir" / "movie.mkv")):
        with pytest.raises(SubtitleError, match="path_outside_media_folders"):
            resolve_video(raw, [root.resolve()])


def test_resolve_rejects_non_video_missing_and_dirs(media):
    root, _ = media
    (root / "notes.txt").write_text("x")
    (root / "evil.mp4.exe").write_bytes(b"x")
    (root / "folder.mp4").mkdir()
    roots = [root.resolve()]
    with pytest.raises(SubtitleError, match="not_a_video_file"):
        resolve_video(str(root / "notes.txt"), roots)
    with pytest.raises(SubtitleError, match="not_a_video_file"):
        resolve_video(str(root / "evil.mp4.exe"), roots)
    with pytest.raises(SubtitleError, match="not_a_file"):
        resolve_video(str(root / "folder.mp4"), roots)
    with pytest.raises(SubtitleError, match="video_not_found"):
        resolve_video(str(root / "missing.mp4"), roots)
    with pytest.raises(SubtitleError, match="no_media_folders_configured"):
        resolve_video(str(root / "clip.mp4"), [])


def test_target_never_clobbers_existing_srt(media):
    _, video = media
    assert subtitle_target(video, False) == video.with_suffix(".srt")
    video.with_suffix(".srt").write_text("mine")
    assert subtitle_target(video, False).name == "clip.nod.srt"
    assert subtitle_target(video, True) == video.with_suffix(".srt")


# --------------------------------------------------------- lifecycle
def test_job_writes_srt_and_reports_measured_duration(media):
    root, video = media
    fake = FakeTranscriber()
    jobs = make_jobs(root, fake)
    started = jobs.start(str(video), "auto")
    assert started["state"] in {"queued", "transcribing", "done"}
    done = wait_final(jobs, started["id"])
    assert done["state"] == "done" and done["ok"] is True
    assert done["progress"] == 100 and done["segments"] == 3
    assert done["audio_source"] == "direct"
    assert done["duration_ms"] >= 0 and done["media_seconds"] == 10.0
    assert fake.calls == [(video.resolve(), None)]
    srt = Path(done["srt"])
    assert srt == video.with_suffix(".srt").resolve()
    body = srt.read_text(encoding="utf-8")
    assert body.startswith("1\n00:00:00,000 --> 00:00:02,500\nHello there.\n")
    assert "3\n00:00:06,000 --> 00:00:10,000\nThe end.\n" in body
    assert "ünïcode ✓" in body
    assert not list(root.glob(".nod-*"))


def test_language_code_is_passed_and_validated(media):
    root, video = media
    fake = FakeTranscriber()
    jobs = make_jobs(root, fake)
    wait_final(jobs, jobs.start(str(video), "DE")["id"])
    assert fake.calls[-1][1] == "de"
    for bad in ("english", "e1", "../x", "en-US"):
        with pytest.raises(SubtitleError, match="invalid_language"):
            jobs.start(str(video), bad)


def test_progress_and_cancel_midway(media):
    root, video = media
    gate = threading.Event()
    fake = FakeTranscriber(gate=gate)
    jobs = make_jobs(root, fake)
    job_id = jobs.start(str(video))["id"]
    end = time.time() + 3
    while jobs.status(job_id)["state"] != "transcribing" and time.time() < end:
        time.sleep(0.01)
    assert jobs.status(job_id)["label"].startswith("TRANSCRIBING")
    jobs.cancel(job_id)
    gate.set()
    final = wait_final(jobs, job_id)
    assert final["state"] == "cancelled" and final["ok"] is False
    assert not video.with_suffix(".srt").exists()
    assert not list(root.glob(".nod-*"))


def test_cancel_queued_job_never_runs(media):
    root, video = media
    gate = threading.Event()
    fake = FakeTranscriber(gate=gate)
    jobs = make_jobs(root, fake)
    first = jobs.start(str(video))["id"]
    second = jobs.start(str(video), overwrite=True)["id"]
    assert jobs.status(second)["state"] == "queued"
    assert jobs.cancel(second)["state"] == "cancelled"
    gate.set()
    wait_final(jobs, first)
    time.sleep(0.1)
    assert len(fake.calls) == 1
    assert jobs.status(second)["state"] == "cancelled"


def test_timeout_fails_job(media):
    root, video = media
    fake = FakeTranscriber(delay=0.2)
    jobs = make_jobs(root, fake, timeout_seconds=0.25)
    final = wait_final(jobs, jobs.start(str(video))["id"])
    assert final["state"] == "failed" and final["error"] == "timeout"
    assert not video.with_suffix(".srt").exists()


def test_transcriber_failure_is_a_failed_state(media):
    root, video = media

    class Broken:
        def transcribe(self, media, language):
            raise RuntimeError("model exploded")

    jobs = make_jobs(root, Broken())
    final = wait_final(jobs, jobs.start(str(video))["id"])
    assert final["state"] == "failed" and "model exploded" in final["error"]


def test_ffmpeg_failure_reported(media, tmp_path):
    root, video = media
    fake_ffmpeg = tmp_path / "ffmpeg"
    fake_ffmpeg.write_text("#!/bin/sh\necho boom >&2\nexit 3\n")
    fake_ffmpeg.chmod(0o755)
    if os.name == "nt":
        pytest.skip("shell script stand-in needs POSIX")
    jobs = make_jobs(root, ffmpeg=str(fake_ffmpeg))
    final = wait_final(jobs, jobs.start(str(video))["id"])
    assert final["state"] == "failed"
    assert final["error"].startswith("audio_extraction_failed") and "boom" in final["error"]
    assert final["audio_source"] == "ffmpeg"


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
def test_real_ffmpeg_extracts_16k_mono_wav(media):
    root, _ = media
    video = root / "tone.mkv"
    subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
         "-f", "lavfi", "-i", "color=c=black:s=64x64:d=1", "-shortest", str(video)],
        check=True,
    )
    seen = {}

    class Inspect(FakeTranscriber):
        def transcribe(self, media, language):
            with wave.open(str(media), "rb") as wav:
                seen.update(rate=wav.getframerate(), channels=wav.getnchannels())
            return super().transcribe(media, language)

    jobs = make_jobs(root, Inspect(), ffmpeg=True)
    final = wait_final(jobs, jobs.start(str(video))["id"], timeout=20)
    assert final["state"] == "done" and final["audio_source"] == "ffmpeg"
    assert seen == {"rate": 16000, "channels": 1}


# --------------------------------------------------------------- VLC
def test_vlc_missing_is_graceful(media):
    root, video = media
    jobs = make_jobs(root, vlc_finder=lambda: None)
    final = wait_final(jobs, jobs.start(str(video), open_vlc=True)["id"])
    assert final["state"] == "done"
    assert final["vlc"] == {"requested": True, "opened": False, "reason": "vlc_not_found"}


def test_vlc_opened_with_argument_list(media):
    root, video = media
    opened = []
    jobs = make_jobs(
        root,
        vlc_finder=lambda: "/opt/vlc",
        vlc_opener=lambda vlc, v, s: opened.append((vlc, v, s)),
    )
    final = wait_final(jobs, jobs.start(str(video), open_vlc=True)["id"])
    assert final["vlc"]["opened"] is True
    assert opened == [("/opt/vlc", video.resolve(), Path(final["srt"]))]


# --------------------------------------------------------------- API
def api_client(root: Path, jobs: SubtitleJobs | None = None) -> TestClient:
    settings = settings_for(root)
    return TestClient(create_app(settings, subtitles=jobs or make_jobs(root)))


def test_endpoints_require_auth(media):
    root, video = media
    api = api_client(root)
    assert api.post("/subtitles/job", json={"path": str(video)}).status_code == 401
    assert api.get("/subtitles/job/abc").status_code == 401
    assert api.post("/subtitles/job/abc/cancel").status_code == 401
    assert api.get("/subtitles/videos").status_code == 401
    bad = {"Authorization": "Bearer wrong"}
    assert api.post("/subtitles/job", headers=bad, json={"path": str(video)}).status_code == 401


def test_api_lifecycle_and_rejections(media, tmp_path):
    root, video = media
    jobs = make_jobs(root)
    api = api_client(root, jobs)

    listing = api.get("/subtitles/videos", headers=HEADERS)
    assert listing.status_code == 200
    assert [v["name"] for v in listing.json()["videos"]] == ["clip.mp4"]

    started = api.post("/subtitles/job", headers=HEADERS, json={"path": str(video), "language": "en"})
    assert started.status_code == 200
    job_id = started.json()["id"]
    wait_final(jobs, job_id)
    status = api.get(f"/subtitles/job/{job_id}", headers=HEADERS).json()
    assert status["state"] == "done" and status["language"] == "en"
    assert api.post(f"/subtitles/job/{job_id}/cancel", headers=HEADERS).json()["state"] == "done"
    assert api.get("/subtitles/jobs", headers=HEADERS).json()["jobs"][0]["id"] == job_id

    (tmp_path / "x.mp4").write_bytes(b"x")
    outside = api.post("/subtitles/job", headers=HEADERS, json={"path": "../x.mp4"})
    assert outside.status_code == 400 and outside.json()["detail"] == "path_outside_media_folders"
    assert api.get("/subtitles/job/nope", headers=HEADERS).status_code == 404
    assert api.post("/subtitles/job/nope/cancel", headers=HEADERS).status_code == 404
