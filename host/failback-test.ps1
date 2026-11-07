# Forced failback test (run on the Core PC after the cloud key is added to host\.env):
#   powershell -File host\failback-test.ps1
# Stops the local llama for one turn, shows which brain answered, always restarts llama.
$ErrorActionPreference = 'Continue'
$envFile = Join-Path $PSScriptRoot '.env'
$tok = ((Get-Content $envFile | Where-Object { $_ -match '^MAZ_TOKEN=' }) -split '=', 2)[1].Trim()
$h = @{ Authorization = "Bearer $tok" }
$base = 'http://127.0.0.1:8787'
try {
    Stop-ScheduledTask -TaskName nod-llama
    Get-Process llama-server -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep 2
    $sid = (Invoke-RestMethod -Method Post -Headers $h "$base/session/start").session_id
    $body = @{ session_id = $sid; text = 'Say hello in five words.'; route = 'auto' } | ConvertTo-Json
    $t = Get-Date
    $r = Invoke-RestMethod -Method Post -Headers $h -ContentType 'application/json' -Body $body "$base/turn/text"
    "provider=$($r.provider) llm_ms=$($r.timings.llm_ms) wall_ms=$([int]((Get-Date) - $t).TotalMilliseconds) reply=$($r.reply)"
    if ($r.provider -notmatch 'groq|cloud|openrouter|mazlatest') { 'FAILBACK DID NOT REACH A CLOUD BRAIN (key missing or stage skipped)' }
} finally {
    Start-ScheduledTask -TaskName nod-llama
    'nod-llama restarted'
}
