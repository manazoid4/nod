#!/usr/bin/env python3
"""Drive the Piblo Cardputer remotely via MAZ Core (agents only need Core's token).

Commands:
  status                  print device status (app, volume, brightness, battery)
  screen <out.png>        save a PNG screenshot of the LCD
  keys "<spec>"           press keys: "down right*7 esc" (see docs)
  open <app-id>           open a surface/app
  volume <0-100>          set volume percent
  brightness <0-100>      set brightness percent
"""
import json
import os
import sys
import urllib.error
import urllib.request

CORE = "http://host.docker.internal:8787"


def token():
    return os.environ.get("MAZ_TOKEN", "")


def call(path, method="GET", data=None):
    url = CORE + path
    body = None
    headers = {"Authorization": f"Bearer {token()}"}
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read(), resp.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), {}


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def main(argv):
    if not argv:
        die("usage: piblo_remote.py status|screen|keys|open|volume|brightness ...")
    cmd, args = argv[0], argv[1:]

    if cmd == "status":
        code, body, _ = call("/core/cardputer/status")
        print(body.decode() if code == 200 else f"status {code}: {body.decode()}")
        return 0 if code == 200 else 1

    if cmd == "screen":
        if not args:
            die("screen needs an output path")
        code, body, _ = call("/core/cardputer/screen.png")
        if code != 200:
            die(f"screen {code}: {body.decode()}")
        with open(args[0], "wb") as f:
            f.write(body)
        print(f"saved {args[0]} ({len(body)} bytes)")
        return 0

    if cmd == "keys":
        if not args:
            die("keys needs a spec, e.g. 'down right*7 esc'")
        code, body, _ = call("/core/cardputer/key", "POST", {"keys": args[0]})
        print(body.decode() if code == 200 else f"keys {code}: {body.decode()}")
        return 0 if code == 200 else 1

    if cmd == "open":
        if not args:
            die("open needs an app id, e.g. settings")
        code, body, _ = call("/core/cardputer/action", "POST", {"action": f"open:{args[0]}"})
        print(body.decode() if code == 200 else f"open {code}: {body.decode()}")
        return 0 if code == 200 else 1

    if cmd == "volume":
        if not args:
            die("volume needs 0-100")
        code, body, _ = call("/core/cardputer/config", "POST", {"volume": int(args[0])})
        print(body.decode() if code == 200 else f"volume {code}: {body.decode()}")
        return 0 if code == 200 else 1

    if cmd == "brightness":
        if not args:
            die("brightness needs 0-100")
        code, body, _ = call("/core/cardputer/config", "POST", {"brightness": int(args[0])})
        print(body.decode() if code == 200 else f"brightness {code}: {body.decode()}")
        return 0 if code == 200 else 1

    die(f"unknown command: {cmd}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Remote-control the Piblo Cardputer via MAZ Core.")
    parser.add_argument("--core", default=CORE, help="Core base URL")
    parser.add_argument("--token", default=None, help="Override MAZ_TOKEN from the environment")
    parser.add_argument("command")
    parser.add_argument("operands", nargs="*")
    ns = parser.parse_args()
    CORE = ns.core
    if ns.token:
        os.environ["MAZ_TOKEN"] = ns.token
    sys.exit(main([ns.command, *ns.operands]))