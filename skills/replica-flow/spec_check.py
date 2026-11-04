#!/usr/bin/env python3
"""Clean-room check for probe specs.

Flags, in every replica/spec/*.md:
  - fenced code blocks and code-shaped lines;
  - identifiers (camelCase, PascalCase, snake_case, dotted.names) found in the raw probe files;
  - long string literals (likely UI copy or messages) found in the raw probe files.

Usage:
  python3 spec_check.py replica/spec --raw replica/.probe [--allow "name1,name2"]
  python3 spec_check.py --selftest
Exit 1 if anything is flagged. Standard library only, Python 3.8+.
"""
import argparse
import os
import re
import sys
import tempfile

IDENT = re.compile(
    r"\b(?:[a-z][a-z0-9]*[A-Z]\w*"          # camelCase
    r"|[A-Z][a-z0-9]+[A-Z]\w*"              # PascalCase
    r"|[A-Za-z]\w*_\w+"                     # snake_case
    r"|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*){2,})\b"  # a.b.c
)
STRING = re.compile(r"[\"']([^\"'\\\n]{16,200})[\"']")
CODE_LINE = re.compile(
    r"=>|\bfunction\s*\(|\)\s*\{|;\s*$|^\s*(?:def|class|import|return|const|let|var|#include)\b"
)
# Public standards and platform APIs a spec may name. Extend per run with --allow.
PUBLIC = {
    "JavaScript", "TypeScript", "GitHub", "WebSocket", "WebSockets", "PostgreSQL", "MySQL",
    "IndexedDB", "localStorage", "sessionStorage", "OAuth", "WebAssembly", "WebRTC", "GraphQL",
    "macOS", "iOS", "iPhone", "iPad", "NodeJS", "OpenAPI", "JSONPath", "SQLite", "HTTPS",
    "Content-Type", "user_agent",
}
SKIP_RAW_BYTES = 50 * 1024 * 1024  # ponytail: whole-file reads; stream if raw dumps exceed 50 MB


def raw_terms(raw_dir):
    idents, strings = set(), set()
    for root, _, files in os.walk(raw_dir):
        for name in files:
            path = os.path.join(root, name)
            if os.path.getsize(path) > SKIP_RAW_BYTES:
                print(f"note: skipped large raw file {path}", file=sys.stderr)
                continue
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
            idents.update(m for m in IDENT.findall(text) if len(m) >= 5)
            strings.update(s.strip() for s in STRING.findall(text) if " " in s.strip())
    return idents, strings


def check(spec_dir, raw_dir, allow):
    idents, strings = raw_terms(raw_dir) if raw_dir else (set(), set())
    idents -= PUBLIC | allow
    findings = []
    for name in sorted(os.listdir(spec_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(spec_dir, name)
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        in_fence = False
        for no, line in enumerate(lines, 1):
            if line.lstrip().startswith("```"):
                if not in_fence:
                    findings.append((path, no, "fenced code block: describe it in prose or a table"))
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if CODE_LINE.search(line) and not line.lstrip().startswith("|"):
                findings.append((path, no, "code-shaped line"))
            for tok in set(IDENT.findall(line)) & idents:
                findings.append((path, no, f"identifier from raw evidence: {tok}"))
            for s in strings:
                if s in line:
                    findings.append((path, no, f"string from raw evidence: {s[:60]!r}"))
    return findings


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        spec, raw = os.path.join(tmp, "spec"), os.path.join(tmp, "raw")
        os.makedirs(spec), os.makedirs(raw)
        with open(os.path.join(raw, "dump.json"), "w") as f:
            f.write('{"fn": "mergeRemoteChanges", "msg": "Your changes could not be synced", '
                    '"store": "localStorage", "k": "pending_ops_queue"}')
        with open(os.path.join(spec, "clean.md"), "w") as f:
            f.write("# Sync\n\nQueued edits are kept in localStorage and sent oldest first.\n"
                    "| field | type |\n|---|---|\n| created at | timestamp |\n")
        with open(os.path.join(spec, "dirty.md"), "w") as f:
            f.write("Calls mergeRemoteChanges on reconnect.\nShows 'Your changes could not be synced'.\n"
                    "Uses pending_ops_queue.\n```js\nx()\n```\nconst a = 1;\n")
        got = check(spec, raw, set())
        assert not [g for g in got if g[0].endswith("clean.md")], got
        reasons = " ".join(g[2] for g in got)
        for needle in ("mergeRemoteChanges", "could not be synced", "pending_ops_queue",
                       "fenced code block", "code-shaped line"):
            assert needle in reasons, (needle, got)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec_dir", nargs="?")
    ap.add_argument("--raw", help="raw probe folder, e.g. replica/.probe")
    ap.add_argument("--allow", default="", help="comma-separated public names to permit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.spec_dir or not os.path.isdir(a.spec_dir):
        ap.error("spec_dir must be an existing folder")
    if a.raw and not os.path.isdir(a.raw):
        ap.error("--raw must be an existing folder")
    allow = {s.strip() for s in a.allow.split(",") if s.strip()}
    findings = check(a.spec_dir, a.raw, allow)
    for path, no, why in findings:
        print(f"{path}:{no}: {why}")
    print(f"{len(findings)} finding(s)" if findings else "clean")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
