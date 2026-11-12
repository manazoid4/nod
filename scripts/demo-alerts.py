#!/usr/bin/env python3
"""One-command demo of the 3 Piblo Buddy alert workflows against a running Piblo Core.

    set MAZ_TOKEN=<your Core token>          (never printed)
    python scripts/demo-alerts.py [--url http://127.0.0.1:8787] [--only reminder|approval|webhook|nod]

Workflows (each waits for you to answer on the Cardputer before the next one):
  1. reminder : chime + edge flash + Buddy "needs attention"; press A (ack) or S (snooze)
  2. approval : the SAME approval queue Claude Code uses; press Y to allow or N to deny
  3. webhook  : "CI failed on main" (urgent, loud) then "SLA breach" (high); press A
  4. nod      : "Pay Acme GBP 42.00" - HOLD Y ~0.8 s to approve (a short press does nothing), N stops.
              Only runs with --only nod, so the default demo is unchanged.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def call(base: str, token: str, method: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        base.rstrip("/") + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> HTTP {e.code} {e.read().decode(errors='replace')[:200]}")
    except OSError as e:
        sys.exit(f"cannot reach Core at {base}: {e}")


def wait_alert(base: str, token: str, aid: str, secs: int = 120) -> str:
    end = time.time() + secs
    while time.time() < end:
        for a in call(base, token, "GET", "/buddy/alerts")["alerts"]:
            if a["id"] == aid and a["outcome"] in ("acked", "snoozed"):
                return a["outcome"]
        time.sleep(1.5)
    return "no answer"


def wait_approval(base: str, token: str, rid: str) -> str:
    st = call(base, token, "GET", f"/buddy/state?id={rid}&wait=30")
    return st.get("decision") or "no answer (timed out; falls back to terminal)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("MAZ_CORE_URL", "http://127.0.0.1:8787"))
    ap.add_argument("--only", choices=["reminder", "approval", "webhook", "nod"])
    args = ap.parse_args()
    token = os.environ.get("MAZ_TOKEN", "")
    if not token:
        sys.exit("Set MAZ_TOKEN to your Core token first.")
    run = lambda name: args.only in (None, name) and (name != "nod" or args.only == "nod")  # noqa: E731

    if run("reminder"):
        print("1/3 Reminder -> device (A = ack, S = snooze)")
        r = call(args.url, token, "POST", "/buddy/alert", {
            "source": "reminder", "kind": "reminder", "title": "Stand up and stretch",
            "body": "Reminder from Piblo Core", "priority": "high", "actions": ["ack", "snooze"]})
        print("   outcome:", wait_alert(args.url, token, r["id"]))
    if run("approval"):
        print("2/3 Agent approval -> device (Y = allow, N = deny)")
        r = call(args.url, token, "POST", "/buddy/alert", {
            "source": "demo-agent", "kind": "approval", "title": "Bash", "body": "npm test"})
        print("   decision:", wait_approval(args.url, token, r["id"]))
    if run("webhook"):
        print("3/3 Webhook alerts -> device (A = ack)")
        for body in ({"source": "ci", "kind": "computer", "title": "CI failed on main",
                      "body": "build #482 - 3 tests failing", "priority": "urgent"},
                     {"source": "helpdesk", "kind": "sla", "title": "SLA breach: ticket #123",
                      "body": "Customer waiting 4h", "priority": "high", "actions": ["ack", "snooze"]}):
            r = call(args.url, token, "POST", "/buddy/alert", body)
            print(f"   {body['title']}: {wait_alert(args.url, token, r['id'])}")
    if run("nod"):
        print("The Nod -> device (short press does nothing; HOLD Y 0.8 s = approve, N = stop)")
        r = call(args.url, token, "POST", "/buddy/alert", {
            "source": "demo-bank", "kind": "approval", "title": "Pay Acme", "body": "Invoice 1042",
            "nod": True, "category": "payment", "amount": "£42.00", "recipient": "Acme Ltd"})
        print("   decision:", wait_approval(args.url, token, r["id"]))
        print("   nod log :", [(n["title"], n["outcome"]) for n in call(args.url, token, "GET", "/buddy/nods")["nods"][:3]])
    print("Done. Full history: GET /buddy/alerts")


if __name__ == "__main__":
    main()
