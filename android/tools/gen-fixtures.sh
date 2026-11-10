#!/usr/bin/env bash
# Regenerates android/app/src/test/resources/fixtures from a REAL running Core (host/mazhost).
# Usage: start Core (see android/README.md "Run Core locally"), then
#   CORE=http://127.0.0.1:18787 TOKEN=<token> bash android/tools/gen-fixtures.sh
set -euo pipefail
CORE=${CORE:-http://127.0.0.1:18787}
TOKEN=${TOKEN:?set TOKEN to the Core token}
OUT="$(dirname "$0")/../app/src/test/resources/fixtures"
mkdir -p "$OUT"
H=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Piblo-Client: android/fixtures")
get()  { curl -s "${H[@]}" "$CORE$1" > "$OUT/$2.json"; }
post() { curl -s "${H[@]}" -X POST "$CORE$1" -d "$2" > "$OUT/$3.json"; }
j()    { sed -E "s/.*\"id\":\"([^\"]+)\".*/\1/"; }

get /buddy/summary summary_idle
get "/buddy/events?since=0" events_empty

REQ=$(curl -s "${H[@]}" -X POST "$CORE/buddy/request" -d '{"tool":"Bash","summary":"rm -rf build/ && npm run build","project":"piblo"}')
echo "$REQ" > "$OUT/request_created.json"
RID=$(echo "$REQ" | j)
get /buddy/summary summary_pending

post /buddy/event '{"kind":"done","text":"Build finished: 0 errors","source":"claude"}' event_posted
post /buddy/alert '{"source":"ci","kind":"sla","title":"SLA breach: ticket #123","body":"Customer waiting 4h","priority":"urgent","actions":["ack","snooze"]}' alert_posted
post /buddy/alert '{"source":"phone","kind":"info","title":"Find my phone","body":"find_phone","priority":"urgent","actions":["ack"]}' alert_info_posted
get "/buddy/events?since=0" events_mixed
AID=$(cat "$OUT/alert_posted.json" | sed -E 's/.*"id":"(al-[a-f0-9]+)".*/\1/')
curl -s "${H[@]}" -X POST "$CORE/buddy/alert/$AID/ack" -d '' > "$OUT/alert_ack.json"
post /buddy/alert '{"source":"ci","kind":"reminder","title":"Stand-up","body":"","priority":"normal","actions":["ack","snooze"]}' alert_posted_snoozable
AID3=$(sed -E 's/.*"id":"(al-[a-f0-9]+)".*/\1/' "$OUT/alert_posted_snoozable.json")
curl -s "${H[@]}" -X POST "$CORE/buddy/alert/$AID3/snooze" -d '{"minutes":10}' > "$OUT/alert_snooze.json"
AID2=$(sed -E 's/.*"id":"(al-[a-f0-9]+)".*/\1/' "$OUT/alert_info_posted.json")
curl -s "${H[@]}" -X POST "$CORE/buddy/alert/$AID2/snooze" -d '{"minutes":10}' > "$OUT/alert_snooze_not_offered.json"
post /buddy/decide "{\"id\":\"$RID\",\"decision\":\"allow\"}" decide_allow
post /buddy/decide '{"id":"nope","decision":"deny"}' decide_not_found
curl -s -H "Content-Type: application/json" "$CORE/buddy/summary" > "$OUT/error_401.json"
CODE=$(curl -s "${H[@]}" -X POST "$CORE/pair/start" -d '' | sed -E 's/.*"code":"([^"]+)".*/\1/')
curl -s -H "Content-Type: application/json" -X POST "$CORE/pair/claim" -d "{\"code\":\"$CODE\"}" > "$OUT/pair_claim_ok.json"
curl -s -H "Content-Type: application/json" -X POST "$CORE/pair/claim" -d '{"code":"WRONG123"}' > "$OUT/pair_claim_bad.json"
# the token in pair_claim_ok is the throwaway fixture token, not a real credential
echo "fixtures written to $OUT"
