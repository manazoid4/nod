# Private mode

**Piblo Core makes no internet requests** while private mode is on. Core's HTTP
transports check each request, and live voice checks each upstream connection.
Cloud agents, arbitrary shells, project builds/tests, remote discovery, GitHub
CLI operations and self-update are refused with `PRIVATE_MODE`. Fixed local
capture, clipboard, media and hardware-query tools may still run, along with
read-only Git queries. Local model servers and LAN communication remain available.

Turning private mode on is immediate. Turning it off waits for a fresh Ask on
Piblo approval (category `other`). Denial, cancellation or a 60-second timeout
keeps it on; an allowed decision is persisted before the endpoint returns.

The socket-blocking test covers chat, cloud refusal, agent/shell routes, live
voice, library ingest/search, needs, telemetry, update and GitHub bridge polling.
Look is checked through its service: its router is not installed in the main app.
Library URL ingest stores a reference; it does not download the page.

This is a Core request policy, not an OS firewall. The tests do not prove that
other PC apps, third-party media/model runtimes or a local server never use the
internet. They do not revoke subprocesses or sockets started before the switch.
`.local` names remain allowed for mDNS: a hostile or misconfigured resolver can
resolve one to a public address. Private mode trusts local endpoints and the
machine's resolver; it does not pin resolved addresses.

Run `python -m pytest host/tests/test_private_mode.py` for the regression proof.

## Fix verification (11 November 2026)

Implemented and independently reviewed on `fable2/private`. Private-mode tests:
53 passed. Full suite command (writable temp directory and pytest cache disabled):

```
python -m pytest host/tests -n auto --basetemp .tmp-private-suite-final -p no:cacheprovider --tb=short --disable-warnings
524 passed, 3 skipped, 3714 warnings in 63.86s (0:01:03)
```

The initial full run hit the existing 300 ms dead-port timing limit (313 ms);
both subsequent full runs passed. Local test logs and temporary artifacts are
archived under ignored `host/data/private-mode-fix/`.

Git metadata is outside this writable worktree. `git rm -r --cached host/Microsoft`
failed because the worktree index lock could not be created (permission denied).
Changes remain uncommitted as the fix brief permits. No merge, deployment or
physical-device validation was performed. Next command in an unrestricted shell:
`git rm -r --cached host/Microsoft`.
