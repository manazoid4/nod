#!/usr/bin/env node
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import { CoreClient, loadConfig } from "./core.js";
import { createServer } from "./server.js";

const cfg = loadConfig();
if (!cfg.token) console.error("piblo-mcp: no token found (PIBLO_TOKEN or host/.env); tools will report no_token");

// stdout is the protocol channel: log to stderr only.
const handle = serveStdio(() => createServer(new CoreClient(cfg), cfg.agent));
console.error(`piblo-mcp ready (Core ${cfg.url})`);
for (const sig of ["SIGINT", "SIGTERM"] as const) process.on(sig, () => void handle.close().finally(() => process.exit(0)));
