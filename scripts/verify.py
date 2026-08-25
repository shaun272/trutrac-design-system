#!/usr/bin/env python3
"""Tru-Trac design system — run every gate.

One command, so nobody has to remember three.

    python3 scripts/verify.py                    # the system itself
    python3 scripts/verify.py path/to/page.html  # the system, then that page

Exit 0 = everything passed. Exit 1 = something failed, and the output says what.
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "system", "system.html")


def run(label, args):
    print(f"\n{'=' * 66}\n{label}\n{'=' * 66}")
    rc = subprocess.call([sys.executable] + args, cwd=ROOT)
    return label, rc


def main():
    pages = [os.path.abspath(p) for p in sys.argv[1:]]

    results = [
        run("1/3  selfcheck — the skill is sound and will load",
            ["scripts/selfcheck.py"]),
        run("2/3  ds-audit — token discipline, naming, completeness",
            ["scripts/ds-audit.py", SPEC]),
    ]

    if pages:
        for p in pages:
            results.append(run(f"3/3  density — {os.path.basename(p)} is not empty",
                               ["scripts/density.py", p]))
    else:
        results.append(run("3/3  density — the living spec is not empty",
                           ["scripts/density.py", SPEC]))

    print(f"\n{'=' * 66}\nSUMMARY\n{'=' * 66}")
    failed = 0
    for label, rc in results:
        state = "PASS" if rc == 0 else "FAIL"
        if rc != 0:
            failed += 1
        print(f"  {state}  {label.split('  ', 1)[1] if '  ' in label else label}")

    if failed:
        print(f"\n{failed} gate(s) failed. Nothing ships until they are green.")
        return 1
    print("\nAll gates green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
