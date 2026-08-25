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
            # Hard platform ceiling. Over this and the skill is rejected at install time,
            # which is a failure you only discover once, in front of someone.
            if len(d) > 1024:
                fail("SKILL", f"description is {len(d)} chars; the ceiling is 1024 and install will fail")
        if name and len(name.group(1)) > 64:
            fail("SKILL", f"name is {len(name.group(1))} chars; the ceiling is 64")
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
spec = read("system/system.html") or ""


def declared_tokens(text):
    """Every custom property the file declares, name -> value."""
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+?)\s*(?=;)", text, re.I))


css_tokens = declared_tokens(css)
spec_tokens = declared_tokens(spec)

if not css_tokens:
    fail("TOKENS", "tokens.css declares no custom properties")
for k in sorted(set(css_tokens) - set(spec_tokens)):
    fail("TOKENS", f"'{k}' is in tokens.css but not in the living spec")
for k in sorted(set(spec_tokens) - set(css_tokens)):
    fail("TOKENS", f"'{k}' is in the living spec but not in tokens.css")
for k in sorted(set(css_tokens) & set(spec_tokens)):
    if css_tokens[k].strip() != spec_tokens[k].strip():
        fail("TOKENS", f"'{k}' is {css_tokens[k]} in tokens.css but {spec_tokens[k]} in the spec")

# ------------------------------- 5. no doc cites a token that does not exist, and no doc
#                                    annotates a token with the wrong value.
#
# This is the check that would have caught the drift that killed the previous SKILL.md:
# documentation quietly describing a system the token file had already moved off.
declared = set(css_tokens)
ANNOTATED = re.compile(r"`(--[a-z0-9-]+)`\s*\((\d+(?:\.\d+)?)(px|ch|ms|%)\)", re.I)

for rel in shipped + ["SKILL.md"]:
    txt = read(rel) or ""
    for used in sorted(set(re.findall(r"`(--[a-z0-9-]+)`", txt))):
        if used not in declared:
            fail("DOCS", f"{rel} cites '{used}' which is not declared in tokens.css")
    for name, num, unit in ANNOTATED.findall(txt):
        if name not in declared:
            continue
        actual = css_tokens[name].strip()
        if actual.startswith("var("):
            continue
        if actual != f"{num}{unit}" and actual != f"{num.rstrip('0').rstrip('.')}{unit}":
            fail("DOCS", f"{rel} annotates '{name}' as {num}{unit} but tokens.css says {actual}")

# ------------------------------------------- 5b. SKILL.md must name the shipped type stack
if skill:
    fam = re.search(r"--font-sans\s*:\s*'([^']+)'", css)
    if fam and fam.group(1).lower() not in skill.lower():
        fail("DOCS", f"SKILL.md never names '{fam.group(1)}', the shipped --font-sans")
    for ghost in ("Plus Jakarta Sans", "Inter "):
        if ghost in skill and ghost.strip().lower() not in css.lower():
            fail("DOCS", f"SKILL.md names '{ghost.strip()}' which is not in the type stack")

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
            for used in set(re.findall(r"var\((--[a-z0-9-]+)\)", txt)):
                if used not in declared:
                    fail("TESTS", f"{rel} uses '{used}' which is not declared in tokens.css")

# ----------------------------------------------------- OKLCH, resolved not trusted
#
# The accent was wrong for as long as nobody resolved it. The token said
# oklch(0.577 0.223 27.3) and the comment beside it said "#E1261C, locked". Those
# are different colours. A string search for the hex found it in the comment and
# reported the brand as intact. So this converts, in pure Python with no
# dependencies, and compares the actual colour.

def _oklch_to_hex(l, c, h):
    import math
    a = c * math.cos(math.radians(h))
    b = c * math.sin(math.radians(h))
    l_ = (l + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (l - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (l - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )
    out = []
    for v in lin:
        v = 12.92 * v if v <= 0.0031308 else 1.055 * (v ** (1 / 2.4)) - 0.055
        out.append(max(0, min(255, round(v * 255))))
    return "#%02x%02x%02x" % tuple(out)


def _relative_luminance(hexstr):
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255.0
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


def _contrast(fg, bg):
    a, b = _relative_luminance(fg), _relative_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def resolve(name, tokens, _seen=None):
    """Follow var() chains down to a literal, then resolve oklch() to hex."""
    _seen = _seen or set()
    if name in _seen or name not in tokens:
        return None
    _seen.add(name)
    val = tokens[name].strip()
    m = re.fullmatch(r"var\(\s*(--[a-z0-9-]+)\s*\)", val)
    if m:
        return resolve(m.group(1), tokens, _seen)
    m = re.fullmatch(r"oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)", val)
    if m:
        return _oklch_to_hex(float(m.group(1)), float(m.group(2)), float(m.group(3)))
    if re.fullmatch(r"#[0-9a-fA-F]{6}", val):
        return val.lower()
    return None


BRAND_RED = "#e1261c"          # Pantone 485C. Locked. See references/logo.md.

accent = resolve("--accent", css_tokens)
if accent is None:
    fail("BRAND", "--accent does not resolve to a colour; the chain is broken")
elif accent != BRAND_RED:
    fail("BRAND", f"--accent resolves to {accent}, not the locked brand red {BRAND_RED}")

a5 = resolve("--a-5", css_tokens)
if a5 and a5 != BRAND_RED:
    fail("BRAND", f"--a-5 resolves to {a5}, not the locked brand red {BRAND_RED}")

# The button contract is a white label on the accent fill. If that stops passing AA,
# the contract is broken and no amount of correct tokens saves it.
if accent:
    ratio = _contrast("#ffffff", accent)
    if ratio < 4.5:
        fail("A11Y", f"white on --accent is {ratio:.2f}:1, below the 4.5:1 floor")

# ------------------------------------------------- scripts a doc names must exist
for rel in shipped + ["SKILL.md"]:
    txt = read(rel) or ""
    for script in sorted(set(re.findall(r"(scripts/[A-Za-z0-9_.\-]+\.py)", txt))):
        if not os.path.exists(os.path.join(ROOT, script)):
            fail("DOCS", f"{rel} tells the reader to run '{script}', which does not exist")

# ------------------------------- a doc may only name a hex the system actually owns
DOCUMENTED_HEX = {
    BRAND_RED, "#414042",                      # locked brand values
    "#e42526", "#e32726", "#3a3a3c",           # the raster discrepancy, named to warn
    "#df1c21", "#df1c2f",                      # the corrected and the rejected red, in provenance
    "#181a1d", "#1d1c1e",                      # retired direction, recorded in provenance
    "#a3a3a6", "#a8acb1",                      # the reference's duplicate greys, quoted
}
for rel in shipped + ["SKILL.md"]:
    txt = read(rel) or ""
    for hx in sorted({h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", txt)}):
        if hx not in DOCUMENTED_HEX:
            fail("DOCS", f"{rel} names {hx}, which is not a value this system owns or documents")

# ------------------------------------------------------- 6. brand values are locked
if "#E1261C" not in css:
    fail("BRAND", "locked brand red #E1261C is not recorded in tokens.css")
# The literal value is deliberately NOT asserted here. Pinning the string is what let
# the wrong colour sit in place behind a comment that claimed otherwise. The resolver
# check above compares the colour, which is the thing that matters.
if css_tokens.get("--accent", "").strip() != "var(--a-5)":
    fail("BRAND", "--accent no longer points at the locked brand primitive --a-5")
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
