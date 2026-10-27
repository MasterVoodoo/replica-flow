# replica-flow

A Claude Code plugin that rebuilds an app's features and flows (never its code, assets, copy or brand), phase by phase, with a check before each next step:

recon → wedge → architect → design → build → backend → test → diff → entrepreneur → brand → launch → deploy

It also adds three modes:
- **Flow mode** (`--flow`) rebuilds one flow of an app, such as Calendly booking, as a module inside your existing app.
- **Pitch mode** (`--pitch`) builds a thin prototype plus a client pitch: preview, demo video, priced scope of work and proposal.
- **Wedge** localizes the plan for the Philippines and Southeast Asia: GCash/Maya, Taglish, payday cutoffs and similar.

The [Replica pack](https://github.com/Jakeschincariol/replica-skill) by Jake Schincariol is bundled, so one install gives you everything.

## Install

In Claude Code:

```
/plugin marketplace add MasterVoodoo/replica-flow
/plugin install replica-flow@replica-flow
```

Then restart Claude Code or run `/reload-plugins`.

## Use

```
/replica-flow Notion
/replica-flow "Notion: pages, blocks, sharing"
/replica-flow --flow "Calendly booking" --into ../my-app
/replica-flow Calendly --pitch --client "Acme Clinic"
/replica-flow --from build
```

The pack's tools (`sweep.py`, `parity.py`, `contrast.py` and others) need Python 3.8 or newer and use only the standard library.

## Update

```
/plugin marketplace update replica-flow
```

## Credits

- `skills/replica-flow`: Andrew Reyes, MIT (see `LICENSE`).
- `skills/replica-*` (all the others): the Replica pack by Jake Schincariol, MIT (see `skills/LICENSE-replica-skill`), included unchanged.
