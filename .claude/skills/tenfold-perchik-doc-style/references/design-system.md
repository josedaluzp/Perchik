# Design system — audited from the source PDF

Every value below was extracted directly from
`docs/Mapping 1065 CCH Axcess Tenfold Perchik v2.3.pdf` (53 pages, A4).
Treat this as the source of truth. **Do not invent colors or fonts** — if a
new need arises, pick the closest existing token.

## Page geometry

| Property | Value |
|----------|-------|
| Page size | A4 — 595.3 × 841.9 pt (210 × 297 mm) |
| Page furniture (footer, rules) left/right | ~31 pt (≈11 mm) |
| Main content column left edge | ~61 pt (content is inset ~30 pt past the furniture) |
| Footer baseline | ~815 pt from top (bottom ~14 mm margin) |

## Fonts

| Role | Family | Weights seen |
|------|--------|--------------|
| Display / body | **Archivo** | Regular 400, Semi-Bold 600, Bold 700, Heavy/Black 800–900, Oblique |
| Kickers / code / tables | **IBM Plex Mono** | Regular 400, Semi-Bold 600, Bold 700 |
| Fallback | DejaVu Sans / DejaVu Sans Mono | — |

Both primary families are open-source (Google Fonts). DejaVu fallback is a
WeasyPrint hallmark — the original was almost certainly HTML/CSS → WeasyPrint,
then written by `pypdf` (PDF producer string).

## Type scale (points, as measured)

| Element | Font | Size | Color |
|---------|------|------|-------|
| Hero title (cover) | Archivo Heavy (900) | 28 pt | `#1b262e` |
| Section title (H2) | Archivo Heavy (900) | 17.4 pt | `#1b262e` |
| Group label ("PARTE 1 —…") | Archivo Bold (700), uppercase | 10.7 pt | `#1f6f54` |
| Sub-head (H3) | Archivo Bold (700) | 11–12.6 pt | `#1b262e` |
| Card title | Archivo Heavy (900) | 10.3 pt | `#1b262e` (cream on green cards) |
| Body | Archivo Regular (400) | 9.6–10 pt | `#46555f` (ink `#1b262e` for emphasis) |
| Strong inline | Archivo Bold/Semi-Bold | 9.6 pt | `#1b262e` |
| Kicker / eyebrow | IBM Plex Mono Semi-Bold, uppercase, +letter-spacing | 7.4–8.1 pt | `#1f6f54` |
| Table header | IBM Plex Mono Semi-Bold, uppercase | 7.4 pt | `#46555f` |
| Inline code / paths | IBM Plex Mono | 8–8.3 pt | `#1b262e` (paths `#8a8578`) |
| Page footer | IBM Plex Mono | 6.5 pt | `#8a8578` |

## Color palette

| Token | Hex | Use |
|-------|-----|-----|
| Ink | `#1b262e` | headings, primary text, strong rules, dark cards |
| Slate | `#46555f` | secondary body text, table labels |
| Muted | `#8a8578` | monospace paths, captions, footer |
| Green | `#1f6f54` | eyebrows, section kickers, links, accent border, filled card bg |
| Rule (hairline) | `#d4dcd9` | card borders, table separators, thin rules |
| Surface | `#f5f7f6` | cards, neutral tags |
| Surface-2 | `#eef1f0` | callout background, table emphasis/zebra |
| White | `#ffffff` | base card background |
| Cream | `#f4f1ea` | text on deep-green surfaces |
| Cream-2 | `#d7eee2` | secondary text on deep-green surfaces |

## Badge / legend tokens

Pill, monospace Semi-Bold 7.4 pt, uppercase, letter-spacing ~0.1em, rounded 4px,
0.6pt border.

| Badge | Meaning | Text | Background | Border |
|-------|---------|------|-----------|--------|
| `AUTO` | dato directo, automatizable | `#1f6f54` | `#e4f1ea` | `#bcd9cb` |
| `REGLA` | automatizable con lógica condicional | `#2f5fa8` | `#e7eef9` | `#c3d3ee` |
| `MANUAL` | queda manual (criterio profesional) | `#b3641c` | `#faeede` | `#ecd0b3` |
| `CHECK` | verificación humana obligatoria | `#8d2f3c` | `#f8e9eb` | `#e6c3c9` |

Neutral source **tag** (e.g. `SS-4 (Dropbox)`, `Airtable / SS-4`): monospace
8 pt, text `#46555f`, background `#f5f7f6`, border `#d4dcd9`, rounded 4px.

## Components

- **Eyebrow / kicker** — mono uppercase green label above every title.
- **Scenario cards** — 3-up grid, white bg, hairline border, rounded 8px,
  eyebrow + Heavy title + small body. A "filled" variant uses deep-green bg
  `#1f6f54` with cream text (used for the terminal step / emphasis).
- **Process flow** — row of cards joined by mono `→` arrows; last card filled.
- **Callout** — surface-2 bg, 3px left green border, mono uppercase green title.
- **Table of contents** — `NN` number (mono, muted) + title (ink), hairline
  under each row, grouped under green "PARTE N —" labels.
- **Mapping table** — mono uppercase header with a strong bottom rule; rows
  separated by hairlines; first column is the ink-bold field name; source
  column uses neutral tags; rightmost column carries the status badge.
- **Cover footer block** — strong dark top rule, two columns (Proyecto left /
  Versión-Fecha right) with eyebrow + bold ink value.
- **Running page footer** — `TENFOLD × PERCHIK CPA` left; `MAPPING 1065 → CCH
  AXCESS · v2.3 · N/total` right, both mono 6.5 pt muted.

## Voice & language

Spanish, plain and direct ("en lenguaje simple"), second-person informal where
addressing the reader. Section titles are short and concrete. Document metadata:
title, author "Tenfold (Inforge) × Perchik CPA", subject describing the project.
