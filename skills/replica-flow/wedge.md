# Wedge phase: Philippine / SEA localization levers

Runs between recon and architect. Turns "a copy of X" into "X, built for the Philippine market".
Writes `replica/wedge.json` (the decisions) and `replica/wedge.md` (the same, readable, with sources),
and adds rows to `replica/features.csv` (below).

## When it runs

Only when the agreed audience is users in the Philippines (or SEA). If the audience is elsewhere,
write `replica/wedge.json` as `{"skipped": "<one-line reason>"}` and move on.

## The levers

Decide every lever: `adopt`, `skip` or `defer`. Each decision needs a one-line reason.
- **`adopt` needs evidence**: a recon feature it touches plus a source (a PH review, a local competitor,
  a regulation, a public stat). No evidence → `defer`, not `adopt`. A checklist applied blindly is scope bloat.
- **`skip`**: the slice has nothing the lever touches (no money → no payments lever).
- **`defer`**: it could matter, but there is no evidence yet, or it needs a paid provider the run doesn't have.

| id | lever | typical adopt | check the test phase runs |
|---|---|---|---|
| payments | Local payments | PayMongo (cards, GCash, Maya, GrabPay) as primary; Stripe only if the target sells abroad. Only if the slice takes money. | sandbox checkout passes for each adopted method |
| identity | Mobile-number login | SMS OTP sign-in next to email, PH numbers (+63) validated | OTP sign-in flow passes |
| language | Taglish / Filipino UI | English base with a Filipino string file; plain, friendly Taglish microcopy where the audience is consumer | no hard-coded strings; Filipino locale renders all screens |
| connectivity | Slow / patchy networks | offline-first for the core flow (local store + sync queue), or at least optimistic UI + retry that never double-submits | core flow passes with 3G throttling and one offline toggle |
| device | Low-end Android budget | first-load JS < 300 KB gzipped (lower for public pages); LCP < 4 s in a lab run (Lighthouse or Playwright, 3G throttling + 4x CPU slowdown); APK size budget for mobile | budget check on a **production build** (dev builds are much larger) |
| privacy | Data Privacy Act (RA 10173) | either collect nothing personal, or: consent record, privacy notice (English + Filipino), data-subject requests (access, delete), NPC registration note if processing sensitive data | if personal data is collected: consent recorded before it is saved and a delete request works; if not: a test proves nothing personal is stored |
| notifications | Local channels | SMS (e.g. Semaphore) and/or Viber for time-critical messages; email second | notification sent through each adopted channel in sandbox (stubbed if no provider) |

**Your own levers.** Before deciding, spend a few searches on local gaps the table misses: PH reviews of
the target, local competitors, PH forums. A local gap with a source becomes a lever in the same shape
(e.g. "seller-links: quick-add GCash, Messenger, Shopee buttons").

## Effects on `features.csv`

- **Every `adopt` adds a row**: `feature` = the lever's main constraint in plain words, `area` = `wedge`,
  `priority` = must (or should, with the reason), `original` = `no`, `clone` = `no`, `notes` = `wedge: <id>`.
  Rows with `original` = `no` are built, tested and priced, but not counted in parity (parity only
  measures what the original has).
- **A feature an adopted lever rules out** (e.g. per-visitor analytics under "collect nothing personal"):
  set its `clone` to `skip`, `notes` = `wedge: <id>`. Parity leaves skips out, so the choice doesn't
  count against the clone.

## `replica/wedge.json`

```json
{
  "market": "PH",
  "levers": [
    {
      "id": "payments",
      "decision": "adopt",
      "reason": "Booking takes deposits; local users pay with GCash",
      "evidence": ["features.csv: Take payment at booking", "https://... (review asking for GCash)"],
      "constraints": ["PayMongo primary: GCash, Maya, cards", "payment provider behind one adapter"],
      "check": "sandbox checkout passes for GCash and card"
    },
    { "id": "identity", "decision": "skip", "reason": "Guests book without an account" },
    { "id": "language", "decision": "defer", "reason": "No local reviews ask for Filipino; revisit after entrepreneur" }
  ]
}
```

`skip` and `defer` need only `id`, `decision` and `reason`.

## How later phases use it

Every phase after it gets "honor replica/wedge.json adopted levers as hard requirements" in `args`.
- **architect**: constraints shape the stack and schema (payment adapter, consent table, sync queue).
  Check that budgets are reachable with the chosen stack (a framework's own JS can exceed a tight budget).
- **design**: language and device levers (string files, bundle budget, light assets).
- **build / backend**: implement the adopted levers.
- **test**: every adopted lever's `check` becomes a named test; budgets measured on a production build.
- **pitch bundle**: the lever rows are priced like any feature, and the proposal lists them as "built for <market>".
- **entrepreneur**: adopted levers are the first draft of the positioning angle; reviews confirm or kill
  them, and deferred levers get a second look.
- **launch**: the privacy lever adds the privacy notice and NPC checklist to the launch files.
