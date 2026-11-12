# Piblo for Windows

The Windows app for Piblo. It finds your Piblo on the same Wi-Fi, you press **Allow** once, and from
then on you can see its screen, send keys, type for it, take screenshots and handle its settings from
the PC. No tokens, no terminals, no jargon.

```
Home       what Piblo is doing, battery, software, and a note to send it
Live View  its screen at 2 fps, on-screen buttons, "type on Piblo", Save screenshot
Ask        talk to the same brain Piblo uses
Memory     everything Piblo heard and everything you saved
Actions    approvals that are waiting for you
Settings   connecting, brains, privacy, the app itself
```

## Run it from source

```bat
cd app
npm install
npm run dev        :: real Piblo on this PC (python -m mazhost in host/)
npm run dev:mock   :: no Python, no hardware: scripts/mock-core.mjs pretends to be everything
```

`npm run dev:mock` starts a mock of Piblo on this PC on a free port, including a pending pairing
request and a real 240x135 PNG for Live View, so the whole flow can be seen without a device.

## Tests

```bat
npm test           :: vitest: pairing card, live view polling, key mapping, rebrand check
npm run typecheck  :: tsc, no emit
npm run screenshots:: drives the built app against the mock, writes docs/screenshots
```

`npm run screenshots` and the UI checks need Electron's binary (`node node_modules/electron/install.js`
does it if `npm install` skipped the download).

## Build the installer

```bat
npm run build      :: typecheck, build main + renderer, then electron-builder --win nsis
```

The result is `app/release/Piblo-Setup-<version>.exe`. CI does the same on a Windows runner and uploads
it as the `Piblo-Setup` artifact (`.github/workflows/app.yml`).

**Installing an unsigned build:** Windows SmartScreen shows *"Windows protected your PC"* the first
time. Choose **More info**, then **Run anyway**. The installer is per-user (no admin prompt), creates a
Start menu shortcut, and can start with Windows from Settings inside the app. There is no code signing
certificate yet.

## How it fits together

- `electron/` main process: window, tray, Core discovery, token, pairing notifications, screenshots.
  The token is read from Piblo's own `.env` and never reaches the page.
- `src/` the React UI. All colours, radii and fonts come from `src/styles/tokens.css`, which mirrors
  `design/tokens-a.css` (Concept A) — the same contract the device uses in `src/ui/theme.h`.
- `scripts/mock-core.mjs` a stand-in for Piblo on this PC, with the pairing routes from
  `docs/protocol/DEVICE-PAIRING.md`.
- Internal `MAZ_*` environment names stay as they are: they are what the background service reads from
  its own settings file. They are never shown in the app.
