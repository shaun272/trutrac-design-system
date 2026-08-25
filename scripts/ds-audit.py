#!/usr/bin/env python3
"""Tru-Trac design system audit.

Measures what a design system audit is supposed to measure: token coverage,
hardcoded values that should be tokens, naming consistency across the token
namespace, and component completeness by state.

    python3 scripts/ds-audit.py system/system-v9.html
"""

import os
import re
import sys
from collections import defaultdict

SPACING_SCALE = {0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128}
RADIUS_SCALE = {0, 2, 3, 5, 999}
# values that are legitimately outside the spacing scale
PX_EXEMPT_PROPS = {
    "font-size", "line-height", "letter-spacing", "border", "border-top", "border-bottom",
    "border-left", "border-right", "border-width", "outline", "outline-offset", "stroke-width",
    "min-width", "max-width", "width", "height", "min-height", "flex", "top", "background-size",
    "background", "grid-template-columns", "transform", "translate", "aspect-ratio", "inset",
    "box-shadow", "filter", "backdrop-filter", "background-position", "scroll-margin-top",
}

STATES = ("hover", "focus", "active", "disabled", "loading/busy", "error", "readonly")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def split(src):
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S | re.I))
    root = "\n".join(re.findall(r"(?::root|\[data-mode[^\]]*\])\s*\{(.*?)\n\s*\}", css, re.S))
    body = re.sub(r"(?::root|\[data-mode[^\]]*\])\s*\{.*?\n\s*\}", "", css, flags=re.S)
    markup = re.sub(r"<style[^>]*>.*?</style>", "", src, flags=re.S | re.I)
    return css, root, body, markup


def tokens(root):
    out = defaultdict(list)
    for name, val in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", root):
        stem = name[2:]
        if re.match(r"^n-\d|^a-\d|^ok$|^warn$|^info$", stem):
            cat = "colour, primitive"
        elif re.search(r"page|panel|ink|rule|accent|hair|line-heavy|focus|surface", stem):
            cat = "colour, semantic"
        elif stem.startswith(("f-", "l-")) or stem in ("face", "mono"):
            cat = "typography"
        elif stem.startswith("s-") or stem in ("base", "measure", "tap"):
            cat = "spacing"
        elif stem.startswith("r-"):
            cat = "radius"
        elif stem.startswith(("t-", "ease", "spring")):
            cat = "motion"
        elif stem.startswith("z-"):
            cat = "z-index"
        else:
            cat = "other"
        out[cat].append((name, val.strip()))
    return out


def hardcoded(body):
    findings = defaultdict(list)
    for m in re.finditer(r"(?<![-\w])(#[0-9a-fA-F]{3,8})\b", body):
        findings["hex colour"].append(m.group(1))
    for m in re.finditer(r"\boklch\([^)]*\)", body):
        findings["raw oklch"].append(m.group(0)[:34])
    for m in re.finditer(r"([a-z-]+)\s*:\s*([^;{}]*?)(\d+(?:\.\d+)?)px", body):
        prop, val = m.group(1), m.group(3)
        if prop in PX_EXEMPT_PROPS or "var(" in m.group(2):
            continue
        if prop in ("padding", "margin", "gap", "padding-block", "padding-inline",
                    "margin-top", "margin-bottom", "padding-top", "padding-bottom",
                    "row-gap", "column-gap", "padding-left", "padding-right"):
            if float(val) not in SPACING_SCALE:
                findings["off-scale spacing"].append(f"{prop}: {val}px")
        elif prop == "border-radius":
            if float(val) not in RADIUS_SCALE:
                findings["off-scale radius"].append(f"{val}px")
    return findings


def undefined_vars(css):
    """A var() with no matching declaration renders as nothing. The hardcoded-value
    check cannot see this, and a broken focus ring looks exactly like no focus ring."""
    declared = set(re.findall(r"(--[a-z0-9-]+)\s*:", css))
    used = set(re.findall(r"var\(\s*(--[a-z0-9-]+)", css))
    return sorted(used - declared)


def circular(css):
    """A declaration that references itself resolves to nothing. It looks declared to
    a regex and it is invisible in the browser."""
    return sorted(set(re.findall(r"(--[a-z0-9-]+)\s*:\s*var\(\s*\1\s*\)", css)))


def runtime_check(path, css):
    """The definitive check. Render the page and ask the browser what every token
    actually resolves to. A regex cannot see a CSS parse error; the browser can.
    Skipped silently when Playwright is unavailable."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    names = sorted(set(re.findall(r"(--[a-z0-9-]+)\s*:", css)))
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            pg.goto("file://" + os.path.abspath(path))
            pg.wait_for_timeout(2200)
            empty = pg.evaluate(
                "(n)=>{const c=getComputedStyle(document.documentElement);"
                "return n.filter(x=>!c.getPropertyValue(x).trim())}", names)
            b.close()
        return names, empty
    except Exception:
        return None


def naming(tok, _root_comment=""):
    issues = []
    stems = [n for group in tok.values() for n, _ in group]
    prefixes = defaultdict(list)
    for n in stems:
        prefixes[n[2:].split("-")[0]].append(n)
    singles = {p: v for p, v in prefixes.items() if len(v) == 1}
    documented = {"layout", "accent", "photo", "status", "spinner"}
    singles = {p: v for p, v in singles.items() if p not in documented}
    if len(singles) > 4:
        issues.append(("One-off token prefixes",
                       ", ".join(sorted(singles)),
                       "Fold into an existing namespace or accept as documented singletons"))
    # a ramp is <optional-namespace>-rule-N. Several namespaces are fine; several
    # naming *shapes* for the same concept are not.
    rules = [n for n in stems if re.search(r"rule|hair|line-heavy", n)]
    shapes = {("ramp" if re.match(r"^--([a-z]+-)?rule-\d+$", n) else n) for n in rules}
    stray = sorted(s for s in shapes if s != "ramp")
    if stray:
        issues.append(("Rule weights use mixed naming", ", ".join(stray),
                       "One shape: <namespace>-rule-N"))
    if "CONVENTION:" in _root_comment:
        return issues
    scale_a = [n for n in stems if n.startswith("--f-")]
    scale_b = [n for n in stems if n.startswith("--s-")]
    if scale_a and scale_b:
        a = {n.split("-")[-1] for n in scale_a}
        if not a & {"1", "2", "3"}:
            issues.append(("Type scale is named by role, spacing by number",
                           "--f-body / --s-4",
                           "Defensible, but state it so nobody 'fixes' one to match the other"))
    return issues


def components(body, markup):
    defs = {
        "Button":      (r"\.btn\b", ["hover", "focus", "active", "disabled", "busy"]),
        "Input":       (r"\.in\b", ["hover", "focus", "disabled", "readonly", "bad"]),
        "Checkbox":    (r"\.ck\b", ["checked", "focus-visible"]),
        "Table":       (r"table\.doc", ["hover", "aria-sort", "tfoot"]),
        "Tabs":        (r"\.tabs\b", ["hover", "aria-selected"]),
        "Admonition":  (r"\.adm\b", ["note", "caution", "warning"]),
        "Empty state": (r"\.emptystate\b", ["ph", "btn"]),
        "TOC":         (r"\.toc\b", ["hover"]),
        "KPI":         (r"\.kpi\b", ["up", "dn"]),
        "Sheet":       (r"\.sheet\b", ["cover", "rh", "folio"]),
        "Slide":       (r"\.slide\b", ["dark", "sf"]),
        "Pull quote":  (r"\.pull\b", ["cite"]),
    }
    rows = []
    for name, (sel, needed) in defs.items():
        present = bool(re.search(sel, body))
        blocks = "\n".join(
            b for b in re.findall(r"[^{}]*\{[^{}]*\}", body)
            if re.search(sel, b.split("{")[0])
        )
        scope = blocks + markup
        have = [n for n in needed if re.search(re.escape(n), scope)]
        score = round(10 * len(have) / len(needed)) if present else 0
        rows.append((name, len(have), len(needed), sorted(set(needed) - set(have)), score))
    return rows


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    src = load(argv[1])
    css, root, body, markup = split(src)
    tok = tokens(root)
    hard = hardcoded(body)
    name_issues = naming(tok, root)
    undef = undefined_vars(css)
    circ = circular(css)
    rt = runtime_check(argv[1], css)
    comps = components(body, markup)

    total_tokens = sum(len(v) for v in tok.values())
    hard_count = sum(len(v) for v in hard.values())

    print(f"\nDESIGN SYSTEM AUDIT — {os.path.basename(argv[1])}")
    print("=" * 62)

    print(f"\nTOKEN COVERAGE  ({total_tokens} declared)")
    for cat in sorted(tok):
        print(f"  {cat:22} {len(tok[cat]):>3}")

    print(f"\nHARDCODED VALUES  ({hard_count} outside the token block)")
    if not hard:
        print("  none")
    for kind, items in sorted(hard.items()):
        uniq = sorted(set(items))
        print(f"  {kind:22} {len(items):>3}  ({len(uniq)} distinct)")
        for u in uniq[:6]:
            print(f"        {u}")
        if len(uniq) > 6:
            print(f"        ... {len(uniq)-6} more")

    print(f"\nVARIABLE INTEGRITY")
    print(f"  used but never declared   {len(undef)}")
    for u in undef:
        print(f"      {u}")
    print(f"  self-referential          {len(circ)}")
    for c in circ:
        print(f"      {c}: var({c})")
    if rt is None:
        print("  runtime resolution        skipped, no browser available")
    else:
        names, empty = rt
        print(f"  runtime resolution        {len(names)-len(empty)}/{len(names)} resolve")
        for e in empty:
            print(f"      {e} resolves to nothing in the browser")

    print(f"\nNAMING CONSISTENCY  ({len(name_issues)} issue(s))")
    if not name_issues:
        print("  consistent")
    for title, where, rec in name_issues:
        print(f"  · {title}\n      {where}\n      -> {rec}")

    print("\nCOMPONENT COMPLETENESS")
    print(f"  {'Component':<14}{'Have':>5}{'Need':>6}{'Score':>7}   Missing")
    worst = 0
    for name, have, need, missing, score in comps:
        worst += (10 - score)
        print(f"  {name:<14}{have:>5}{need:>6}{score:>6}/10   {', '.join(missing) or '—'}")

    # score: token discipline 40, naming 20, components 40
    rt_empty = 0 if rt is None else len(rt[1])
    tok_score = max(0, 40 - hard_count - len(undef) * 8 - len(circ) * 8 - rt_empty * 8)
    name_score = max(0, 20 - len(name_issues) * 5)
    comp_score = round(40 * sum(c[4] for c in comps) / (10 * len(comps)))
    total = tok_score + name_score + comp_score
    print("\n" + "=" * 62)
    print(f"  token discipline   {tok_score:>3}/40   ({hard_count} hardcoded, {len(undef)+len(circ)+rt_empty} broken)")
    print(f"  naming             {name_score:>3}/20   ({len(name_issues)} issues)")
    print(f"  components         {comp_score:>3}/40")
    print(f"  TOTAL              {total:>3}/100")
    return 0 if total >= 90 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
