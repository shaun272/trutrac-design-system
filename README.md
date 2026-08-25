# Tru-Trac design system

The approved design system for Tru-Trac reports, dynamic HTML reports, proposals, technical
documents, handbooks, presentations and web pages. Light is the primary surface because most of
this prints. Dark is a mode.

**`system/system.html` is the system.** Open it first. Every component in every state, both
modes, live, with a grid overlay. Everything else here is commentary on it.

## Layout

| Path | What it is |
|---|---|
| `SKILL.md` | The agent entry point. A summary of the rules, plus where to fetch the rest. |
| `system/system.html` | The living spec. Authoritative. |
| `tokens/tokens.css` | The canonical token file. Identical to the spec's inline block, 105 tokens. |
| `references/components.md` | The component API: variants, states, accessibility contract. |
| `references/logo.md` | The ten official assets and which one goes on which surface. |
| `references/layout-and-imagery.md` | Page sequence, grid derivatives, the four imagery roles. |
| `references/provenance.md` | Why values are what they are, what was retired, and the open items. |
| `scripts/` | The gates. See below. |
| `assets/` | Ten logo assets, plus stock placeholder photography to be replaced. |

## Verify

One command runs everything:

```bash
python3 scripts/verify.py                    # the system itself
python3 scripts/verify.py path/to/page.html  # the system, then your page
```

It runs three gates:

- **`selfcheck.py`** proves the skill loads and that nothing contradicts anything else. It
  resolves OKLCH tokens to hex and fails if the accent drifts off the locked brand red, checks
  token parity between the spec and the token file, and fails if a document annotates a token
  with a value the token file disagrees with.
- **`ds-audit.py`** scores token discipline, naming and component completeness, resolving every
  variable in a real browser.
- **`density.py`** renders a page at six widths and fails on overflow or on a page that was
  abandoned rather than finished. **This is the gate that matters.** A page can be perfectly
  token-clean and still be rejected on sight.

Renaming a token touches the spec, the token file and the docs at once. Never do it by hand:

```bash
python3 scripts/rename-token.py --old focus --new accent-focus
```

## Open items

Two brand questions are recorded at the top of `references/provenance.md` and are not settled:
the type stack (the system ships Archivo, provenance records Plus Jakarta Sans as the locked
standard), and whether the OKLCH neutral ramp should be re-cut on brand charcoal `#414042`.

## Requirements

Python 3 for the gates. `ds-audit.py` and `density.py` drive a headless browser through
Playwright; `pip install playwright && playwright install chromium` if they report it missing.
`selfcheck.py` has no dependencies at all and runs anywhere.
