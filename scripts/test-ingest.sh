#!/usr/bin/env bash
# Fire the sample Tock payload at the ingest webhook, then read the served feed.
#
#   N8N=https://your-n8n TOKEN=your-secret MODE=test ./scripts/test-ingest.sh
#
# MODE=test  -> hits /webhook-test/... (open the workflow and click "Listen for test event" first)
# MODE=prod  -> hits /webhook/...      (workflow must be Active)
set -eu

N8N="${N8N:-https://YOUR-N8N-HOST}"
MODE="${MODE:-test}"
TOKEN="${TOKEN:-CHANGE_ME_TO_A_LONG_RANDOM_STRING}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"

if [ "$MODE" = "prod" ]; then BASE="$N8N/webhook"; else BASE="$N8N/webhook-test"; fi

echo "==> POST $BASE/tock-reservation"
curl -sS -X POST "$BASE/tock-reservation" \
  -H "Content-Type: application/json" \
  -H "x-tock-token: $TOKEN" \
  --data @"$HERE/fixtures/tock-webhook-sample.json"
echo; echo

echo "==> GET $BASE/waitlist.json"
curl -sS "$BASE/waitlist.json"
echo
