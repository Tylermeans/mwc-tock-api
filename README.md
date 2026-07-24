# Midwest Cards Reservation Board

A DMV-style "now serving" board for the shop floor. It shows upcoming Tock
reservations on a lobby TV — time, first name, last initial — and nothing else.
Built to run on a kiosk with a simple JSON feed behind it.

## Quick start (local, no install)
```bash
python3 dev/dev-server.py
# open http://localhost:8000/?data=/waitlist.json
```
That serves the board plus a live mock feed so you can see it working immediately.

## How it fits together
```
Tock webhook -> n8n (redact) -> Google Sheet -> n8n (/waitlist.json) -> board
```
- Frontend: `board/index.html` (single file, no dependencies).
- Backend: `n8n/midwest-cards-tock-ingest.n8n.json` (import into n8n).
- The board only ever receives first name + last initial + time + status. All other
  guest data is dropped server-side at ingest. See `CLAUDE.md`.

## Set it up for real
1. **Google Sheet** — create a tab named `Waitlist` with this header row:
   `reservationId | sortKey | timeDisplay | firstName | lastInitial | status | updatedAt`
2. **Import** `n8n/midwest-cards-tock-ingest.n8n.json` into n8n.
3. On both Google Sheets nodes, attach your credential and pick the spreadsheet + `Waitlist` tab.
4. In `Redact & Shape`, set `SHARED_SECRET` to a long random string. In `Build Board JSON`, set `BUSINESS_TZ`.
5. Activate. Copy the two production webhook URLs:
   - `.../webhook/tock-reservation` -> give to Tock (with header `x-tock-token: <secret>`)
   - `.../webhook/waitlist.json` -> the board's data feed
6. Deploy `board/index.html` and point it at the feed:
   either set `DATA_URL` in the file, or load it as `?data=<feed-url>`.

## Test end-to-end
```bash
N8N=https://your-n8n TOKEN=your-secret ./scripts/test-ingest.sh
```

## Pilot before Tock access lands
The serve step just reads the sheet, so type reservations into `Waitlist` by hand
(firstName / lastInitial / timeDisplay; leave sortKey blank) and the board works with
no Tock dependency. The webhook fills the same sheet later.

## Getting Tock API access
Tock's reservation API/webhook is gated (Premium plans, request-only). See
`docs/tock-api-access.md` for the steps and the request email.
