---
name: replica-flow
description: Runs the Replica pack (Jakeschincariol/replica-skill) end to end with gates (recon → wedge → architect → design → build → backend → test → diff → entrepreneur → brand → launch → deploy), plus three modes the pack lacks. Flow mode (`--flow`) rebuilds ONE flow of an app (e.g. Calendly booking) as a module inside an existing app. Pitch mode (`--pitch`) builds a thin prototype and a client pitch (preview, demo video, priced scope of work, proposal). The wedge localizes for the Philippines/SEA. Use for "/replica-flow <app>", "clone/replicate <app>", "copy the <X> flow into my app", "pitch a <product> clone to <client>", "resume replica from <phase>".
metadata:
  author: Andrew Reyes
  version: "2.1.0"
  domain: workflow
  triggers: replica-flow, replica, replicate, clone this app, reverse engineer app, single flow, drop-in module, client pitch, scope of work, wedge, localize for Philippines
  role: orchestrator
  scope: workflow
  output-format: files
  related-skills: replica-recon, replica-architect, replica-design, replica-build, replica-backend, replica-test, replica-diff, replica-entrepreneur, replica-brand, replica-launch, replica-deploy
---

# replica-flow: the Replica pack, end to end, plus flow, pitch and wedge

An add-on to Jake Schincariol's Replica pack (https://github.com/Jakeschincariol/replica-skill, MIT).
The pack does the work, phase by phase. This skill runs it in order with gates, and adds flow mode,
pitch mode and the wedge phase. Clean-room: an app's **features and flows**, never its code, assets,
copy or brand. Every phase enforces that; so does this.

## Before anything: find the pack

The pack ships bundled with this skill (the `replica-flow` plugin), so it is normally already here.
Its skills appear under one of these names. Check the available skills list:
- bundled in this plugin: `replica-flow:replica-recon`, `replica-flow:replica-architect`, ...
- the pack installed on its own: `replica-skill:replica-recon`, ...
- copied into a skills folder: `replica-recon`, `replica-architect`, ...

Use whichever exists. Below, `replica-<phase>` means that skill under the name found. None found →
stop and tell the user to reinstall this plugin, then reload skills:

```
/plugin marketplace add MasterVoodoo/replica-flow
/plugin install replica-flow@replica-flow
```

**Pack tools** (`sweep.py`, `parity.py`, `contrast.py`, ...) live in the pack's folder, not the project.
When bundled, `<pack>` is the folder holding this SKILL.md's parent (the sibling `replica-brand/` sits
next to `replica-flow/`). Otherwise search for `replica-brand/sweep.py` at any depth under
`~/.claude/plugins/cache/`, then `~/.claude/skills/`, then the project's `.claude/skills/`.
The folder holding `replica-brand/` is `<pack>`.

**Python:** use `python3`; if missing (common on Windows), `python`. Standard library only, 3.8+.

## Usage

```
/replica-flow <app name | URL | App Store link>        # full run, phase 1 → 12
/replica-flow Notion                                   # a name is enough
/replica-flow "Notion: pages, blocks, sharing"         # name + slice skips the scope question
/replica-flow --flow "Calendly booking"                # one flow → module in the app in the current dir
/replica-flow --flow "Calendly booking" --into ../my-app
/replica-flow Calendly --pitch --client "Acme Clinic"  # prototype + pitch bundle, stops there
/replica-flow --no-wedge <app>                         # skip the Philippine/SEA phase
/replica-flow --from <phase>                           # resume, e.g. --from build
/replica-flow --only <phase>                           # one phase
/replica-flow <app> --until diff                       # stop after a phase
```

`--from` / `--until` / `--only` work in every mode, on that mode's phase list.

**Input:** a product name (Salesforce, Google Drive, Notion) works as well as a URL. With a name only,
resolve it yourself: web-search its official site, help center/docs, pricing page, changelog, store
listings and public API docs, and fill recon's sources table from those. Don't ask the user for URLs.

**Scope:** big suites are never cloned whole. If no slice was given, propose one in one line (the core
paid loop, e.g. Drive → upload, folders, share links; Salesforce → contacts, accounts, deals pipeline)
plus platform (default: web) and audience (who uses it, which market: it decides whether the wedge runs),
and get a yes before recon goes past scoping. Pass the agreed slice, platform and audience to recon.

Nothing given and no `replica/recon.md` in the project → ask which app, nothing else.

## The full pipeline

Invoke each with the **Skill** tool, in this order. Pass the app name/URL (and any user notes) as `args`
to recon; later phases read `replica/`. After the wedge, every later phase's `args` starts with "honor
replica/wedge.json adopted levers as hard requirements", then the phase's line from the table below.

Gates are minimums. Each phase still produces everything its own SKILL.md lists.

| # | Skill | Reads | Gate before moving on |
|---|---|---|---|
| 1 | `replica-recon` | name/URL + slice, public pages, user's own account | `replica/recon.md` + `replica/features.csv` exist |
| 2 | **wedge** (this skill: follow `wedge.md` in this folder) | recon | `replica/wedge.json` exists; every lever decided, every `adopt` has evidence |
| 3 | `replica-architect` | recon, wedge | `replica/architecture.md` exists |
| 4 | `replica-design` | recon, `replica/screens/` | `tokens.json` + `components.md` exist, `contrast.py` passes, primitives page builds |
| 5 | `replica-build` | recon, architecture, design | core flow builds and runs; `features.csv` `clone` column updated; `replica/build-log.md` |
| 6 | `replica-backend` | architecture | `replica/backend.md` checklist filled; `.env.example` written **and tracked by git** |
| 7 | `replica-test` | recon flows, wedge checks | `replica/bugs.md` has no open S1/S2 |
| 8 | `replica-diff` | `features.csv` | `replica/parity.md` written; must-haves done (the "better than the original" verdict needs entrepreneur, which runs after) |
| 9 | `replica-entrepreneur` | public reviews, wedge | `replica/feedback.md` / `fixes.md` written |
| 10 | `replica-brand` | fixes | `replica/brand.json` written; `sweep.py` clean |
| 11 | `replica-launch` | fixes, brand | `replica/launch/` written; `listing.py` passes |
| 12 | `replica-deploy` | everything | preflight green **and user says go** |

`--no-wedge`, or an audience outside PH/SEA, skips phase 2 (see `wedge.md`).

**Who creates the app:** design's Step 4 builds the primitives in code, so scaffold the app from
`architecture.md`'s stack at the start of phase 4 (then commit). Build adds screens to it.

**`args` per phase** (the pack's defaults assume a funded, multi-user product with accounts ready):

| phase | `args` |
|---|---|
| recon | "slice: <slice>, platform: <platform>, audience: <audience> (already agreed: skip Step 1)" |
| architect | "scope = the slice only. If the user has no accounts/keys for this run, pick a stack that runs locally with zero signups (see Rules)" |
| design | "scaffold the app per architecture.md before Step 4. No screenshots of the original → set roles and scale fresh, don't measure" |
| build | (wedge line only) |
| backend | "only what the slice needs per architecture.md: no signup, OAuth, payments or email it doesn't use" |
| test | "every adopted wedge lever's check is a named test; size/speed budgets are measured on a production build" |
| diff | "layout diff only if replica/screens/ holds screenshots of the original" |

## Flow mode (`--flow "<product> <flow>"`)

Rebuilds **one flow** of the target app as a module inside an existing app, the **host app**
(`--into <path>`, default the current dir). Resolve `--into` against the current dir; if it doesn't
exist there, look one level up and confirm the match with the user. All `replica/` files in flow mode
live **inside the host app**. Output is a module + changes on a branch, not a new app.

The host must be an app: a `package.json` (or the platform's equivalent) and source files. Empty or
missing folder → stop and ask: scaffold a minimal host there (the user's usual stack), run the full
pipeline instead, or point `--into` at another app.

| # | Phase | How it differs from the full pipeline | Gate |
|---|---|---|---|
| 1 | `replica-recon` | Slice = that one flow only, no scope question: trigger, steps, keyboard/mouse input, every state (empty, loading, error, mobile). `features.csv` holds only that flow's rows (~5-15). | `replica/recon.md` + `features.csv` exist, one flow |
| 2 | **host read** (no pack skill: do it yourself) | Read the host app: `package.json`, framework + version, UI kit (`components.json`, Tailwind config, theme), state/data layer, auth, DB schema + access rules (e.g. Supabase migrations, RLS), test setup, folder conventions. Write `replica/host.md`. | `replica/host.md` exists |
| 3 | `replica-architect` | Stack is fixed: the host's. Plan only the module boundary (public API/props), where it goes in the host, and any new tables. Pass `args`: "flow mode, stack fixed, see replica/host.md". | `replica/architecture.md` exists |
| 4 | `replica-design` | No new design system. Map the flow's components onto the host's existing tokens/theme/components. Write only `replica/design/components.md`. | `components.md` exists |
| 5 | `replica-build` | Build the module in the host's folder conventions, one self-contained folder (component, hooks, types, README) behind one import, and one example usage. | host type-checks and builds |
| 6 | `replica-backend` | **Skip** if the flow stores no data. Else: migration + access rules in the host's migration folder, following the host's auth model. | migration applies on a local/dev DB |
| 7 | `replica-test` | Tests run against the host app, in its existing e2e setup (add Playwright only if none). | no open S1/S2 |
| 8 | `replica-diff` | Parity on the flow rows only. | `replica/parity.md`; must-haves done |

**Pass these `args`** so the pack's skills skip their whole-app steps (each skill otherwise does them):

| phase | `args` |
|---|---|
| recon | "flow mode: slice is only <flow>, skip Step 1 scope, features.csv holds only this flow's rows" |
| architect | "flow mode, stack fixed, see replica/host.md: skip Step 1 stack choice; plan module boundary, location, tables only" |
| design | "flow mode: no new design system. Skip tokens.json, tokens.css, the Tailwind mapping, contrast.py and the primitives route. Map components onto the host's existing ones; write only replica/design/components.md" |
| build | "flow mode: skip Step 1 shell (the host has one) and the per-screen commits; build the module + example routes on the current branch" |
| backend | "flow mode: storage for this flow only; no auth, payments or email unless the flow needs them" |
| test | "flow mode: test against the host app; write clone screenshots to replica/flows/<slug>/clone-screens/" |
| diff | "flow mode: parity on this flow's rows; clone screenshots in replica/flows/<slug>/clone-screens/" |

The wedge does not run in flow mode: the host app already made those choices. Entrepreneur, brand,
launch and deploy do not run: the host app has its own.

Flow mode rules:
- **Branch:** if the host is a git repo, create `replica/flow-<slug>` before phase 5. Don't commit; the
  user reviews the diff.
- **Host conventions win** over the pack's defaults (stack, folder layout, naming, tokens). If the host
  can't support the flow without a new dependency or a big refactor, stop after phase 3 and ask.
- **No database in the host** and the flow stores data → use the local zero-signup stack (see Rules).
- **Host bugs are reported, not fixed.** Problems in the host's own code or theme (contrast, fonts,
  audit findings) go in `bugs.md` marked "host", with the fix. Touch only the module, its routes and
  test setup.
- **Not a pixel copy.** Behavior matches the target; the look matches the host.
- **After phase 8**, move the run's files to `replica/flows/<slug>/` so the next `--flow` starts clean and
  each flow keeps its audit trail. Anything the project's code or tests reference (clone screenshots)
  is written to `replica/flows/<slug>/` from the start, so the move breaks nothing.
- Report at the end: module path, the one import, files changed, tests, parity score, branch name.

## Pitch mode (`--pitch --client "<name>"`)

A sales bundle for a prospect, before any contract. No `--client` → ask for the client name, nothing else.
A new app in the current dir. No backend, no real accounts, no keys. Git commits are fine; never push.

| # | Phase | `args` / how it differs | Gate |
|---|---|---|---|
| 1 | `replica-recon` | "slice, platform, audience agreed: skip Step 1. features.csv covers the whole slice (it is all priced)" | recon.md + features.csv |
| 2 | **wedge** | as full; adopted levers become `features.csv` rows (see `wedge.md`) so they get priced | wedge.json |
| 3 | `replica-architect` | "pitch mode: plan the full build (it is what gets priced); mark which milestone the prototype covers; local zero-signup stack" | architecture.md |
| 4 | `replica-design` | as full (scaffold the app here) | as full |
| 5 | `replica-build` | "pitch mode: only the single most valuable must-have flow, end to end, on seed data; other screens stubbed" | core flow builds and runs |
| 6 | `replica-test` (light) | "pitch mode: happy path of the core flow + adopted wedge checks only" | those tests pass |
| 7 | `replica-diff` | "pitch mode: write the full score to replica/parity.md, and a slice score: parity.py on a copy of features.csv with only the core flow's rows" | parity.md written (a low full score is expected: it is what the price covers) |
| 8 | **bundle** | below | pitch.json |

**Bundle.** Client-facing files go in `replica/pitch/client/`; `replica/pitch/pitch.json` is internal.

1. **Sizes.** Add a `size` column to `features.csv`: effort per feature, not recon's whole-app size.
   S = small UI change (~4 h), M = one screen or rule (~12 h), L = a subsystem (~32 h), XL = an
   integration (~80 h); hours come from the rate card. **Hard stop:** show sizes + rate card, the user
   approves or edits. Prices go to a client, so no silent guesses.
2. **Scope of work.** Rate card: `replica/rate_card.json` if the project has one, else `rate_card.json`
   in this skill's folder. Null `hourly_rate` → ask, and offer to save to the project copy. Run
   `python3 <this folder>/sow.py replica/features.csv --rates <card> --client "<name>" --all > replica/pitch/client/sow.md`.
   `--all` prices the prototype's rows too: they run on seed data and still need the production build.
   The card's `fixed` items (setup, QA, management) land in phase 1.
3. **Preview.** Ask first. Vercel skill or CLI if available (preview, not prod), else the user's host,
   else local only: record the run command.
4. **Demo video.** Ask first (it is slow). Yes and `hyperframes` installed (run a house-style video skill
   first if there is one): 60-90 s on real Playwright captures, beats: problem → the flow working → what
   the full build adds → price tiers → `client/demo.mp4`. Otherwise 4-6 screenshots → `client/screens/`.
5. **Proposal.** Self-contained `client/proposal.html`: one-line pitch, video or screenshots, preview
   link, the **slice** parity score, the Good/Better/Best table, adopted wedge levers as "built for
   <market>", next step. Publish it (e.g. as a private Artifact) only if the user asks: it holds prices.
6. **Clean-room sweep, last.** Over the app: `python3 <pack>/replica-brand/sweep.py . --avoid "<target>"`;
   over the client files: `python3 <pack>/replica-brand/sweep.py replica/pitch/client --include-replica --avoid "<target>"`.
   Both clean before anything leaves the machine. The prototype uses a neutral working name.
7. **`replica/pitch/pitch.json`:**
   ```json
   {"client": "Acme Clinic", "target": "Calendly", "slice": "guest booking", "working_name": "Ngiti Book",
    "preview": {"url": null, "local": "npm run build && npm run start"},
    "video": null, "screens": ["client/screens/S01.png"], "proposal": "client/proposal.html",
    "parity": {"slice": 92.0, "full": 48.0},
    "totals": {"Good": {"PHP": 0, "USD": 0, "weeks": 0}, "Better": {}, "Best": {}}}
   ```

Client signs → `/replica-flow --from build` continues the same folder: build finishes the stubbed screens,
then backend, test, diff and the rest. Nothing is thrown away. After the project, update the card's `hours`
with real numbers so the next quote is closer.

## Rules

- **Run each phase fully per its own SKILL.md**, then check its gate, then invoke the next. Don't summarize
  a phase instead of running it.
- **Gate fails → stop, report what's missing, fix within that phase** (e.g. test finds S1 bugs → fix, re-test)
  before moving on. If unfixable, stop and tell the user which phase to resume with `--from`.
- **Hard stops: wait for the user, never work around:**
  - recon needs the user to click through their own account (if they have one);
  - backend needs the user to create accounts and put keys in `.env.local`. Claude never signs up, types
    passwords, cards or live keys;
  - brand: the user picks the name;
  - secrets the app itself needs (owner password, session secret): Claude writes a script that generates
    them into `.env.local`; the user runs it;
  - pitch: the user approves sizes and rates, and says yes before any deploy, video or publish;
  - deploy: the user buys the domain, does DNS/account steps, and gives the explicit go to ship.
  At each, say what's needed and that they can continue with `/replica-flow --from <phase>`.
- **Order is fixed.** Skipping a phase is fine only on `--from`/`--only`, and only if its input files exist.
- **No screenshots of the original** in `replica/screens/` (public sources only, no account) changes
  three phases: design sets token roles and scale fresh instead of measuring; diff skips `imgdiff.py` and
  scores feature parity only; diff's behaviour walk compares against the public docs. Say so in
  `parity.md`. Never scrape the original's screens to fill the gap.
- **No accounts or keys** for this run (or a host without a database): a local zero-signup stack.
  Storage the runtime already has (e.g. Node 22+ `node:sqlite`) behind one `db` file; a single owner
  account via a generated password hash in `.env.local` if login is needed; no payments or email. Write
  the ceiling (e.g. no persistence on serverless) in `backend.md`. A hosted service with keys is the user's call.
- **`.env.example` must be tracked.** Next.js's default `.gitignore` has `.env*`; add `!.env.example`.
- After each phase, one line to the user: phase done, file(s) written, next phase.
