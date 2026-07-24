# Data Contract

The interface between the backend (n8n) and the board. Change both sides together.

## 1. Board feed — `GET /waitlist.json`
Returned by the n8n **Serve** chain. Response body:

```json
{
  "updatedAt": "2026-07-24T17:32:00-04:00",
  "reservations": [
    { "time": "5:30 PM", "firstName": "Marcus", "lastInitial": "T", "status": "seated"   },
    { "time": "6:00 PM", "firstName": "Devon",  "lastInitial": "R", "status": "upcoming" }
  ]
}
```

| Field                        | Type   | Notes                                                       |
|------------------------------|--------|-------------------------------------------------------------|
| `updatedAt`                  | string | ISO 8601. Optional; the board falls back to its own clock.  |
| `reservations[]`             | array  | Sorted ascending by time by the backend.                    |
| `reservations[].time`        | string | Display string, e.g. "6:30 PM".                             |
| `reservations[].firstName`   | string | First name only.                                            |
| `reservations[].lastInitial` | string | Single letter, no period.                                   |
| `reservations[].status`      | string | `"upcoming"` or `"seated"` only.                            |

Response headers set by Serve: `Access-Control-Allow-Origin: *`, `Cache-Control: no-store`.

**Never add fields.** The board is public; extra fields = PII leak risk.
"Up next" (the gold hero) is derived by the board (earliest `upcoming`), not sent.

## 2. Datastore — Google Sheet tab `Waitlist`
Written by the **Ingest** chain (`appendOrUpdate`, matched on `reservationId`), read
by the **Serve** chain. Header row (auto-map matches on these exact names):

| Column          | Meaning                                                              |
|-----------------|---------------------------------------------------------------------|
| `reservationId` | Tock `id` (stable dedup key). Manual/walk-in rows: any unique value. |
| `sortKey`       | ms since epoch (Tock `serviceDateTimestamp`). Sort + today-filter. Blank for manual rows -> sorts by `timeDisplay`. |
| `timeDisplay`   | "6:30 PM".                                                          |
| `firstName`     | First name.                                                        |
| `lastInitial`   | Single letter.                                                     |
| `status`        | `upcoming` / `seated` / `cancelled` / `left` (last two filtered out by Serve). |
| `updatedAt`     | ISO 8601 write time.                                               |

The sheet holds **no** last name, email, phone, party size, notes, or payment. That
is the whole point — the scrubbed row is the only data at rest.
