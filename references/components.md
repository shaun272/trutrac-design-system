# Components

Twelve components. Every one is live in `system/system.html`; this file is the API, the states
and the accessibility contract. If a behaviour is not written down here, it is not part of the
system and you should not rely on it.

Every value below is a token from `tokens/tokens.css`. If you find yourself typing a hex or a
pixel value that is not in that file, stop.

---

## Button

The only element that performs an action. One primary per view; everything else is secondary.

**Variants**

| Variant | Use when |
|---|---|
| `.btn-1` primary | The single action the page exists for |
| `.btn-2` secondary | Supporting actions. Sits beside a primary, never alone as the only action |

**States**

| State | Visual | Behaviour |
|---|---|---|
| Default | `--accent` fill, `--paper-inv` label | — |
| Hover | Fill to `--accent-hover` over 180ms | — |
| Active | `scale(.975)` over 110ms | Tactile only, no state change |
| Focus | 2px `--accent-focus` outline, 3px offset, **no transition** | Focus is keyboard-initiated and never animates |
| Disabled | `--panel` fill, `--ink-4` label, `cursor:not-allowed` | Non-interactive. Carries the `disabled` attribute, not just the class |
| Working | Label goes transparent, spinner in `--spinner-track` | `pointer-events:none` while running |

**Accessibility** — Role `button`. Enter and Space activate. Minimum target 44 × 44 via
`min-height:var(--layout-tap)`. A working button must keep its accessible name; never swap the
label for a spinner.

| Do | Don't |
|---|---|
| Label as verb plus object: "Request assessment" | "Submit", "OK", "Click here" |
| One primary per view | Two primaries competing |
| Name the object in a destructive label: "Remove flight CV-04" | "Are you sure?" with OK and Cancel |

```html
<button class="btn btn-1">Request assessment</button>
<button class="btn btn-2" disabled>Download manual</button>
<button class="btn btn-1 busy">Sending</button>
```

---

## Input

**States** — default, hover (`--ink-4` border), focus (`--accent-focus` border plus 3px
`--accent-tint` ring, no transition), disabled, **read-only**, error.

Read-only and disabled are different and they look different. Read-only content is still yours
and uses a dashed border on `--page-tint`. Disabled content is not yours to change and uses a
solid `--panel` fill.

**Accessibility** — Every field carries a visible `<label>`, never a placeholder as the label.
Errors use `aria-invalid="true"`, `aria-describedby` pointing at the message, and the message
carries `role="alert"`. Required fields mark with a `.req` asterisk that is `aria-hidden`, since
`required` already announces.

| Do | Don't |
|---|---|
| "Enter drift in millimetres, for example 34" | "Invalid input" |
| Validate on blur | Validate on every keystroke |
| Persistent helper text below the field | Helper text only in a placeholder |

```html
<div class="f">
  <label for="d">Measured drift <span class="req" aria-hidden="true">*</span></label>
  <input class="in bad" id="d" aria-invalid="true" aria-describedby="de" required>
  <span class="hlp bad" id="de" role="alert"><i class="ph ph-warning-circle"></i>Enter drift in millimetres, for example 34</span>
</div>
```

---

## Checkbox

19px box, `--rule-3` border, fills `--accent` when checked. The tick draws in over 150ms with a
`--ease-spring` scale. Label and box together form a 44px target.

**Accessibility** — A real `<input type="checkbox">` visually hidden behind the styled box, so
the native role, state and keyboard behaviour survive. Focus ring sits on the box via
`:focus-visible + .bx`.

---

## Data table

**Structure** — `caption` names the table, `thead` is sticky under the bar, `tfoot` carries
totals above a `--rule-4` rule. Even rows tint to `--page-tint`. Rows hover to `--hover`.

**Sorting** — Sortable columns wrap the header in a `.sortbtn` and the `th` carries `aria-sort`
of `ascending`, `descending` or `none`. The icon reflects state; colour alone never carries it.

**Accessibility** — Numeric columns right-align and use `font-variant-numeric:tabular-nums` so
figures line up and never shift. Wrap wide tables in `.tw` so they scroll rather than blowing
the viewport.

| Do | Don't |
|---|---|
| Right-align numbers, left-align text | Centre-align a data column |
| Tabular figures everywhere numeric | Proportional figures in a column |

---

## Tabs

Peer content of equal weight. Anything sequential belongs in numbered sections, not tabs.

**Accessibility** — `role="tablist"` with `aria-label`, each tab `role="tab"` with
`aria-selected`, panel `role="tabpanel"` with `aria-labelledby`. Roving `tabindex`: the selected
tab is 0, the rest are −1. Arrow keys move, Home and End jump to the ends. The 2px `--accent`
ink bar slides over 280ms.

---

## Admonition

| Variant | Use when |
|---|---|
| `.note` | Context that helps but is not required |
| `.caution` | Damage to equipment if ignored |
| `.warning` | Injury if ignored |

Full border, never a coloured left stripe. Each carries an icon **and** a word, so the meaning
never rests on hue. Label is uppercase and short; the body is sentence case.

---

## Empty state

Three parts, always all three: what this is, why it is empty, how to start. Dashed
`--rule-3` border on `--page-tint` so it reads as a placeholder rather than a card.

| Do | Don't |
|---|---|
| "No flights assessed yet. Assessments appear once an engineer has walked a flight" | "No data available" |
| Give the action that fills it | Leave the user at a dead end |

---

## Sheet

The A4 page object: cover, section opener, data page. Carries a running head with the mark and
document reference, and a folio with the entity and page number, because these documents
circulate detached from their covers.

Sheets use the `--paper-*` tokens and **do not flip in dark mode**. A sheet is paper whether you
are reading it on a dark screen or not.

---

## Slide

Four masters: title, content, single figure, section divider. 16:9. Anything that will not fit
one of them belongs in a document, not a deck. Also on `--paper-*`.

---

## KPI

Figure at 38px weight 200, label beneath, then a delta carrying an icon and an explicit word.
"Up 4 points on prior period", never an arrow glyph and a colour.

---

## Table of contents

Number, title, leader dots, page. The dots are a `--rule-3` dotted border on a flexing span, so
they fill whatever space is left. Rows hover to `--hover` and the whole row is the target.

---

## Pull quote

Framed top and bottom with `--rule-4` at 1.5px, `--f-h3` at weight 300, attribution in mono
beneath. One per document section at most.

---

## Editorial support

**Margin note** — `.sidenote` in a 200px column beside the measure, label in `--accent`.
**Footnotes** — mono superscript in `--accent`, list beneath a `--rule-1` rule.
**Page break marker** — dashed rule with a centred mono label, for drafts only.
**Specification block** — mono on `--panel`, for machine-readable extracts.
