# piblo-mcp

MCP server (stdio) that lets Claude Code, Codex, and other MCP apps notify you and ask for approval
through Piblo Core. It is a **thin adapter** over Core's HTTP API — no orchestration, no shell, no
notification ever becomes a command.

## Build & test

```
cd host/mcp
npm install        # or npm ci
npm test           # builds (tsc) then runs node --test (14 unit tests against a scripted fake Core)
```

## Connect an app

Open Core's `/sim` page, press **Connect**, then copy the block from **Connect an app** (it also lists
`claude mcp add …` and the Codex `config.toml`). The config points at `dist/index.js` and sets
`PIBLO_URL`; **the token is found automatically** — never pasted into the command.

The token is resolved in this order: `PIBLO_TOKEN` / `NOD_TOKEN` / `MAZ_TOKEN` env, then a dotenv file
(`PIBLO_ENV_FILE`, else `host/.env`). Core keeps its token in `host/.env`; no OS keyring dependency.

## Tools

| Tool | What it does | Notes |
|---|---|---|
| `piblo_status` | Connected / simulated / last seen, halt state. | Read-only. |
| `piblo_notify` | Show a notification (info / task_done / reminder / deadline). | ack-only; nothing in it is run. |
| `piblo_task_update` | Report a task's status + progress %. | Same `task_id` for every update. |
| `piblo_request_approval` | Ask the user to approve/reject ONE action; waits ~55 s. | Returns `approved` / `rejected` / `expired`. Treat expired like rejected. `sensitive=true` asks for the Nod hold. |
| `piblo_device_state` | Battery + connectivity only. | Allow-listed fields. |

Agent identity: `PIBLO_AGENT_NAME`, else the MCP app's announced client name. Length-limited and
zod-validated inputs; everything fails closed (unknown decision → rejected; unreachable Core → rejected).
