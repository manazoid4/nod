from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .subtitles import SubtitleError, SubtitleJobs


class SubtitleStartRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="auto", min_length=2, max_length=8)
    open_vlc: bool = False
    overwrite: bool = False


def install_subtitle_routes(api: FastAPI, jobs: SubtitleJobs) -> None:
    @api.get("/subtitles/videos")
    def subtitle_videos(limit: int = 50):
        if not jobs.roots:
            raise HTTPException(503, "no_media_folders_configured")
        return {"ok": True, "roots": [str(r) for r in jobs.roots], "videos": jobs.videos(limit)}

    @api.post("/subtitles/job")
    def subtitle_start(body: SubtitleStartRequest):
        try:
            return jobs.start(body.path, body.language, body.open_vlc, body.overwrite)
        except SubtitleError as error:
            raise HTTPException(400, str(error)) from error

    @api.get("/subtitles/job/{job_id}")
    def subtitle_status(job_id: str):
        try:
            return jobs.status(job_id)
        except SubtitleError as error:
            raise HTTPException(404, str(error)) from error

    @api.post("/subtitles/job/{job_id}/cancel")
    def subtitle_cancel(job_id: str):
        try:
            return jobs.cancel(job_id)
        except SubtitleError as error:
            raise HTTPException(404, str(error)) from error

    @api.get("/subtitles/jobs")
    def subtitle_jobs(limit: int = 20):
        return {"ok": True, "jobs": jobs.recent(limit)}
