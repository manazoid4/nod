"""Routes behind the Piblo Companion page: history, agents, prefs, export/reset, MCP connect info.
All of them sit behind the normal bearer token (only the static pages are public)."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .buddy import AlertIn, Buddy
from .buddy_store import BuddyStore

MCP_ENTRY = Path(__file__).resolve().parents[1] / "mcp" / "dist" / "index.js"
MAX_SHORTCUTS = 12


class Shortcut(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    title: str = Field(min_length=1, max_length=60)
    body: str = Field(default="", max_length=200)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")


class PrefsIn(BaseModel):
    retention_days: int | None = Field(default=None, ge=1, le=365)
    shortcuts: list[Shortcut] | None = Field(default=None, max_length=MAX_SHORTCUTS)


class ResetIn(BaseModel):
    confirm: bool = False


def connect_info(port: int, entry: Path = MCP_ENTRY) -> dict:
    """Copy-paste config for MCP apps. No token in it: piblo-mcp finds Core's own token (see host/mcp/README.md)."""
    url = f"http://127.0.0.1:{port}"
    path = entry.as_posix()
    return {
        "url": url, "entry": path, "built": entry.exists(),
        "claude_code_cmd": f'claude mcp add piblo --env PIBLO_URL={url} --env PIBLO_AGENT_NAME=claude-code -- node "{path}"',
        "claude_json": json.dumps({"mcpServers": {"piblo": {"command": "node", "args": [path],
                                    "env": {"PIBLO_URL": url, "PIBLO_AGENT_NAME": "claude"}}}}, indent=2),
        "codex_toml": f'[mcp_servers.piblo]\ncommand = "node"\nargs = ["{path}"]\n'
                      f'env = {{ PIBLO_URL = "{url}", PIBLO_AGENT_NAME = "codex" }}\n',
    }


def install_companion_routes(api: FastAPI, buddy: Buddy, port: int = 8787) -> None:
    def store() -> BuddyStore:
        if not buddy.store:
            raise HTTPException(503, "history_disabled")
        return buddy.store

    @api.get("/buddy/history")
    def history(limit: int = 100):
        st, n = store(), min(max(limit, 1), 500)
        return {"ok": True, "notifications": st.notifications(n), "approvals": st.approvals(n),
                "alerts": [{**a["data"], "outcome": a["outcome"], "agent": a["agent"]} for a in st.alerts(n)]}

    @api.get("/buddy/agents")
    def agents():
        return {"ok": True, "agents": store().agents()}

    @api.get("/buddy/activity")
    def activity(limit: int = 100):
        return {"ok": True, "activity": store().activity(min(max(limit, 1), 500))}

    @api.get("/buddy/prefs")
    def prefs_get():
        st = store()
        return {"ok": True, "retention_days": st.retention_days(), "shortcuts": st.get_pref("shortcuts", [])}

    @api.put("/buddy/prefs")
    def prefs_put(body: PrefsIn):
        st = store()
        if body.retention_days is not None:
            st.set_pref("retention_days", body.retention_days)
            st.prune()
        if body.shortcuts is not None:
            st.set_pref("shortcuts", [s.model_dump() for s in body.shortcuts])
        return prefs_get()

    @api.get("/buddy/export")
    def export():
        return Response(json.dumps(store().export(), indent=2), media_type="application/json",
                        headers={"Content-Disposition": 'attachment; filename="piblo-export.json"'})

    @api.post("/buddy/reset")
    def reset(body: ResetIn):
        if not body.confirm:
            raise HTTPException(400, "confirm_required")
        store().reset()
        return {"ok": True}

    @api.get("/buddy/connect-info")
    def connect():
        return {"ok": True, **connect_info(port)}

    @api.post("/buddy/demo")
    def demo():
        """'Test Piblo': one notification + one approval so the flow has both to show. No device needed."""
        note = buddy.post_alert(AlertIn(source="piblo", kind="info", title="Hello from Piblo",
                                        body="This is a demo notification. Everything is working.",
                                        priority="normal"))
        approval = buddy.request("Test Piblo", "Demo approval: approve to see the answer reach the app.",
                                 agent="demo", sensitive=False)
        return {"ok": True, "notification_id": note.get("id"), "approval_id": approval["id"]}
