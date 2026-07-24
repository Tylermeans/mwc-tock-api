# CLAUDE.md — Midwest Cards Reservation Board

Context for Claude Code / agents picking up this project. Read this first.

## What this is
A customer-facing, DMV-style "now serving" reservation board for the Midwest Cards
shop floor (the bar + kitchen). It shows upcoming Tock reservations on a lobby TV /
kiosk: reservation time, first name, last initial, and status. Tock has no native
public waitlist display, so this project bridges Tock's reservation data to a live
screen.

## The one rule that overrides everything: PRIVACY
This board is shown in public. The ONLY fields that may ever reach the display are:
- `time` (e.g. "6:30 PM")
- `firstName`
- `lastInitial` (single letter)
- `status` ("upcoming" | "seated")

Full last name, email, phone, party size, notes, payment, table — every other Tock
field MUST be discarded server-side, at ingest, before anything is stored or shown.
Redaction happens in the n8n `Redact & Shape` node. The Google Sheet and the board
therefore hold no PII beyond first name + initial.

> Any change that would put additional guest data into the sheet, the /waitlist.json
> feed, or the board is prohibited. If a task appears to require it, STOP and flag it.

## Architecture
```
Tock (Real-time Reservation Webhook)
        |  POST on reservation create / edit / cancel
        v
n8n  -- Ingest chain -----------------------------------------
   Webhook -> Redact & Shape -> Upsert (Google Sheet, matched on reservationId) -> 200
        |
        v
Google Sheet "Waitlist"   (the only datastore; scrubbed rows only)
        |
        v
n8n  -- Serve chain ------------------------------------------
   GET /waitlist.json -> Read Sheet -> Build Board JSON (filter + sort) -> JSON
        |
        v
board/index.html   (polls /waitlist.json every 20s, renders the board)
```
Both chains live in one importable workflow: `n8n/midwest-cards-tock-ingest.n8n.json`.

## Repo layout
- `board/index.html` — the display board. Single file, zero dependencies. Supports
  `?data=<url>` to override the feed URL (used for local dev). For production, set
  `DATA_URL` in-file OR serve it with the query param.
- `n8n/midwest-cards-tock-ingest.n8n.json` — importable n8n workflow (Ingest + Serve).
- `docs/data-contract.md` — /waitlist.json schema + the Google Sheet column schema.
  This is the interface between backend and board; don't change one side alone.
- `docs/tock-reservation-model.md` — the subset of Tock's Reservation Data Model we
  consume, and the partyState -> status mapping.
- `docs/tock-api-access.md` — how to obtain Tock API/webhook access (it's gated) and
  the request email.
- `fixtures/tock-webhook-sample.json` — a realistic raw Tock payload (includes PII we
  deliberately drop, so it doubles as a redaction test).
- `fixtures/waitlist-sample.json` — the scrubbed board feed.
- `dev/dev-server.py` — zero-dependency local server. Serves the board at `/` and a
  live mock `/waitlist.json`. Run: `python3 dev/dev-server.py`.
- `scripts/test-ingest.sh` — curl the ingest + serve endpoints against a running n8n.

## Data contract (summary — full detail in docs/data-contract.md)
`/waitlist.json` returns:
```json
{ "updatedAt": "<ISO8601>",
  "reservations": [
    { "time": "6:30 PM", "firstName": "Casey", "lastInitial": "R", "status": "upcoming" }
  ] }
```
Google Sheet "Waitlist" header row (auto-map matches on header names):
`reservationId | sortKey | timeDisplay | firstName | lastInitial | status | updatedAt`

## Tock facts (full detail in docs/tock-reservation-model.md)
- Access is gated to Premium / Premium Unlimited plans, provisioned by request:
  email api-integration@resy.com from an Account Owner on the Tock Dashboard Team
  page. The reservation API is READ-only (you cannot create/edit reservations).
- Fields we use: `id` (stable dedup key), `dateTime` (24h "HH:MM" in business TZ ->
  convert to 12h), `serviceDateTimestamp` (ms epoch, for sort + today-filter),
  `dinerPatron.firstName`/`lastName` (name shown in Tock; fallback `ownerPatron`),
  `partyState` (enum), `isCancelled`.
- Status mapping: CANCELLED / NO_SHOW / isCancelled -> dropped; LEFT -> dropped;
  SEATED / PARTIALLY_SEATED / ARRIVED / PARTIALLY_ARRIVED -> "seated";
  EXPECTED / default -> "upcoming". "Up next" (the gold hero) is computed by the
  board, not stored.

## Run locally
```
python3 dev/dev-server.py
# open http://localhost:8000/?data=/waitlist.json
```
No build step, no install.

## Deploy
- Board: host `board/index.html` on Vercel / Cloudflare Pages or straight on the
  kiosk. Set `DATA_URL` (in-file) or serve with `?data=<serve-webhook-url>`.
- Workflow: import the JSON into n8n -> attach your Google Sheets credential on both
  Sheets nodes + pick the `Waitlist` tab -> set `SHARED_SECRET` in Redact & Shape and
  `BUSINESS_TZ` in Build Board JSON -> activate -> give the `tock-reservation`
  production URL + `x-tock-token` to Tock; point the board at the `waitlist.json`
  production URL.

## Bridge mode (pilot before Tock is provisioned)
Serve just reads the sheet, so you can type rows into `Waitlist` by hand (fill
firstName / lastInitial / timeDisplay; leave sortKey blank) and the board works with
zero Tock dependency. The webhook later fills the same sheet — no board changes.

## Status
- [x] Board (frontend) — kiosk-ready, brand-styled (Navy #001D48 / Gold #E8B144, Barlow Condensed).
- [x] n8n Ingest + Serve workflow — importable.
- [x] Tock data-model mapping + access path — documented.
- [ ] Attach real Google credential + spreadsheet (manual, per environment).
- [ ] Obtain Tock webhook access (email sent -> awaiting provisioning).
- [ ] Swap the type wordmark in the board for the official Trellis logo asset.

## Backlog / open decisions
- Native Header Auth on the webhook node instead of the in-code token check
  (cleaner 403; secret lives in a credential, not node text).
- Optional daily "clear the sheet" cleanup workflow (the sheet grows; the board
  already filters stale rows out by date, so this is tidiness only).
- Multi-location: Serve filters to one BUSINESS_TZ. If the business group has more
  than one venue, add a location column + filter.
- Refresh mechanism: polling (current, 20s) vs SSE/websockets if instant updates
  are ever needed.
- Logo: board uses a type-wordmark placeholder; swap the official vector before
  large-format / kiosk polish.

## Conventions & guardrails for agents
- Keep the board a single dependency-free HTML file. No frameworks. No localStorage /
  sessionStorage.
- Never commit real secrets. `SHARED_SECRET` in the workflow JSON is a placeholder;
  the real value belongs in an n8n credential / env, not in git.
- Anything touching the production n8n instance or the live board is human-review-
  gated. Propose diffs; don't assume deploy.
- House style: n8n = runtime for scheduled/mechanical automation; Google Sheets =
  persistence (Google Drive-first shop); BLUF in written output; paste-ready deliverables.
- Don't break the data contract on one side only — `docs/data-contract.md` is the
  source of truth for the board <-> backend interface.
