---
name: trutrac-design-system
description: >-
  The approved Tru-Trac design system. Use for any Tru-Trac surface built from these tokens: web
  page, landing page, HTML dashboard, dynamic or interactive report, internal tool UI, app screen,
  email template, embedded widget, prototype, Lovable/Figma/React build, and the A4 sheet and 16:9
  slide objects rendered from the same token file. Owns the colour tokens, type stack, spacing,
  radii, elevation rules, the twelve-component library, logo usage and the stage/canvas section
  rhythm. Use when the request says "build a page for", "make a dashboard", "style this UI", "does
  this match our brand", "use our design system", "which red do we use", "put the logo on", or
  whenever producing HTML, JSX, Vue or Svelte a Tru-Trac audience will see. Also use when auditing
  an existing screen or document for brand compliance. Boundary: the WeasyPrint pipeline belongs
  to trutrac-dynamic-reporting, A4 proposals to trutrac-proposals, product motion to trutrac-
  motion-production. All three use these tokens.
---

# Tru-Trac design system

**Version 1.0.** The system is `system/system.html`. Everything else in this repo, this file
included, is commentary on it.

Built for documents first: reports, dynamic HTML reports, proposals, technical documents,
handbooks, presentations and web pages. Light is the primary surface because most of this
prints. Dark is a mode.

12 column grid at a 24px gutter over an 8px baseline. Modular type scale at ratio 1.25 from a
16px base, every leading resolving to a whole number of baseline units. Toggle the grid overlay
in the living spec to check registration before shipping.

## Precedence

`tokens/tokens.css` and `system/system.html` are the ground truth and they are kept identical,
105 tokens, same values. Where a reference document disagrees with the token file, **the token
file wins** and the reference document is the thing that needs fixing. Never resolve a conflict
by editing a component.

## Where these files are

**The installed skill is this file alone.** Everything it points at lives in the public repo:

**https://github.com/shaun272/trutrac-design-system**

If `system/system.html`, `tokens/tokens.css` or the `references/` documents are not on disk
beside this file, fetch them before building anything. Raw paths:

```
.../raw/main/system/system.html
.../raw/main/tokens/tokens.css
.../raw/main/references/components.md
.../raw/main/references/logo.md
.../raw/main/references/layout-and-imagery.md
.../raw/main/references/provenance.md
```

Full form, for the token file as the example:
`https://raw.githubusercontent.com/shaun272/trutrac-design-system/main/tokens/tokens.css`

The ten logo assets and the verification scripts are in the same repo. If you are building more
than one page, clone it rather than fetching file by file:

```bash
git clone https://github.com/shaun272/trutrac-design-system.git
```

**Do not build from this file alone.** What follows is a summary. The spec carries every
component in every state, both modes, and the exact token values. A page built from the summary
will be approximately right, which for a design system is the same as wrong.

## Load order

1. `system/system.html` - the system. Every component in every state, both modes, live.
   Open it before building anything. Fetch it from the repo if it is not on disk.
2. `tokens/tokens.css` - the single canonical token file, identical to the spec's inline block.
   Fetch it from the repo if it is not on disk.
3. `references/components.md` - the API: variants, states, accessibility contract, do and don't.
4. `references/logo.md` - the ten official assets and which one goes on which surface.
5. `references/layout-and-imagery.md` - page sequence, grid derivatives, the four imagery roles.
6. `references/provenance.md` - why values are what they are. Read it before proposing a
   redesign. It records decisions taken against an earlier direction, so read it as history.

## The rules that carry the system

**Colour.**
- `--accent` is `#E1261C` (Pantone 485C), declared as `--a-5`, which resolves to that hex
  exactly. It is the only decorative
  chromatic colour in the system. It marks primary actions, the brand mark, and one focus
  series in a chart. Nothing else.
- Red never forms a headline, a section background, a full-width band, a table header band,
  or a field behind body copy. Red reads as punctuation.
- `--status-ok`, `--status-warn` and `--status-info` are the one exception. They are semantic
  only: they carry state in an admonition, a validation message or a delta. They never
  decorate, never theme a section, and never appear as a chart series colour.
- Every other value is a neutral from the `--n-0` to `--n-11` ramp. Do not invent greys and do
  not write a raw `oklch()` in a component.
- Never sample a colour from the logo file. The rasters carry `#e42526` and `#e32726`, and
  `#3a3a3c` for charcoal. None of those is the brand value.

**Type.**
- `--font-sans` is **Archivo**, a variable face loaded at `wdth 75..125, wght 100..900`.
- `--font-mono` is **JetBrains Mono** for numerals, part codes, references and micro-labels
  only. Never a whole table body, never a caption, never a paragraph.
- Weight 600 for headings and display lines, 500 for nav links, buttons and UI labels, 400 for
  body copy. **600 is the ceiling. Never 700 or 800.**
- Weights 300 and 200 are reserved for two jobs only: the large KPI figure and the pull quote.
  Never for body copy, never for a heading.
- The scale is named by role (`--f-body`, `--l-h2`); spacing is named by number (`--s-4`).
  That asymmetry is deliberate. Do not "fix" one to match the other.

**Shape.**
- Three radii: `--r-1` 2px, `--r-2` 3px, `--r-3` 5px. This is a near-square system and it is
  meant to be. Do not soften it.
- Hero and evidence photography runs full-bleed with hard edges and no radius.
- The only circle in the system is the loading spinner. The checkbox is `--r-1`.

**Elevation.**
- No drop shadows. Anywhere. Depth comes from surface contrast: `--page` against `--panel`,
  and the `--rule-1` to `--rule-4` hairline ramp.
- The one permitted `box-shadow` is a focus ring at zero offset and zero blur. A ring cannot
  cast, it can only surround.

**Rhythm.**
- Alternate full-bleed stage bands with light content sections. A page with one dark band at
  the top and nothing else is not using the system.
- Content sections centre at 1200px max width. Stage bands span the viewport.
- Light sections carry `--s-10` (40px) per side, so adjacent sections sit 80px apart. Stage
  bands carry `--s-24` (96px). Padding does not compound into 128px voids.
- Body copy never runs wider than `--layout-measure` (66ch), whatever the container.
- Never place a white card or light block on a stage band.
- Full sequence and grid derivatives in `references/layout-and-imagery.md`.

**Modes and paper.**
- Light is `:root`. Dark is `[data-mode="dark"]` and re-points the semantic layer only.
- Primitives never flip. `--paper-*` tokens never flip either: a sheet is paper whether you are
  reading it on a dark screen or not. The Sheet and Slide components sit on `--paper-*`.

**Photography and icons.**
- Real plant and site photography. Product on white only inside product tiles.
- One tonal grade across a whole page. Mixed white balance between adjacent images is the
  clearest sign a page was assembled from whatever was on the drive.
- Icons are Phosphor, line-based, single colour. No filled multicolour icons, no illustration
  sets.

**Motion.**
- `--t-press` 110ms, `--t-ui` 180ms, `--t-panel` 280ms, on `--ease-out` or `--ease-spring`.
- Focus never animates. It is keyboard-initiated and must appear instantly.
- The shimmer gradient is for skeleton loading states only. Never decorative.

## Accessibility floor

Body text 4.5:1 minimum against its surface. Input borders and other non-text UI 3:1 minimum.
Minimum target 44px via `--layout-tap`. Never carry a distinction on colour alone; add a label,
a position or a shape.

## Verify before you hand anything over

```bash
python3 scripts/selfcheck.py                     # the skill is sound and will load
python3 scripts/ds-audit.py system/system.html   # token discipline, naming, completeness,
                                                 #   runtime resolution in a real browser
python3 scripts/density.py path/to/page.html     # the page is not EMPTY

# Never hand-edit a token name. Renames touch the spec, the token file and the docs:
python3 scripts/rename-token.py --old focus --new accent-focus
```

`density.py` renders at six widths and fails on horizontal overflow, on a dead run over
`DEAD_RUN_MAX`, or on a genuinely abandoned page. It reports cell occupancy but does not gate on
it: the chosen reference measures 20.6% and a rejected page measured 27.2%, so occupancy does
not predict the judgement. The calibration history is in the script and is worth reading before
anyone adds a metric to this gate. **This is the gate that matters.** A page can be perfectly
token-clean and still be rejected on sight, because no static checker can tell a considered page
from an empty one.

There is no hex-and-pixel compliance checker. One existed, it could not read `oklch()` or
resolve `var()`, so it passed everything including a violet accent and a 1.3:1 button, and it
was removed. `ds-audit.py` is the token-discipline gate. If you want a colour rule enforced,
add it there where the values can actually be resolved.

## Anti-patterns

- A second accent colour "just for this one chart".
- A status colour used to theme a section or brighten a layout.
- A red hero band, or white text on a large red field.
- Card shadows added to "lift" a grid.
- Softening the radii because 2px "looks unfinished".
- The supplied logo dropped straight onto a dark surface. It is a knockout mark and the
  counterforms will fill with the background. Use the reverse asset.
- Body copy set in JetBrains Mono because it "looks technical". It reads as debug output.
- A 1200px content block stretched full width. The measure becomes unreadable.
