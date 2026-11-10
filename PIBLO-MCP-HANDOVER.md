# Piblo MCP companion — handover

What shipped in `feat/mcp-companion` (continued from WIP, not restarted).

## What works

- **Durable store** `host/mazhost/buddy_store.py` (stdlib sqlite3, WAL, versioned migrations): alerts,
  approvals, notifications, tasks, agents, connections, prefs, activity. Bounded tables + retention.
  Write-through from `Buddy`; reload on start. Corrupt DB → moved to `*.corrupt-<n>`, fresh start, logged.
  Export/reset behind the token.
- **Approval safety:** on open every still-pending approval is expired (`decided_by: "restart"`) — never
  replayed, never auto-approved. Timeouts and lost connections fail closed (reject).
- **Tasks** (`/buddy/task`): agents report status; first `done`/`failed` raises one alert so firmware
  needs no change.
- **MCP server** `host/mcp/` (TypeScript, official `@modelcontextprotocol/{client,server}` v2, stdio):
  `piblo_status`, `piblo_notify`, `piblo_task_update`, `piblo_request_approval`, `piblo_device_state`.
  Thin adapter, zod-validated, fail closed. Token from env or `host/.env`.
- **Simulator** `/sim` (`host/mazhost/static/sim/index.html`, plain HTML/JS): a 240×135 virtual
  Cardputer that drives the same `/buddy/*` routes as firmware, with **Test Piblo**, Approve/Reject,
  Ack/Snooze, and a **Connect an app** copy box (Claude Code + Codex).
- **End-to-end test** `host/tests/test_mcp_e2e.py`: real Core + real piblo-mcp (stdio) + a headless
  simulator. Covers notify → sim approves → client gets `approved` → restart Core → history kept and a
  pending approval is expired (not replayed) → duplicate idempotency key → no-answer expiry → corrupt
  DB recovery.

## How tested (exact commands)

- `cd host/mcp && npm test` → 14 passed (build + node --test)
- `uv run pytest host/tests/test_mcp_e2e.py -p no:xdist` → 4 passed
- `uv run pytest host/tests -q` → **412 passed, 3 skipped**

## What is simulated / needs the device

- The simulator is the "device" for all of the above. Nothing here was tested on hardware.
- Remaining device work is unchanged from `docs/ALERTS.md` / `AGENT-DEVICE-CONTROL.md`: firmware must
  eventually report battery/connectivity via `/buddy/device-state` (it already reads `/buddy/status`).

## Next actions

- Claude reviews and merges once CI is green (the firmware and Android lanes merge separately).
- Android lane adds the phone sender; MCP and Android merge in any order.

## Attribution / reuse

- Reused `work_store.py`'s sqlite pattern (WAL, integrity-check, migrations) as the template for
  `buddy_store.py`. Official MCP TypeScript SDK v2 packages (`@modelcontextprotocol/*`).
