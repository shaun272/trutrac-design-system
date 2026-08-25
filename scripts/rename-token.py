#!/usr/bin/env python3
"""Rename a design token safely, everywhere, and prove it still resolves.

Three ways a token rename goes wrong, all of which happened in this project:

  1. Usages renamed, declaration missed.   --focus -> --accent-focus
     Every var(--accent-focus) then resolves to nothing. Focus rings vanish and
     look exactly like no focus ring was ever specified.

  2. The VALUE renamed instead of the NAME. --spin-track:var(--spinner-track)
     A declaration's right-hand side is a value. A name-rename must never touch it.

  3. Self-reference.                        --paper-rule-1:var(--paper-rule-1)
     Caused by substituting raw values for token names across the whole file,
     including the :root block, where those raw values ARE the declarations.

This tool renames declarations and usages as separate operations, refuses to
create a self-reference, applies longest-name-first so --rule does not clobber
--rule-2, and updates the reference docs in the same pass so they cannot drift.

    python3 scripts/rename-token.py --old focus --new accent-focus
    python3 scripts/rename-token.py --old=--focus --new=--accent-focus
    python3 scripts/rename-token.py --map renames.json
    python3 scripts/rename-token.py --old rule-2 --new rule-hairline --dry-run

Always finishes by running ds-audit, which renders the page and asks the browser
what every token actually resolves to. That is the only check that catches a CSS
parse error, and a regex never will.
"""

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM = os.path.join(ROOT, "system", "system.html")
TOKENS = os.path.join(ROOT, "tokens", "tokens.css")
DOCS = os.path.join(ROOT, "references")


def targets():
    files = [SYSTEM, TOKENS]
    if os.path.isdir(DOCS):
        files += [os.path.join(DOCS, f) for f in sorted(os.listdir(DOCS)) if f.endswith(".md")]
    return [f for f in files if os.path.exists(f)]


def rename_in(text, mapping, is_doc=False):
    """Declarations and usages are renamed as separate, explicit operations."""
    changes = 0
    # longest first, so --rule does not eat --rule-2
    for old, new in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        # 1 · usages:  var(--old)  ->  var(--new)
        pat_use = re.compile(r"var\(\s*" + re.escape(old) + r"\s*([,)])")
        text, n1 = pat_use.subn(lambda m: f"var({new}{m.group(1)}", text)
        # 2 · declarations:  --old:  ->  --new:   (left-hand side only)
        pat_dec = re.compile(r"(^|[;{\s])" + re.escape(old) + r"(\s*:)", re.M)
        text, n2 = pat_dec.subn(lambda m: f"{m.group(1)}{new}{m.group(2)}", text)
        # 3 · documentation references, which are written as `--token`
        n3 = 0
        if is_doc:
            text, n3 = re.subn(r"`" + re.escape(old) + r"`", f"`{new}`", text)
        changes += n1 + n2 + n3
    return text, changes


def self_referential(text):
    return sorted(set(re.findall(r"(--[a-z0-9-]+)\s*:\s*var\(\s*\1\s*\)", text)))


def undeclared(text):
    declared = set(re.findall(r"(--[a-z0-9-]+)\s*:", text))
    used = set(re.findall(r"var\(\s*(--[a-z0-9-]+)", text))
    return sorted(used - declared)


def main():
    # argparse treats a value beginning with -- as a flag, so accept the bare
    # stem too: --old rule-2 is the same as --old=--rule-2
    ap = argparse.ArgumentParser()
    ap.add_argument("--old")
    ap.add_argument("--new")
    ap.add_argument("--map", help="JSON file of {old: new}")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    norm = lambda n: n if n.startswith("--") else "--" + n.lstrip("-")
    if a.map:
        mapping = {norm(k): norm(v) for k, v in json.load(open(a.map)).items()}
    elif a.old and a.new:
        mapping = {norm(a.old): norm(a.new)}
    else:
        print(__doc__)
        return 2

    for old, new in mapping.items():
        if old == new:
            print(f"refusing a no-op rename: {old}")
            return 2

    print(f"renaming {len(mapping)} token(s)\n")
    edited = []
    for path in targets():
        src = open(path, encoding="utf-8").read()
        out, n = rename_in(src, mapping, is_doc=path.endswith(".md"))
        if n:
            rel = os.path.relpath(path, ROOT)
            print(f"  {rel:44} {n} change(s)")
            edited.append((path, out))

    if not edited:
        print("  nothing matched. Check the spelling of the old name.")
        return 1

    # refuse to write anything that breaks
    for path, out in edited:
        if path.endswith((".html", ".css")):
            circ = self_referential(out)
            if circ:
                print(f"\nREFUSED: this rename creates a self-reference in "
                      f"{os.path.relpath(path, ROOT)}: {', '.join(circ)}")
                return 1

    if a.dry_run:
        print("\ndry run, nothing written")
        return 0

    for path, out in edited:
        open(path, "w", encoding="utf-8").write(out)

    sysdoc = open(SYSTEM, encoding="utf-8").read()
    missing = undeclared(sysdoc)
    if missing:
        print(f"\nWARNING: now used but never declared: {', '.join(missing)}")

    audit = os.path.join(ROOT, "scripts", "ds-audit.py")
    if os.path.exists(audit):
        print("\nrunning the audit, including runtime resolution in a browser\n")
        subprocess.run([sys.executable, audit, SYSTEM])
    return 0


if __name__ == "__main__":
    sys.exit(main())
