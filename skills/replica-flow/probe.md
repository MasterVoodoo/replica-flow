# Probe phase (`--deep`): how a feature works, without its code reaching the build

Recon sees what an app does from the outside. Some features can't be inferred that way: an offline
sync scheme, a file or export format, a local search index, a pricing or scheduling rule, an
Electron app's IPC between windows. The probe answers "how does it actually work?" with REA
(`morluto/rea`, MCP server `rea`, skill `reverse-engineer-anything`), and hands the build only a
**behavioral spec**. The build never sees the target's code.

This is the classic clean-room split: one team reads the original and writes a functional spec,
a checker removes anything copied, and a second team builds only from that spec.

## When it runs

Only with `--deep` (or `--only probe` / `--from probe`). Runs right after recon, in every mode
(full, flow, pitch). Without `--deep` nothing here happens and the pipeline is unchanged.

## Step 0: REA available?

Look for tools named `mcp__rea__*` in the available tools, or run `rea --version`.
- Neither → skip the phase. Tell the user once: `npm install --global rea-agents` then
  `rea setup --client claude_code`, restart Claude Code, resume with `/replica-flow --from probe`.
- CLI only (MCP not loaded in this session) → the probe subagent uses the `rea` CLI with `--format json`.
- Native binaries need an engine (Ghidra, IDA, Hopper, Kuna). JavaScript/Electron/ASAR and web
  analysis need none. If a target needs a missing engine, say which one and probe what you can.

## Step 1: pick the targets (hard stop)

From `replica/recon.md` and `features.csv`, list the features whose **mechanism** is unknown and
matters to the build. Pure UI is never probed; recon already covers it. For each one, name the
**artifact** to inspect. It must be a file on this machine: an installed app folder, an `.asar`, an
`.exe`/`.app`/`.dll`, an `.apk`, a downloaded installer, or a HAR capture of the user's own session.

Write `replica/probe-targets.md`:

| feature | question | artifact (local path) | why it can't be inferred from the UI |
|---|---|---|---|

Then ask the user to confirm, **in one message, all of**:
1. they got each artifact lawfully (installed it, own a license, or it's their own capture);
2. they've checked the target's license terms (EULA). Many forbid reverse engineering; some
   jurisdictions still allow it for interoperability. That is the user's call, not Claude's;
3. the scope is the listed questions only.

No confirmation → skip the phase and continue the pipeline. Never probe:
- anything the user didn't confirm, or anything that isn't a local file;
- with the aim of getting around license checks, copy protection, DRM or anti-tamper;
- to pull out keys, credentials, tokens, other people's data or paid content;
- a live service beyond the user's own captured traffic. No replaying requests at someone else's
  servers, no fuzzing or scanning them.

## Step 2: the probe subagent (the dirty room)

Run the probe in **one subagent per target** (Agent tool, general-purpose). The main thread never
reads REA output itself. That boundary is the firewall. Brief each subagent with:

- invoke the `reverse-engineer-anything` skill first and follow it;
- the artifact path, the question from `probe-targets.md`, and the scope limits above;
- put everything raw (REA evidence JSON, decompiled code, strings, HAR captures, notes) in
  `replica/.probe/<feature-slug>/`;
- write the clean spec to `replica/spec/<feature-slug>.md` in the format below, **in your own words**:
  - no code, pseudocode that mirrors the original's structure, or decompiled snippets;
  - no function, class, variable, file or key names taken from the target;
  - no strings, messages or copy from the target;
  - public standards keep their names (SQLite, JWT, AES-GCM, HTTP header names, MIME types);
  - say what the evidence does **not** cover. REA reports limits; carry them over;
- reply with the spec path and one line per open question, nothing else. No excerpts.

Spec format (`replica/spec/<feature-slug>.md`):

```markdown
# <feature>: behavioral spec
Question: <from probe-targets.md>
Confidence: high | medium | low, plus one line why

## Behavior
Inputs, outputs, states and transitions, in plain language or a table.

## Data
Shapes and formats as tables (field, type, meaning, constraints), named by meaning, not the
target's names. Standards named as such.

## Rules and edge cases
Ordering, limits, conflict handling, error cases, timing.

## Not covered
What the evidence couldn't show, and what the build should decide itself.

## Checks
3-8 observable checks a test can run on our clone (input → expected behavior).
```

## Step 3: check the specs

```
python3 <this folder>/spec_check.py replica/spec --raw replica/.probe
```

It flags fenced code blocks, code-shaped lines, and any identifier or string from the raw evidence
that shows up in a spec. It ignores public-standard names it knows, and anything passed with
`--allow` (comma-separated). Use `--allow` only for public standards or protocol names, never for
the target's private names. Findings → send the subagent back to reword (it alone can read the
raw files). Repeat until clean.

## Step 4: lock the dirty room

- `replica/.probe/` goes in `.gitignore`. Never committed, never shown to build agents, never in a
  pitch bundle. Keep it locally as the record of where the spec came from.
- `replica/spec/` is committed. It is what later phases read.

## Gate

`replica/probe-targets.md` exists with the user's confirmation recorded (date + their words), and
either a `replica/spec/*.md` for each target with `spec_check.py` clean, or the phase recorded as
skipped with the reason.

## How later phases use it

Each later phase's `args` gets: "read replica/spec/*.md for the probed features; never open
replica/.probe/". architect turns the Data sections into schema; build and backend implement the
Behavior and Rules sections; test turns each Checks list into named tests; diff counts a probed
feature done only when its Checks pass.

Optional, after test: for a JS/Electron or CLI target, the probe subagent can run REA's
`capture_process_scenario` on the original and on the clone with the same inputs, then
`compare_process_captures`. The comparison goes into `replica/parity.md` as differences in
behavior only. Again, the main thread reads only the subagent's summary.
