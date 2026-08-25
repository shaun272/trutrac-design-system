# Provenance

**Read this as history, not as instructions.** It records where values came from and which
directions were abandoned. The system in force is `system/system.html` and `tokens/tokens.css`.
Where this file and the token file disagree, the token file is correct and this file is a record
of a decision that has since moved.

Three directions were built. The first two were retired and are documented at the foot of this
file. The one in force is the third: a document system on **Archivo** and an **OKLCH** neutral
ramp. Everything in the next two sections was decided during the *first* direction, against the
Peloton reference, and several of those decisions no longer hold. They are kept because the
reasoning still explains the shape of the system, and each superseded value is marked.

## Open items, for Shaun

Two questions this file cannot settle. Both need a brand answer, not a documentation edit.

1. **Archivo or Plus Jakarta Sans.** The section below records Plus Jakarta Sans and Inter as
   "Tru-Trac's locked type standard", and states that the locked print standard sets cover
   titles at PJS 600. The system in force ships **Archivo** and no Inter. Either the locked
   standard moved to Archivo and that section is stale, or Archivo arrived with the retired
   cinematic direction and was never reconciled with print. Screen and print are currently on
   different faces, which is the exact fault the weight decision below was made to avoid.
2. **The neutral ramp and brand charcoal.** The section below says the ramp was rebuilt on
   `#414042`. The ramp in force is OKLCH at hue 285; brand charcoal `#414042` sits at hue 308,
   and no step on the ramp equals it. Changing the ramp restyles every surface, so it has not
   been touched. Either the ramp is re-cut on brand charcoal, or brand charcoal is accepted as
   the print and ink reference only and the screen ramp is documented as its own thing.

## Corrected, 25 August 2026

**Accent red. `--a-5` was `oklch(0.577 0.223 27.3)`, which resolves to `#df1c21`.**
That is not `#E1261C`. It is within a shade of `#df1c2f`, the reference red this system had
already rejected, so the rejected value appears to have survived a hand conversion into OKLCH
while the comment beside it still read "locked". Three documents and the token's own comment
declare `#E1261C` (Pantone 485C) as the locked brand red, so the token was corrected to
`oklch(0.5855 0.2205 29.14)`, which round-trips to `#E1261C` exactly. The `--a-*` ramp and every
accent alpha were rehued to match so the ramp does not kink at step 5. White on the corrected
accent is 4.67:1, still WCAG AA. `selfcheck.py` now resolves this token and fails if it ever
drifts off the brand value again.

## Source

Peloton style reference, `styles.refero.design/style/355e8465-df7d-486a-9d76-2ace37d076a2`,
retrieved 23 August 2026. Supplied by Shaun Blumberg as the reference for the Tru-Trac screen
design system, together with `Tru_Trac_Logo_Vector-01.png` as the approved mark.

## Taken from the reference unchanged

The structural system, which is the part worth having:

- Two-mode rhythm — full-bleed dark stage bands alternating with light content sections
- ~~4px spacing base; 64px section gap, 24px card padding, 12px element gap~~ **superseded:**
  the system in force is an 8px baseline. 1200px max width survives
- ~~Radius scale: 6px inputs and in-card images, 24px cards, 28px buttons, pill for one widget~~
  **superseded:** the system in force is `--r-1` 2px, `--r-2` 3px, `--r-3` 5px, and no pill
- Zero drop shadows; depth from surface contrast and a hairline border
- ~~Type scale steps 12, 14, 15, 16, 18, 20, 26, 32, 36, 48~~ **superseded:** the system in
  force is a 1.25 modular scale from 16px, 13 / 14 / 16 / 20 / 25 / 31 / 39 / 61, every leading
  a whole multiple of the 8px baseline
- Negative tracking on large sizes, positive tracking at 12px
- Single-accent discipline: exactly one chromatic colour in the whole system
- Line icons at 1.5px stroke, single colour
- Component set and its behaviour
- Shimmer gradient restricted to skeleton loading states
- The rule that a light card never sits on a dark hero

## Substituted, with reasons

**Accent red. `#df1c2f` replaced by `#E1261C`.**
`#E1261C` (Pantone 485C) is Tru-Trac's locked brand red, already carried by
`trutrac-proposals`, `trutrac-motion-production` and `asana-implementation`. Running a second
red on screen against that in print would put two brand reds in the business. The reference
red is not Tru-Trac's and has no claim on it.

**Dark surface. `#181a1d` replaced by `#1D1C1E`.**
The reference dark is slightly cool. `#1D1C1E` is brand grey `#414042` at a 55% shade, so the
stage sits in the same neutral family as everything else in the system. Declared as a neutral
shade, not a brand colour.

**Neutral ramp rebuilt on `#414042`.** *(Superseded. See open item 2.)*
The reference ships ten loosely related greys, several of which duplicate each other
(`#a3a3a6` and `#a8acb1` differ by an amount nobody can see) and two of which its own
documentation labels "do not promote to primary CTA", which is a note about a colour that was
never a candidate. The Tru-Trac ramp is six deliberate steps computed as tints and shades of
`#414042`, each with one job.

**Type stack. Inter-only replaced by Plus Jakarta Sans, Inter and JetBrains Mono.**
Tru-Trac's locked type standard. Inter is retained as the body and UI face, so the reference's
typographic texture largely survives.

> **Superseded and unreconciled.** The system in force ships Archivo and JetBrains Mono, with no
> Plus Jakarta Sans and no Inter. See open item 1 at the top of this file. This is the one
> substitution in this section that was never carried through to the shipped tokens.

**Display weight. Weight 300 replaced by weight 600.** *(Partly superseded: 600 is the heading
ceiling in force, but weights 200 and 300 are used for the KPI figure and the pull quote.)*
This is the reference's signature move and the one I most deliberately dropped. A whisper-light
48px display is a fashion and fitness-retail gesture. Tru-Trac sells conveyor tracking into
mines and processing plants, and its locked print standard sets cover titles at PJS 600.
A light display would put screen and print visibly out of step.

## Defect found in the source, resolved

The reference contradicts itself on whether its red is the primary CTA colour. Its token
table says "do not promote it to the primary CTA color" and its agent guide says "primary
action: no distinct CTA color", while its Do list says "use it exclusively for primary
actions" and every one of its component specs uses it as the CTA fill. Resolved in favour of
the component specs and the Do list: the accent is the primary CTA colour. The contrary lines
appear to be boilerplate the generator emitted for every colour in the palette.

## Defect found in the logo, resolved

The supplied PNG is a knockout mark with transparent counterforms, so it fails on the dark
stage band and nav bar that this system is built around. A reverse asset was generated. See
`logo.md`.

## Standing conflict, not resolved here

`trutrac-proposals/references/design-standard.md` requires hard edges on all photography, no
rounded corners. The reference puts a 6px radius on images. Split by role: hero and evidence
photography runs full-bleed with hard edges, matching print; product and UI crops inside a
card carry the 6px radius, matching the reference. If that split is unwelcome, the print rule
should win and `--r-2` should stop applying to images.

**Resolved, 25 August 2026.** The print rule won by default: the spec applies no radius to
`.box.product`, so no image in the system carries one. `layout-and-imagery.md` claimed a 6px
radius on product crops and has been corrected.

## Reference base

One reference URL, not the three to five that were to inform this system. Structure taken from
a single source is structure with one point of view. If further references arrive and disagree
with this on rhythm, radii or spacing, this file is where the argument gets settled.


---

# Directions tried and retired

Two full art directions were built, shipped and abandoned before the document system landed.
Both are recorded here because the reasoning still constrains the current one, and because
someone will otherwise propose them again.

## Dense technical, retired 24 August 2026

The page as a drawing sheet: balloon callouts keyed to parts lists, dimension chains, sheet
furniture, four line weights. Built on the premise that density signals engineering rigour.

**Why it was wrong.** The reference Shaun then supplied measured 20.6 percent cell occupancy;
the build he had already rejected measured 27.2 percent. The rejected page was *denser* than the
chosen reference. Density never correlated with the judgement.

**What survived.** The drawing-sheet apparatus is right for datasheets and catalogues, and the
admonition, specification-list and revision-block components came from it directly.

## Cinematic dark, retired 24 August 2026

Near-black ground, off-white ink, display type at weight 200, a rim-lit WebGL product object
carrying the page. Derived from q-industrial.com by measuring its computed tokens.

**Why it was retired.** Not because it was wrong, but because the brief changed. The system is
for documents, reports, proposals, handbooks and presentations. Most of that prints. A
near-black marketing surface is the wrong primary for a system whose main output is A4.

**What survived.** Dark mode, the OKLCH neutral ramp, weight falling as size rises, the ban on
pure white on dark, and the one-accent discipline.

## The rule both taught

Every scalar threshold invented by intuition in this project has been wrong: an ink-coverage
floor, a cell-occupancy floor, a dead-run ceiling. Each failed against a real judgement.
Measure a reference before setting a number, and write the calibration into the script.
