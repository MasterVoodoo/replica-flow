#!/usr/bin/env python3
"""Priced scope of work from replica/features.csv. Standard library only.

    python3 sow.py replica/features.csv --rates rate_card.json --client "Acme" > sow.md
    python3 sow.py replica/features.csv --rates rate_card.json --all      # pitch: price prototype rows too
    python3 sow.py --selftest

features.csv needs a `size` column (S, M, L, XL: effort per feature, see rate_card.json `hours`).
Rows with clone=skip are never priced. Rows with clone=yes/done are left out (already built), unless
--all: in a pitch the prototype runs on seed data, so its rows still need the production build.
Phase 1 = must + the rate card's `fixed` items (setup, QA, ...), Phase 2 = should, Phase 3 = could.
Tiers are cumulative: Good = phase 1, Better = 1+2, Best = 1+2+3.
Each currency is a separate price list, not a conversion.
"""

import argparse
import csv
import io
import json
import math
import sys

PHASES = [("must", "Phase 1: core (must)"), ("should", "Phase 2: should"), ("could", "Phase 3: could")]
TIERS = [("Good", 1), ("Better", 2), ("Best", 3)]
PRIORITY = {"p0": "must", "p1": "should", "p2": "could"}


def load_rows(fh, include_built=False):
    rows = []
    for i, raw in enumerate(csv.DictReader(fh), start=2):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
        clone = r.get("clone", "").lower()
        if not r.get("feature") or clone == "skip" or (clone in ("yes", "done") and not include_built):
            continue
        r["priority"] = PRIORITY.get(r.get("priority", "").lower(), r.get("priority", "").lower())
        if r["priority"] not in ("must", "should", "could"):
            sys.exit("row %d: priority must be must/should/could, got %r" % (i, r["priority"]))
        if not r.get("size"):
            sys.exit("row %d (%s): no size. Fill the size column with S/M/L/XL" % (i, r["feature"]))
        rows.append(r)
    return rows


def price(rows, card):
    missing = [c for c, v in card["hourly_rate"].items() if not v]
    if missing:
        sys.exit("rate card has no hourly rate for %s. Fill it in first." % ", ".join(missing))
    buffer = 1 + card.get("contingency", 0)
    out = []
    for n, (key, title) in enumerate(PHASES):
        items = [(r["feature"], r.get("area") or "-", r["size"].upper()) for r in rows if r["priority"] == key]
        hours = 0
        for feature, _, size in items:
            if size not in card["hours"]:
                sys.exit("%s: size %r not in rate card hours %s" % (feature, size, list(card["hours"])))
            hours += card["hours"][size]
        if n == 0:
            for f in card.get("fixed", []):
                items.append((f["item"], "fixed", "%dh" % f["hours"]))
                hours += f["hours"]
        out.append({"title": title, "items": items, "hours": math.ceil(hours * buffer)})
    return out


def weeks(hours, card):
    w = math.ceil(hours / card["team_hours_per_week"]) if hours else 0
    return "~%d week%s" % (w, "" if w == 1 else "s")


def render(phases, card, client):
    cur = list(card["hourly_rate"])
    cost = lambda h: {c: h * card["hourly_rate"][c] for c in cur}
    cells = lambda d: " | ".join("%s %s" % (c, format(round(d[c]), ",")) for c in cur)
    lines = ["# Scope of work%s" % (" for " + client if client else ""), "",
             "Estimates include a %d%% contingency. Team capacity: %d hours/week. "
             "Prices are listed per currency; they are separate price lists, not a conversion." %
             (card.get("contingency", 0) * 100, card["team_hours_per_week"]), ""]
    for p in phases:
        lines += ["## %s" % p["title"], "", "%d h, %s, %s" % (p["hours"], weeks(p["hours"], card), cells(cost(p["hours"])).replace(" | ", " or ")), ""]
        lines += ["- %s (%s, %s)" % i for i in p["items"]] or ["- nothing"]
        lines.append("")
    lines += ["## Options", "", "| tier | includes | time | %s |" % " | ".join(cur), "|---|---|---|%s" % "---|" * len(cur)]
    for name, n in TIERS:
        h = sum(p["hours"] for p in phases[:n])
        lines.append("| %s | %s | %s | %s |" % (name, "phase 1" if n == 1 else "phases 1-%d" % n, weeks(h, card), cells(cost(h))))
    return "\n".join(lines) + "\n"


def selftest():
    csv_text = ("feature,area,priority,original,clone,notes,size\n"
                "Book a slot,booking,must,yes,no,,M\n"
                "Login,auth,must,yes,yes,,S\n"           # built: left out unless --all
                "Reminders,notify,should,yes,partial,,S\n"
                "Marketplace,apps,could,yes,skip,,XL\n")  # skip: never priced
    card = {"hours": {"S": 4, "M": 12, "L": 32, "XL": 80}, "hourly_rate": {"PHP": 1000, "USD": 20},
            "team_hours_per_week": 10, "contingency": 0.5, "fixed": [{"item": "Setup", "hours": 2}]}
    phases = price(load_rows(io.StringIO(csv_text)), card)
    assert [p["hours"] for p in phases] == [21, 6, 0], phases        # (12 + 2 fixed) * 1.5, 4 * 1.5
    md = render(phases, card, "Acme")
    assert "| Better | phases 1-2 | ~3 weeks | PHP 27,000 | USD 540 |" in md, md
    assert "| Good | phase 1 | ~3 weeks |" in md and "~1 week," in md, md
    assert [p["hours"] for p in price(load_rows(io.StringIO(csv_text), True), card)] == [27, 6, 0]
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("features", nargs="?")
    ap.add_argument("--rates")
    ap.add_argument("--client", default="")
    ap.add_argument("--all", action="store_true", help="also price rows already marked built (pitch prototypes)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        if not (a.features and a.rates):
            ap.error("features.csv and --rates are required")
        with open(a.rates, encoding="utf-8") as fh:
            card = json.load(fh)
        with open(a.features, newline="", encoding="utf-8-sig") as fh:
            sys.stdout.write(render(price(load_rows(fh, a.all), card), card, a.client))
