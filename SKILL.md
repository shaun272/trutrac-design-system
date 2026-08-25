---
name: trutrac-design-system
description: >-
  The approved Tru-Trac design system for screen surfaces. Use for ANY Tru-Trac web page,
  landing page, microsite, HTML dashboard, interactive report, internal tool UI, product UI,
  app screen, email template, embedded widget, prototype, or Lovable/Figma/React build.
  Owns the colour tokens, type stack, spacing, radii, elevation rules, component library,
  logo usage and the dark-stage/light-catalogue section rhythm. Trigger on "build a page for",
  "make a dashboard", "design the site", "style this UI", "does this match our brand",
  "use our design system", "brand colours", "which red do we use", "put the logo on", or
  whenever producing any HTML, JSX, Vue or Svelte that a Tru-Trac audience will see.
  Also trigger when reviewing or auditing an existing screen for brand compliance.
  Boundary — this owns SCREEN. A4 print proposals belong to trutrac-proposals; the
  WeasyPrint print pipeline belongs to trutrac-dynamic-reporting; product motion and CGI
  belong to trutrac-motion-production. Colour and type here match those skills exactly.
---

# Tru-Trac design system (screen)

**v9 is authoritative.** Living spec in `system/system.html`. This system is built for
**documents first**: reports, dynamic HTML reports, PDF, proposals, technical documents, product
handbooks, presentations and web pages. Light is the primary surface because most of it prints;
dark is a mode. Built on a **12 column grid at a 24 px gutter over an 8 px baseline**, with a
modular type scale at ratio 1.25 from a 16 px base. Every leading in the scale resolves to a
whole number of baseline units. Toggle the grid overlay in the living spec to check registration
before shipping any page. Logo rules and the ten official assets are in `references/logo.md` — every component in every state, empty and error patterns, the UX copy
layer, motion patterns, and a named refusal list. Earlier token files are kept for the print and
document surfaces only. Open the living spec before building anything; it is the system, and the
prose below is commentary on it.

Version 1.0. Structure adapted from the Peloton reference style at
`styles.refero.design/style/355e8465-df7d-486a-9d76-2ace37d076a2`. Colour, type and logo are
Tru-Trac's own locked brand values. Where the reference and the Tru-Trac brand standard
disagreed, the brand standard won. Those decisions are recorded in
`references/provenance.md` and are not to be quietly reversed.

## The one-line description

A dark engineering stage cut by a single red. Deep charcoal full-bleed bands carry the
message and the call to action, then break into bright grey-white sections where the product,
the data and the specification do the talking.

## Load order

1. `system/system.html` — **the system.** Every component in every state, both modes, live.
   Open it before building anything; the prose below is commentary on it.
2. `tokens/tokens.css` — the single canonical token file, extracted from the living spec.
3. `references/components.md` — the API: variants, states, accessibility contract, do and don't.
4. `references/logo.md` — the ten official assets and which one goes on which surface.
5. `references/layout-and-imagery.md` — grid, page rhythm, the four imagery roles.
6. `references/provenance.md` — why values are what they are, and the two directions retired
   before this one. Read it before proposing a redesign.


## The rules that carry the system

**Colour.**
- `#E1261C` is the only chromatic colour in the system. It marks primary actions, the brand
  mark, and one focus series in a chart. Nothing else.
- Red never forms a headline, a section background, a full-width band, a table header band,
  or a field behind body copy. On any screen, red should read as punctuation.
- Every other value is a neutral drawn from the `#414042` ramp. Do not invent greys.
- Never sample a colour from the logo file. The raster contains `#e42526` and `#ed1c24`.
  Neither is the brand red. The token is `#E1261C` and it is the only correct value.

**Type.**
- Plus Jakarta Sans 600 for every heading and display line.
- Inter 400 for body copy, Inter 500 for nav links, buttons and UI labels.
- JetBrains Mono 500 for numerals, part codes, references and micro-labels only. Never a
  whole table body, never a caption, never a paragraph.
- Do not use weight 700 or 800 anywhere. Do not use a light display weight.

**Shape.**
- Three radii do almost all the work: 6px inputs, tags and in-card images; 24px cards;
  28px buttons. 999px is reserved for the floating support widget.
- Hero and evidence photography runs full-bleed with hard edges and no radius.
- No square 0px corners on interactive elements, no fully circular buttons.

**Elevation.**
- No drop shadows. Anywhere. Depth comes from surface contrast: stage against canvas,
  white card against canvas, hairline border at `#E3E3E3`.

**Rhythm.**
- Alternate full-bleed `#1D1C1E` stage bands with `#F7F7F7` content sections. A page with one
  dark band at the top and nothing else is not using the system.
- Content sections centre at 1200px max width. Stage bands span the viewport.
- Light sections carry 40px padding per side, so adjacent sections sit 80px apart. Stage bands
  carry 96px. Padding does not compound into 128px voids.
- Body copy never runs wider than 68ch, whatever the container.
- Never place a white card or light block on a stage band. Stage carries headline, supporting
  line, imagery and CTAs. Nothing else.
- Full sequence and grid derivatives in `references/layout-and-imagery.md`.

**Photography and icons.**
- Real plant and site photography. Product on white only inside product tiles.
- One tonal grade across a whole page. Mixed white balance between adjacent images is the
  clearest sign a page was assembled from whatever was on the drive.
- Icons are line-based, 1.5px stroke, single colour: white on stage, `#414042` on light.
  No filled multicolour icons, no illustration sets.

**Motion.**
- The 300deg shimmer gradient is for skeleton loading states only. Never decorative.

## Accessibility floor

Body text 4.5:1 minimum against its surface. Input borders and other non-text UI 3:1
minimum. Never carry a distinction on colour alone; add a label, a position or a shape.
`scripts/validate.py` checks these automatically. Run it.

## Verify before you hand anything over

Every screen this system produces gets checked before it leaves:

```bash
python3 scripts/selfcheck.py                    # the skill is sound and will load
python3 scripts/ds-audit.py  system/system.html   # token discipline, naming, completeness,
                                                #   and runtime resolution in a real browser

# Never hand-edit a token name. Renames touch the spec, the token file and the docs:
python3 scripts/rename-token.py --old focus --new accent-focus
python3 scripts/validate.py  path/to/page.html  # the page is not WRONG
python3 scripts/density.py   path/to/page.html  # the page is not EMPTY
```

`validate.py` fails on off-token colours, wrong radii, any drop shadow, wrong font family,
heading weights above 600, the wrong logo variant on a surface, and contrast below the floor.

`density.py` renders the page at six widths and fails on horizontal overflow, on a dead run
over 260px, or on a genuinely abandoned page. It reports cell occupancy but no longer gates on
it: the chosen reference measures 20.6% and a rejected page measured 27.2%, so occupancy does
not predict the judgement. The calibration history is in the script and is worth reading before
anyone adds a metric to this gate. **This is the gate that matters.** A page can
clear `validate.py` completely and still be rejected on sight, because a hex-code checker
cannot tell a considered page from an empty one. Both gates, every time.

## Anti-patterns

- A second accent colour "just for this one chart".
- A red hero band, or white text on a large red field.
- Card shadows added to "lift" a grid.
- The supplied logo dropped straight onto a dark surface. It is a knockout mark and the
  counterforms will fill with the background. Use the reverse asset.
- Body copy set in JetBrains Mono because it "looks technical". It reads as debug output.
- A 1200px content block stretched full width. The measure becomes unreadable.
