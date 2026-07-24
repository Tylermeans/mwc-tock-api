# Tock Reservation Data Model — the parts we use

Source: Tock's public Reservation Data Model (api.exploretock.com). Below is only the
subset this project consumes. The full model has ~50 fields (pricing, payments,
refunds, feedback, tables) — all intentionally ignored.

## Fields we read (in `Redact & Shape`)
| Tock field             | Type            | How we use it                                                                 |
|------------------------|-----------------|-------------------------------------------------------------------------------|
| `id`                   | uint64          | Stable unique id; our `reservationId` dedup key. (Transferred reservations get a NEW id and count as new.) |
| `dateTime`             | string          | Start time in the business timezone, 24h "HH:MM" (e.g. "16:15"). Converted to "4:15 PM". |
| `serviceDateTimestamp` | uint64          | Start time as ms since epoch (UTC). Used for sorting and the today-filter, no timezone math needed. |
| `dinerPatron`          | Patron          | The patron whose name shows in the Tock Dashboard. We take `firstName` + first char of `lastName`. |
| `ownerPatron`          | Patron          | Fallback for name if `dinerPatron` is absent (e.g. concierge bookings).       |
| `partyState`           | enum PartyState | Mapped to our `status` (table below).                                         |
| `isCancelled`          | bool            | If true -> dropped from the board.                                            |
| `confirmationCode`     | string          | Fallback id if `id` is missing (8 chars; absent for walk-ins).                |
| `walkinId`             | int64           | Fallback id for walk-ins.                                                      |

`Patron` gives us `firstName` and `lastName`. It ALSO carries `email`, `phone`,
`zipCode`, etc. — we never read those.

## partyState -> board status
| Tock partyState                              | Board status | On the board?          |
|----------------------------------------------|--------------|------------------------|
| `EXPECTED` (default after booking)           | `upcoming`   | Yes                    |
| `ARRIVED`, `PARTIALLY_ARRIVED`               | `seated`     | Yes (checked in)       |
| `SEATED`, `PARTIALLY_SEATED`                 | `seated`     | Yes (checked in)       |
| `LEFT` (finished)                            | `left`       | No (filtered in Serve) |
| `NO_SHOW`                                    | dropped      | No                     |
| `CANCELLED` (or `isCancelled: true`)         | `cancelled`  | No (filtered in Serve) |
| deprecated states (AWAITING_RESPONSE, etc.)  | `upcoming`   | Yes (default)          |

"Up next" is not a Tock state — the board computes it as the earliest `upcoming`.

## Access & limits
- Gated to Premium / Premium Unlimited plans; provisioned by request (see
  `tock-api-access.md`).
- The reservation API is **read-only**: you can receive/read reservations and ingest
  guest-profile tags, but you cannot create or modify reservations. Fine for a
  display board; do not design two-way sync around it.
- Payload nesting: Tock may send the reservation as the request body, or wrapped
  under a key. `Redact & Shape` handles `body.reservation || body`. If the real
  webhook differs, adjust that one line — it's the only place the raw payload is read.
