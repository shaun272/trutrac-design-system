# Layout and imagery

The token file tells you what colour a thing is. This file tells you what goes on the page and
in what order, which is the part that decides whether the result looks designed or looks like a
component gallery.

## The page is a sequence, not a stack of grids

A page built from this system alternates between two states. The stage band is where the
argument is made and where imagery carries the weight. The light section is where the detail
lives. If four sections in a row are a heading over a uniform grid, the page has no rhythm and
no amount of correct tokens will save it.

A working sequence, in order:

1. **Nav** — stage. Reverse logo, links, utilities right.
2. **Stage hero** — asymmetric. Text left at roughly 45% of the width, imagery right. Not
   centred. Centred hero text with nothing beside it is the default that reads as a template.
3. **Transition strip** — `--panel`, one row of mono figures. It bridges the dark
   band into the light section instead of dropping straight from charcoal to near-white.
4. **Two-column block** — text and a diagram. Establishes the problem before the product.
5. **Product grid** — three or four cards, each with a real image slot at 4:3.
6. **Stage evidence band** — full bleed. One pull statement, one focus figure in red, one
   photograph or condition pair. This is the mid-page pause.
7. **Specification table** — designed, mono numerals, zebra at `--page-tint`.
8. **Close and form** — two columns. Form left, supporting proof right. A form field alone in
   a 1200px row is a defect.
9. **Footer** — stage.

Not every page needs all nine. Every page needs at least one stage band that is not the hero,
and at least one section that is not a grid.

## Rhythm

- Light section padding is `--s-20` (40px) per side, so adjacent sections sit 80px
  apart. Do not add 64px per side and create a 128px void.
- Stage bands carry `--s-24` (96px) per side. They are the pauses.
- Body copy never exceeds `--layout-measure` (68ch) regardless of container width.
- A section whose bottom third is empty is unfinished. Either the content is thin or the
  section should not exist.

## Grid

12 columns at `--s-6` (24px). The useful derivatives:

| Use | Columns |
|---|---|
| Hero text / hero image | 1–5 / 7–12 |
| Two-column text + diagram | 1–6 / 8–12 |
| Product grid | 3 × 4, or 4 × 3 |
| Table, full width | 1–12 |
| Form + proof | 1–5 / 7–12 |

## Imagery — the layer that decides the result

Every image slot on a Tru-Trac screen is one of four kinds. Nothing else goes in a slot.

| Kind | What it proves | Ratio | Treatment |
|---|---|---|---|
| **Site** | We work in plants like yours | `16 / 9` | Full bleed, hard edges, no radius. Low-key grade on stage bands. `--photo-scrim` under any text |
| **Product** | Here is the equipment | `4 / 3` | Neutral ground, 6px radius, inside a card only |
| **Condition** | Here is before and after | `3 / 2` | Matched framing, unretouched, dated, presented as a pair |
| **Technical** | Here is the geometry | free | Line drawing, `1.5px` stroke, `currentColor`, no fills except a 0.10 tint for material |

**One tonal grade across the whole page.** Mixed white balance between adjacent photographs is
the clearest sign a page was assembled from whatever was on the drive.

**Never use the logo as a stand-in for a product image.** It is the single fastest way to make
a finished page look unfinished.

## Technical drawings

When photography is not available or not cleared, a line drawing is the correct answer and it
is on-brand for an engineering company. It is not a fallback, it is the Precision role.

Rules: single stroke weight at `1.5px`, `currentColor` so the drawing inverts
correctly between stage and canvas, no gradients, no fills except a low-opacity tint for bulk
material. Dimension lines carry a mono label. One element may be red where it is the component
under discussion. Everything else is neutral.

Draw the thing an engineer would draw: an orthographic cross-section or a front elevation, with
the structure, the centre line and the dimension that matters.

## Interaction states

Every interactive element declares four states. A component with only a default state is not
finished.

| State | Treatment |
|---|---|
| Hover | Primary fill to `--accent-hover`. Ghost gains a 6% `currentColor` fill. Card border to `--ink-3`. 120ms ease |
| Focus | 3px `--accent-tint` outline, 2px offset. Never removed, never replaced with a colour change alone |
| Active | Fill darkens a further step. No transform, no scale bounce |
| Disabled | `--rule-2` fill, `--ink-3` text, cursor not-allowed. No opacity fade on text |

## Responsive

| Breakpoint | Change |
|---|---|
| ≥1024px | Full grid. `--f-ttl` on the hero |
| <1024px | Three columns to two. Hero drops to `--f-h1`. Hero image below text |
| <640px | Single column. Hero to `--f-h2`. Bands to 64px. Nav collapses. Buttons full width |

Test at 390, 768 and 1440. A page proven at one width is not proven.
