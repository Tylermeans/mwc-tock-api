# Getting Tock API / Webhook Access

Tock does not have a self-serve developer API. Data API + webhook access is gated to
**Premium / Premium Unlimited** plans and provisioned by request.

## Steps
1. Confirm your Tock plan tier is Premium or Premium Unlimited.
2. Identify an **Account Owner** on your Tock Dashboard Team page — the request must
   come from an Account Owner's email address.
3. Email **api-integration@resy.com** requesting:
   - an **API key**, and
   - the **Real-time Reservation Webhook** (reservation create/edit/cancel events).
4. Provide, for the webhook:
   - desired webhook(s): reservations
   - the endpoint URL (your n8n `.../webhook/tock-reservation` production URL)
   - the auth header (preferred format has no spaces/special characters, e.g.
     `x-tock-token` with a long random value — this must match `SHARED_SECRET` in the
     `Redact & Shape` node)
5. Also ask for the current **Reservation Data Model** and **Guest Data Model** docs
   so you can confirm field names against `Redact & Shape`.

## Request email (template)
Subject: API key + real-time reservation webhook request — Midwest Cards

```
Hi Tock API team,

I'm writing from Midwest Cards to request API access for our Tock account. We're
building an internal, customer-facing reservation display and need read access to our
reservation data.

Please provision the following for our business group:

1. API key — for the Midwest Cards Tock account.
2. Real-time Reservation Webhook — reservation create / edit / cancel events for our
   location(s).

Webhook setup details:
- Desired webhook: reservations
- Endpoint URL: https://[our-n8n]/webhook/tock-reservation
- Authorization header: we will supply a token header on setup (no spaces or special
  characters)

Could you also share the current Reservation Data Model and Guest Data Model reference
docs so we can confirm available fields?

This request is being sent from an Account Owner listed on our Tock Dashboard Team
page. Please let me know if you need anything further, including confirmation of our
current plan tier.

Thanks,
[Name]
[Title], Midwest Cards
[Phone]
```

Note: reservation data is read-only via the API (see tock-reservation-model.md).
