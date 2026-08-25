#!/usr/bin/env python3
"""Tru-Trac design system — skill integrity check.

Proves the skill will actually fire and that nothing inside it contradicts
anything else. Run after every edit to the skill.

    python3 scripts/selfcheck.py

Exit 0 = sound, 1 = defects found.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
defects = []


def fail(area, msg):
    defects.append((area, msg))


def read(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- 1. frontmatter
skill = read("SKILL.md")
if skill is None:
    fail("SKILL", "SKILL.md missing — the skill cannot load at all")
else:
    m = re.match(r"---\n(.*?)\n---\n", skill, re.S)
    if not m:
        fail("SKILL", "no YAML frontmatter block; the skill will not be indexed")
    else:
        fm = m.group(1)
        name = re.search(r"^name:\s*(\S+)", fm, re.M)
        desc = re.search(r"^description:\s*(.+?)(?=\n\w+:|\Z)", fm, re.S | re.M)
        if not name:
            fail("SKILL", "frontmatter has no name")
        elif name.group(1) != os.path.basename(ROOT):
            fail("SKILL", f"name '{name.group(1)}' does not match folder '{os.path.basename(ROOT)}'")
        if not desc:
            fail("SKILL", "frontmatter has no description; the skill will never trigger")
        else:
            d = " ".join(desc.group(1).split())
            if len(d) < 120:
                fail("SKILL", f"description is only {len(d)} chars; too thin to trigger reliably")
            if "Use for" not in d and "Use when" not in d:
                fail("SKILL", "description states no trigger condition")

# ------------------------------------------------- 2. every referenced file exists
if skill:
    refs = set(re.findall(r"`((?:tokens|references|scripts|assets|tests)/[A-Za-z0-9_.\-/]+)`", skill))
    refs |= set(re.findall(r"\]\(((?:tokens|references|scripts|assets)/[^)]+)\)", skill))
    for r in sorted(refs):
        if not os.path.exists(os.path.join(ROOT, r)):
            fail("SKILL", f"references '{r}' which does not exist")

# ---------------------------------- 3. every shipped reference file is discoverable
shipped = sorted(
    os.path.join("references", f)
    for f in os.listdir(os.path.join(ROOT, "references"))
    if f.endswith(".md")
)
if skill:
    for s in shipped:
        if s not in skill:
            fail("SKILL", f"'{s}' ships but SKILL.md never points to it; it will never be read")

# ------------------------------------------------------- 4. token file parity
css = read("tokens/tokens.css") or ""
tw = read("tokens/tailwind-v4.css") or ""


def hexes(text):
    return {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", text)}


css_colours = {
    m.group(1): m.group(2).lower()
    for m in re.finditer(r"--tt-([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", css)
}
tw_colours = {
    m.group(1): m.group(2).lower()
    for m in re.finditer(r"--color-tt-([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", tw)
}
for k, v in css_colours.items():
    if k in tw_colours and tw_colours[k] != v:
        fail("TOKENS", f"'{k}' is {v} in tokens.css but {tw_colours[k]} in tailwind-v4.css")

css_scale = set(re.findall(r"--tt-(text-[a-z0-9-]+):", css))
tw_scale = {"text-" + m for m in re.findall(r"--text-([a-z0-9-]+):", tw)}
for s in sorted(css_scale - tw_scale):
    fail("TOKENS", f"type step '{s}' exists in tokens.css but is missing from tailwind-v4.css")

# ------------------------------- 5. no doc or test cites a token that no longer exists
declared = set(re.findall(r"(--tt-[a-z0-9-]+):", css))
for rel in shipped + ["SKILL.md"]:
    txt = read(rel) or ""
    for used in set(re.findall(r"--tt-[a-z0-9-]+", txt)):
        if used not in declared:
            fail("DOCS", f"{rel} cites '{used}' which is not declared in tokens.css")

tests_dir = os.path.join(ROOT, "tests")
if os.path.isdir(tests_dir):
    for dirpath, _, files in os.walk(tests_dir):
        for f in files:
            if not f.endswith((".html", ".css")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
            txt = read(rel) or ""
            if f.endswith(".css"):
                continue
            for used in set(re.findall(r"var\((--tt-[a-z0-9-]+)\)", txt)):
                if used not in declared:
                    fail("TESTS", f"{rel} uses '{used}' which is not declared in tokens.css")

# ------------------------------------------------------- 6. brand values are locked
if "#E1261C" not in css:
    fail("BRAND", "locked brand red #E1261C is not present in tokens.css")
# --------------------------------------------------------------- 7. assets present
LOGO_SET = (
    "lockup-red", "lockup-charcoal", "lockup-red-reverse",
    "lockup-charcoal-reverse", "lockup-white",
    "mark-red", "mark-charcoal", "mark-red-reverse",
    "mark-charcoal-reverse", "mark-white",
)
for a in LOGO_SET:
    if not os.path.exists(os.path.join(ROOT, "assets", a + ".png")):
        fail("ASSETS", f"assets/{a}.png missing; references/logo.md names it")
# every asset named in logo.md must exist
_logo_doc = read("references/logo.md") or ""
import re as _re
for m in _re.findall(r"`([a-z-]+\.png)`", _logo_doc):
    if not os.path.exists(os.path.join(ROOT, "assets", m)):
        fail("ASSETS", f"references/logo.md cites assets/{m} which does not exist")

# ------------------------------------------------------------- 8. validator runs
val = os.path.join(ROOT, "scripts", "validate.py")
if not os.path.exists(val):
    fail("SCRIPTS", "scripts/validate.py missing; the skill claims a verification gate it does not have")
else:
    rc = os.system(f"python3 {val} --selftest > /dev/null 2>&1")
    if rc != 0:
        fail("SCRIPTS", "validate.py --selftest does not pass")

# ------------------------------------------------------------------------ report
print(f"integrity check — {os.path.basename(ROOT)}\n")
if not defects:
    print("  no defects. The skill is internally consistent and will load.")
    sys.exit(0)

by_area = {}
for area, msg in defects:
    by_area.setdefault(area, []).append(msg)
for area in sorted(by_area):
    print(f"  {area}")
    for msg in by_area[area]:
        print(f"    · {msg}")
print(f"\n{len(defects)} defect(s)")
sys.exit(1)
