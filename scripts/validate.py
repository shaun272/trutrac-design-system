#!/usr/bin/env python3
"""Tru-Trac design system compliance checker.

Usage:
    python3 validate.py path/to/page.html [more.html ...]
    python3 validate.py --selftest

Exit code 0 = pass, 1 = violations found, 2 = usage error.
"""

import re
import sys
import os

# ---------------------------------------------------------------- token truth

ALLOWED_HEX = {
    "#e1261c": "tt-red",
    "#c12118": "tt-red-hover",
    "#414042": "tt-grey / tt-ink",
    "#1d1c1e": "tt-stage",
    "#2a2a2b": "tt-stage-raised",
    "#6a696b": "tt-ink-muted",
    "#8e8d90": "tt-ink-subtle",
    "#e3e3e3": "tt-border",
    "#f7f7f7": "tt-canvas",
    "#ffffff": "tt-surface / on-stage",
    "#fff":    "tt-surface / on-stage",
    "#b3b3b4": "tt-on-stage-muted",
    "#f5f5f5": "shimmer midpoint",
    "#010101": "tt-void",
    "#141416": "tt-void-panel",
    "#191919": "tt-void-raise",
    "#e6e6e6": "tt-on-void",
    "#c12118": "tt-red-hover",
    "#000":    "transparent-black only",
    "#000000": "transparent-black only",
}

ALLOWED_RADIUS_PX = {0, 4, 6, 12, 24, 28, 100, 170, 180, 999, 9999}
ALLOWED_FAMILIES = ("plus jakarta sans", "inter", "jetbrains mono")
MAX_HEADING_WEIGHT = 600

# ------------------------------------------------------------------- contrast

def _srgb(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def luminance(hexstr):
    h = hexstr.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _srgb(r) + 0.7152 * _srgb(g) + 0.0722 * _srgb(b)

def contrast(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)

# Pairs the system asserts. Checked on every run regardless of the file.
CONTRAST_ASSERTIONS = [
    ("#414042", "#ffffff", 4.5, "body text on card"),
    ("#414042", "#f7f7f7", 4.5, "body text on canvas"),
    ("#6a696b", "#ffffff", 4.5, "secondary text on card"),
    ("#6a696b", "#f7f7f7", 4.5, "secondary text on canvas"),
    ("#ffffff", "#e1261c", 4.5, "button label on red fill"),
    ("#ffffff", "#1d1c1e", 4.5, "text on stage"),
    ("#b3b3b4", "#1d1c1e", 4.5, "secondary text on stage"),
    ("#8e8d90", "#ffffff", 3.0, "input border on card"),
    ("#e1261c", "#ffffff", 3.0, "red focus border on card"),
]

# --------------------------------------------------------------------- checks

HEX_RE = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b")
RADIUS_RE = re.compile(r"border-radius\s*:\s*([^;}\"']+)", re.I)
SHADOW_RE = re.compile(r"box-shadow\s*:\s*([^;}\"']+)", re.I)
FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}]+)", re.I)
WEIGHT_RE = re.compile(r"font-weight\s*:\s*(\d{3})", re.I)
IMG_RE = re.compile(r'<img[^>]+src\s*=\s*["\']([^"\']+)["\'][^>]*>', re.I)

def strip_documentation(text):
    """Remove <code> spans and drawing-annotation <text> before the colour check.

    A page that documents its own rules will quote the values it forbids. The
    DO-NOT-SAMPLE warning names the three raster colours precisely so nobody uses
    them; flagging that as usage punishes the system for explaining itself."""
    text = blank_out(text, r"<code\b.*?</code>", re.S | re.I)
    text = blank_out(text, r"<text\b.*?</text>", re.S | re.I)
    return text


def blank_out(text, pattern, flags=0):
    """Replace a match with the same number of newlines, so every later line
    number still points at the real file. Deleting the block shifted them."""
    def keep(m):
        return "\n" * m.group(0).count("\n")
    return re.sub(pattern, keep, text, flags=flags)


def strip_token_defs(text):
    """Remove the :root/@theme token block so token definitions are not
    themselves reported as hardcoded values, and remove SVG <defs> blocks.

    A rendered object needs a shading ramp — a dozen neutral greys describing how
    light falls across metal. That is a material, not a brand palette, and the
    brand token list has no business governing it. The ramp is constrained
    separately: neutrals plus the brand red, no other hue. See
    references/art-direction.md."""
    text = blank_out(text, r"(:root|@theme)\s*\{.*?\n\s*\}", re.S)
    text = blank_out(text, r"<defs\b.*?</defs>", re.S | re.I)
    return text

HUE_TOL = 14   # max channel spread before a "neutral" is really a colour


def check_material_ramp(text):
    """Colours inside <defs> are exempt from the brand list but not unchecked:
    every stop must be a neutral grey or the brand red."""
    out = []
    for block in re.findall(r"<defs\b.*?</defs>", text, flags=re.S | re.I):
        for m in re.finditer(r"#([0-9a-fA-F]{6})\b", block):
            h = m.group(1).lower()
            r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
            if h in ("e1261c", "c12118"):
                continue
            if max(r, g, b) - min(r, g, b) > HUE_TOL:
                line = text[:m.start()].count("\n") + 1
                out.append((line, "RAMP", f"#{h} in a render ramp is not neutral or brand red"))
    return out


def check(path, text):
    v = []
    v.extend(check_material_ramp(text))
    body = strip_documentation(strip_token_defs(text))

    for m in HEX_RE.finditer(body):
        h = m.group(0).lower()
        if h not in ALLOWED_HEX:
            line = body[:m.start()].count("\n") + 1
            v.append((line, "COLOUR", f"{m.group(0)} is not a system token"))

    for m in RADIUS_RE.finditer(body):
        raw = m.group(1)
        if "var(" in raw:
            continue
        for num in re.findall(r"(\d+(?:\.\d+)?)(px|%)?", raw):
            val = float(num[0])
            if num[1] == "%":
                continue
            if val not in ALLOWED_RADIUS_PX:
                line = body[:m.start()].count("\n") + 1
                v.append((line, "RADIUS", f"{val:g}px is not 6 / 24 / 28 / pill"))

    for m in SHADOW_RE.finditer(body):
        raw = m.group(1).strip().lower()
        if raw in ("none", "var(--tt-shadow)"):
            continue
        # A focus ring is not a drop shadow. box-shadow with zero offset AND zero
        # blur is a ring: it cannot cast, only surround. Browsers still render the
        # outline property inside overflow:hidden inconsistently, so a spread-only
        # box-shadow is the correct implementation and the system permits it.
        if re.match(r"^0\s+0\s+0\s+\d", raw) or re.match(r"^inset\s+0\s+0\s+0\s+\d", raw):
            continue
        line = body[:m.start()].count("\n") + 1
        v.append((line, "SHADOW", "the system has no drop shadows"))

    for m in FAMILY_RE.finditer(body):
        raw = m.group(1).lower()
        if "var(" in raw:
            continue
        if not any(f in raw for f in ALLOWED_FAMILIES):
            line = body[:m.start()].count("\n") + 1
            v.append((line, "FONT", f"{m.group(1).strip()[:44]} is outside the type stack"))

    for m in WEIGHT_RE.finditer(body):
        w = int(m.group(1))
        if w > MAX_HEADING_WEIGHT:
            line = body[:m.start()].count("\n") + 1
            v.append((line, "WEIGHT", f"font-weight {w} exceeds the 600 ceiling"))

    v.extend(check_logo_surface(text))
    return v

# ------------------------------------------------- logo / surface reconciliation

DARK_VALUES = ("var(--tt-stage)", "var(--tt-stage-raised)", "#1d1c1e", "#2a2a2b",
                "var(--tt-void)", "var(--tt-void-panel)", "var(--bg)", "var(--panel)",
                "#010101", "#141416", "#191919")
LIGHT_VALUES = ("var(--tt-canvas)", "var(--tt-surface)", "#f7f7f7", "#ffffff", "#fff")

def surface_classes(css):
    """Read the stylesheet and return the class names that actually paint a dark
    background and those that paint a light one. Evidence, not guesswork."""
    dark, light = set(), set()
    for sel, block in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        bg = re.search(r"(?:^|[;\s])background(?:-color)?\s*:\s*([^;]+)", block, re.I)
        if not bg:
            continue
        val = bg.group(1).strip().lower()
        names = re.findall(r"\.([A-Za-z0-9_-]+)", sel)
        if any(d in val for d in DARK_VALUES):
            dark.update(names)
        elif any(l in val for l in LIGHT_VALUES):
            light.update(names)
    return dark, light

def check_logo_surface(text):
    """Walk the DOM keeping an element stack, and judge each logo <img> by the
    nearest ancestor that paints a background."""
    from html.parser import HTMLParser

    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S | re.I))
    dark, light = surface_classes(css)
    # a page whose body sits on the void set is dark unless a block says otherwise
    m = re.search(r"body\s*\{[^}]*background\s*:\s*([^;]+)", css, re.I)
    page_is_dark = bool(m) and any(d in m.group(1).lower() for d in DARK_VALUES)
    found = []

    class Walker(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack = []

        def _surface(self, attrs):
            style = (attrs.get("style") or "").lower()
            if any(d in style for d in DARK_VALUES):
                return "dark"
            if any(l in style for l in LIGHT_VALUES):
                return "light"
            for c in (attrs.get("class") or "").split():
                if c in dark:
                    return "dark"
                if c in light:
                    return "light"
            return None

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "body":
                self.stack.append("dark" if page_is_dark else None)
                return
            if tag == "img":
                src = (a.get("src") or "").lower()
                if "logo-" in src:
                    ctx = next((s for s in reversed(self.stack) if s), "light")
                    line = self.getpos()[0]
                    if "logo-primary" in src and ctx == "dark":
                        found.append((line, "LOGO",
                                      "primary logo on a dark surface; use logo-reverse"))
                    if "logo-reverse" in src and ctx == "light":
                        found.append((line, "LOGO",
                                      "reverse logo on a light surface; use logo-primary"))
                return
            if tag not in ("br", "hr", "meta", "link", "input", "source"):
                self.stack.append(self._surface(a))

        def handle_endtag(self, tag):
            if self.stack:
                self.stack.pop()

    try:
        Walker().feed(text)
    except Exception as exc:
        found.append((0, "LOGO", f"could not parse markup for logo check: {exc}"))
    return found

def run_contrast():
    fails = []
    for fg, bg, floor, label in CONTRAST_ASSERTIONS:
        r = contrast(fg, bg)
        if r < floor:
            fails.append(f"{label}: {r:.2f}:1 below {floor}:1  ({fg} on {bg})")
    return fails

# ------------------------------------------------------------------- selftest

GOOD = """<style>:root{--tt-red:#E1261C;}
.h{font-family:'Plus Jakarta Sans';font-weight:600;color:var(--tt-ink);}
.btn{background:#E1261C;border-radius:28px;box-shadow:none;}
.card{background:#FFFFFF;border:1px solid #E3E3E3;border-radius:24px;}</style>
<style>.stage{background:var(--tt-stage);}</style>\n<div class="stage"><img src="assets/trutrac-logo-reverse.png"></div>"""

BAD = """<style>
.h{font-family:'Poppins';font-weight:800;color:#2ECC71;}
.btn{background:#df1c2f;border-radius:18px;box-shadow:0 4px 12px rgba(0,0,0,.2);}</style>
<div class="stage" style="background:#1d1c1e"><img src="assets/trutrac-logo-primary.png"></div>"""

def selftest():
    ok = True
    g = check("<good>", GOOD)
    if g:
        ok = False
        print("SELFTEST FAIL: clean sample flagged", g)
    else:
        print("  clean sample passes                         OK")

    b = check("<bad>", BAD)
    kinds = {k for _, k, _ in b}
    expected = {"COLOUR", "RADIUS", "SHADOW", "FONT", "WEIGHT", "LOGO"}
    missing = expected - kinds
    if missing:
        ok = False
        print("SELFTEST FAIL: checker missed", sorted(missing))
    else:
        print(f"  violation sample caught all 6 classes ({len(b)} hits)  OK")

    cf = run_contrast()
    if cf:
        ok = False
        print("SELFTEST FAIL: token contrast assertions failed:")
        for f in cf:
            print("   ", f)
    else:
        print(f"  {len(CONTRAST_ASSERTIONS)} token contrast assertions hold    OK")

    print("\nSELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1

# ----------------------------------------------------------------------- main

def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if argv[1] == "--selftest":
        return selftest()

    total = 0
    for path in argv[1:]:
        if not os.path.exists(path):
            print(f"{path}: not found")
            return 2
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        v = sorted(check(path, text))
        print(f"\n{path}")
        if not v:
            print("  clean — no violations")
        for line, kind, msg in v:
            print(f"  line {line:>4}  {kind:<7} {msg}")
        total += len(v)

    cf = run_contrast()
    print("\ntoken contrast:", "all assertions hold" if not cf else "FAILED")
    for f in cf:
        print("  ", f)
    total += len(cf)

    print(f"\n{'PASS' if total == 0 else f'FAIL — {total} violation(s)'}")
    return 0 if total == 0 else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
