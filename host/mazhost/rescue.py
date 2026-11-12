"""Local Rescue source and a bounded plain-text copy for the device."""
from __future__ import annotations

import json
import threading
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_JSON_BYTES = 16 * 1024
MAX_COMPACT_BYTES = 2048
MAX_LINE_BYTES = 96


def _json_bytes(value: BaseModel) -> bytes:
    return json.dumps(value.model_dump(), ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class RescueContact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=64)
    phone: str = Field(min_length=1, max_length=40, pattern=r"^[+0-9() .#*xX-]+$")


class Rescue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    contacts: list[RescueContact] = Field(default_factory=list, max_length=8)
    travel: str = Field(default="", max_length=4096)
    notes: str = Field(default="", max_length=8192)
    emergency_instructions: str = Field(default="", max_length=4096)

    @model_validator(mode="after")
    def check_size(self):
        try:
            size = len(_json_bytes(self))
        except UnicodeEncodeError as error:
            raise ValueError("rescue_invalid_unicode") from error
        if size > MAX_JSON_BYTES:
            raise ValueError("rescue_json_too_large")
        return self

    def compact(self) -> str:
        lines = []
        for contact in self.contacts:
            name = " ".join(contact.name.split()).encode("utf-8")[:40].decode("utf-8", errors="ignore")
            lines.append(f"{name}: {contact.phone}")
        for label, value in (("Emergency", self.emergency_instructions), ("Travel", self.travel), ("Notes", self.notes)):
            if value.strip():
                remaining = f"{label}: {' '.join(value.split())}"
                while remaining:
                    line = remaining.encode("utf-8")[:MAX_LINE_BYTES].decode("utf-8", errors="ignore")
                    lines.append(line)
                    remaining = remaining[len(line):]
        output = []
        size = 0
        for line in lines:
            added = len(line.encode("utf-8")) + bool(output)
            if size + added > MAX_COMPACT_BYTES:
                break
            output.append(line)
            size += added
        return "\n".join(output)


def install_rescue_routes(api: FastAPI, require_token, data_dir: str | Path) -> None:
    router = APIRouter(prefix="/rescue", tags=["rescue"], dependencies=[Depends(require_token)])
    path = Path(data_dir).expanduser() / "rescue.json"
    lock = threading.Lock()

    def read() -> Rescue:
        try:
            with path.open("rb") as source:
                raw = source.read(MAX_JSON_BYTES + 1)
            if len(raw) > MAX_JSON_BYTES:
                raise ValueError("rescue_json_too_large")
            return Rescue.model_validate_json(raw)
        except FileNotFoundError:
            return Rescue()
        except ValueError as error:
            raise HTTPException(503, "rescue_data_invalid") from error
        except OSError as error:
            raise HTTPException(503, "rescue_storage_unavailable") from error

    @router.get("")
    def get_rescue():
        return read()

    @router.put("")
    def put_rescue(body: Rescue):
        try:
            with lock:
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = path.with_suffix(".tmp")
                temporary.write_bytes(_json_bytes(body))
                temporary.replace(path)
        except OSError as error:
            raise HTTPException(503, "rescue_storage_unavailable") from error
        return body

    @router.get("/compact", response_class=PlainTextResponse)
    def compact_rescue():
        return read().compact()

    api.include_router(router)
