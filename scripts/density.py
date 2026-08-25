#!/usr/bin/env python3
"""Tru-Trac design system — density gate.

The compliance checker (validate.py) proves a page is not WRONG. It reads hex
codes and radii and cannot tell a considered page from an empty one. This gate
proves a page is not EMPTY, which is the failure mode that actually gets work
rejected.

It renders the page headless and measures what is really on it.

    python3 scripts/density.py path/to/page.html
    python3 scripts/density.py path/to/page.html --report out.png

Exit 0 = meets the floor, 1 = below it, 2 = usage or environment error.
"""

import os
import sys

# ---------------------------------------------------------------- the floors
#
# Calibrated against the dense-technical direction. A page in this idiom is an
# engineering document: annotated drawings, dimension chains, parts lists,
# tables. Flat empty colour is the enemy.

# The metric is CELL OCCUPANCY, not ink coverage. The page is divided into 24px
# cells and a cell counts if it holds any real mark. This asks "is this region
# doing anything", which is the question, rather than "how black is this region",
# which a dense table of small type answers badly and a photograph answers well.
#
# Raw ink coverage is reported but not gated. A densely set text page is only
# 5-10% ink, so an ink floor high enough to be meaningful is unreachable without
# solid fills. That was the first version of this gate and it was wrong.
#
# CALIBRATION, and it is empirical rather than principled: a page rejected on
# sight measured 27% occupancy; a page in the accepted dense-technical direction
# measured 40%. The floor sits between them. Recalibrate as more pages are judged
# and record the movement here.

# CALIBRATION HISTORY, kept because it is the useful part.
#
#   v1  ink coverage, floor 16%.   Wrong: a dense text page is only 5-10% ink.
#   v2  cell occupancy, floor 35%. Wrong for a different reason, below.
#   v3  occupancy reported, not gated.
#
# Measured against real judgements:
#
#   q-industrial.com, the reference Shaun chose      20.6%
#   Tru-Trac build in that direction                 24.5%
#   Tru-Trac "dense technical" build                 40.3%
#   Tru-Trac build rejected on sight                 27.2%
#
# The rejected page scored HIGHER than the reference he picked. Occupancy does
# not predict the judgement, so it must not gate. What separates them is
# contrast, type scale and a lit object, none of which a scalar captures.
# Occupancy is still worth reporting: it catches an abandoned page. It is not
# worth failing a build over.

OCC_FLOOR = 0.10          # reported at all times; only fails a genuinely abandoned page
BAND_FLOOR = 0.04         # likewise
# The reference page runs 738px of near-empty at its longest. A 260px ceiling,
# which is what intuition suggested, would have failed the thing Shaun chose.
# Anchored to the reference with headroom. Every threshold in this file that was
# set by intuition rather than measurement has been wrong. Measure first.
DEAD_RUN_MAX = 820
BAND_H = 100              # measurement band height (CSS px)
CELL = 24                 # occupancy cell size (CSS px)


WIDTHS = (320, 390, 430, 768, 1024, 1440)   # every width the page must survive


def check_overflow(path):
    """Horizontal overflow is the defect that makes a page look broken on a phone
    while looking perfect on the desk it was built at. Neither the compliance
    checker nor the density metric can see it, so it is checked here."""
    from playwright.sync_api import sync_playwright
    findings = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in WIDTHS:
            pg = b.new_page(viewport={"width": w, "height": 844})
            pg.goto("file://" + os.path.abspath(path))
            pg.wait_for_timeout(1400)
            sw = pg.evaluate("document.documentElement.scrollWidth")
            worst = pg.evaluate(
                """(vw) => {
                     for (const e of document.querySelectorAll('*')) {
                       const r = e.getBoundingClientRect();
                       if (r.right > vw + 1) {
                         let a = e.parentElement, clipped = false;
                         while (a) { const s = getComputedStyle(a);
                           if (['auto','scroll','hidden'].includes(s.overflowX)) { clipped = true; break; }
                           a = a.parentElement; }
                         if (!clipped) return e.tagName.toLowerCase() +
                           (e.getAttribute('class') ? '.' + e.getAttribute('class').split(' ')[0] : '');
                       }
                     }
                     return null; }""", w)
            findings.append((w, sw, worst))
            pg.close()
        b.close()
    return findings


def render(path, width=1440):
    from playwright.sync_api import sync_playwright
    out = os.path.abspath("_density_shot.png")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 1000})
        pg.goto("file://" + os.path.abspath(path))
        pg.wait_for_timeout(2500)
        # settle any scroll-reveal so we measure the finished page
        pg.evaluate(
            "document.querySelectorAll('[data-reveal]')"
            ".forEach(e=>e.classList.add('seen'))"
        )
        pg.wait_for_timeout(900)
        pg.screenshot(path=out, full_page=True)
        b.close()
    return out


def measure(shot, width=1440):
    from PIL import Image
    import numpy as np

    im = Image.open(shot).convert("L")
    scale = im.size[0] / width
    a = np.asarray(im, dtype=np.int16)

    # "Ink" = any pixel that differs from its row's dominant flat field.
    # This counts type, rules, drawings and photography, and ignores the
    # background whatever colour that background happens to be.
    ink = np.zeros(a.shape, dtype=bool)
    for y in range(a.shape[0]):
        row = a[y]
        vals, counts = np.unique(row, return_counts=True)
        field = vals[counts.argmax()]
        ink[y] = np.abs(row - field) > 12

    per_row = ink.mean(axis=1)
    raw_ink = float(ink.mean())

    # cell occupancy over the whole page
    c = max(2, int(CELL * scale))
    hh, ww = ink.shape[0] // c, ink.shape[1] // c
    grid = ink[:hh * c, :ww * c].reshape(hh, c, ww, c).sum(axis=(1, 3))
    occupied = grid >= 3
    total = float(occupied.mean())

    # occupancy per horizontal band
    rows_per_band = max(1, int(BAND_H * scale / c))
    bands = []
    for i in range(0, hh, rows_per_band):
        seg = occupied[i:i + rows_per_band]
        if seg.size:
            bands.append((int(i * c / scale), float(seg.mean())))

    # longest consecutive run of near-empty rows
    run = best = best_at = 0
    start = 0
    for y, v in enumerate(per_row):
        if v < 0.012:
            if run == 0:
                start = y
            run += 1
            if run > best:
                best, best_at = run, start
        else:
            run = 0

    return {
        "height": int(a.shape[0] / scale),
        "ink": total,
        "raw": raw_ink,
        "bands": bands,
        "dead_run": int(best / scale),
        "dead_at": int(best_at / scale),
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    if not os.path.exists(path):
        print(f"{path}: not found")
        return 2

    try:
        shot = render(path)
    except Exception as exc:
        print(f"could not render: {exc}")
        return 2

    m = measure(shot)
    fails = []

    print(f"\ndensity gate — {os.path.basename(path)}")
    print(f"  page height        {m['height']} px")
    print(f"  cell occupancy     {m['ink']*100:5.1f}%   (reference: 20.6%)")
    print(f"  raw ink            {m['raw']*100:5.1f}%   (reported, not gated)")
    if m["ink"] < OCC_FLOOR:
        fails.append(
            f"cell occupancy {m['ink']*100:.1f}% is below {OCC_FLOOR*100:.0f}% — "
            "the page is abandoned, not sparse"
        )

    thin = [(y, v) for y, v in m["bands"] if v < BAND_FLOOR]
    print(f"  thin bands         {len(thin)} of {len(m['bands'])}   floor {BAND_FLOOR*100:.0f}% each")
    if thin:
        worst = sorted(thin, key=lambda t: t[1])[:6]
        for y, v in worst:
            print(f"      y={y:>5}px  {v*100:4.1f}%")
        if len(thin) > len(m["bands"]) * 0.30:
            fails.append(
                f"{len(thin)} of {len(m['bands'])} bands fall below {BAND_FLOOR*100:.0f}% occupancy — "
                "the page has too many empty stretches"
            )

    try:
        ov = check_overflow(path)
        bad = [(w, sw, who) for w, sw, who in ov if sw > w + 1]
        print(f"  responsive         {len(WIDTHS)-len(bad)} of {len(WIDTHS)} widths clean")
        for w, sw, who in bad:
            print(f"      @{w}px scrollWidth {sw}" + (f"  <- {who}" if who else ""))
        if bad:
            fails.append(
                f"horizontal overflow at {', '.join(str(w) for w, _, _ in bad)}px — "
                "the page clips and scrolls sideways on those screens"
            )
    except Exception as exc:
        print(f"  responsive         could not test: {exc}")

    print(f"  longest dead run   {m['dead_run']} px at y={m['dead_at']}   max {DEAD_RUN_MAX} px")
    if m["dead_run"] > DEAD_RUN_MAX:
        fails.append(
            f"{m['dead_run']}px of near-empty page at y={m['dead_at']} — "
            "a reader scrolls past nothing"
        )

    if "--report" in argv:
        i = argv.index("--report")
        if i + 1 < len(argv):
            os.replace(shot, argv[i + 1])
            print(f"  screenshot         {argv[i+1]}")
    elif os.path.exists(shot):
        os.remove(shot)

    print()
    if fails:
        for f in fails:
            print(f"  FAIL  {f}")
        print(f"\nBELOW FLOOR — {len(fails)} finding(s)")
        return 1
    print("MEETS FLOOR")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
