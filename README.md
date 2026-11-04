# replica-flow

A Claude Code plugin that rebuilds an app's features and flows (never its code, assets, copy or brand), phase by phase, with a check before each next step:

recon → wedge → architect → design → build → backend → test → diff → entrepreneur → brand → launch → deploy

It also adds four modes:
- **Flow mode** (`--flow`) rebuilds one flow of an app, such as Calendly booking, as a module inside your existing app.
- **Pitch mode** (`--pitch`) builds a thin prototype plus a client pitch: preview, demo video, priced scope of work and proposal.
- **Wedge** localizes the plan for the Philippines and Southeast Asia: GCash/Maya, Taglish, payday cutoffs and similar.
- **Deep mode** (`--deep`) adds a probe phase after recon. It uses [REA](https://github.com/morluto/rea) to work out how a feature works from a local copy of the app (Electron/JS, native binaries, .NET, your own captured traffic). A separate subagent reads REA's output and writes a behavioral spec in its own words; `spec_check.py` blocks copied names, strings and code; the build reads only the spec.

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
/replica-flow Obsidian --deep
```

The pack's tools (`sweep.py`, `parity.py`, `contrast.py` and others) need Python 3.8 or newer and use only the standard library.

Deep mode needs REA (Node.js 22.23.4+, 24.22.1+ or 26.12.1+):

```
npm install --global rea-agents
rea setup --client claude_code
```

Restart Claude Code afterwards. JavaScript/Electron and web targets need nothing else; native binaries need Ghidra, IDA, Hopper or Kuna (see REA's docs). Only probe apps you got lawfully, after checking their license terms. Without REA, `--deep` skips the probe and the rest runs as normal.

## Update

```
/plugin marketplace update replica-flow
```

## Credits

- `skills/replica-flow`: Andrew Reyes, MIT (see `LICENSE`).
- Deep mode calls [REA](https://github.com/morluto/rea) by morluto (MIT), which you install separately; none of its code is included.
- `skills/replica-*` (all the others): the Replica pack by Jake Schincariol, MIT (see `skills/LICENSE-replica-skill`), included unchanged.
