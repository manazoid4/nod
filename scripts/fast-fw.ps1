# Build main's firmware on this PC and stage it for the Cardputer's U update, without waiting for CI.
# Run on MAZPC:  powershell -File scripts\fast-fw.ps1
# Uses its own worktree so Core's checkout is never touched. stage_fw.py still refuses any bin
# that is not origin/main HEAD, so this is as safe as the CI path, just ~10x quicker when warm.
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$wt   = Join-Path $env:USERPROFILE 'piblo-fw'
$pio  = (Get-Command pio -ErrorAction SilentlyContinue).Source
if (-not $pio) { throw 'pio not found on PATH: install PlatformIO or add pio to PATH' }
$py   = Join-Path $repo 'host\.venv\Scripts\python.exe'

$t = Get-Date
git -C $repo fetch -q origin main
if (-not (Test-Path $wt)) { git -C $repo worktree add -q --detach $wt origin/main }
git -C $wt checkout -q --detach origin/main
Push-Location $wt
try {
    & $pio run -e cardputer-adv
    if ($LASTEXITCODE -ne 0) { throw "firmware build failed" }
    & $py scripts\stage_fw.py --bin .pio\build\cardputer-adv\firmware.bin (Join-Path $repo 'host\fw')
    if ($LASTEXITCODE -ne 0) { throw "staging refused" }
} finally { Pop-Location }
"done in {0:n0} s" -f ((Get-Date) - $t).TotalSeconds
