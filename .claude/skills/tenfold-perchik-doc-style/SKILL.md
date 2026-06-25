---
name: tenfold-perchik-doc-style
description: Use when creating a new document, report, or PDF that must match the Tenfold (Inforge) × Perchik CPA house style — the look, typography, colors, badges, and layout of the existing "Mapping 1065 CCH Axcess" functional design document. Use whenever asked for a new doc "in the same style/design/typography" as the project's PDF.
---

# Tenfold × Perchik CPA — Document Style

## Overview

The project ships one reference document: `docs/Mapping 1065 CCH Axcess Tenfold
Perchik v2.3.pdf`. This skill reproduces its house style for **new** documents
without touching the original. The style is built on two fonts (Archivo +
IBM Plex Mono), a fixed palette, a green accent, and a small component set
(cards, callouts, status badges, mapping tables).

**Never edit the source PDF.** Build new documents as separate files.

## How to build a new document

1. **Copy the assets** into your working folder (do not move the originals):
   `assets/style.css` and `assets/template.html`.
2. **Write content as HTML**, reusing the components in `template.html`. Keep
   `<link rel="stylesheet" href="style.css">` and wrap content in `.content`.
3. **Render to PDF**: `python scripts/build.py mydoc.html mydoc.pdf`
   (WeasyPrint preferred; falls back to Playwright/Chromium).
4. **Verify** against the checklist below.

## Quick reference (full audit in `references/design-system.md`)

| Token | Value |
|-------|-------|
| Page | A4, ~11 mm margins, content column inset |
| Fonts | Archivo (display/body), IBM Plex Mono (kickers/code/tables) |
| Ink / Slate / Muted | `#1b262e` / `#46555f` / `#8a8578` |
| Green accent | `#1f6f54` |
| Surfaces | card `#f5f7f6`, callout `#eef1f0`, rule `#d4dcd9` |
| Hero / Section title | Archivo Heavy 28 pt / 17.4 pt |
| Eyebrow & table head | IBM Plex Mono Semi-Bold, uppercase, letter-spaced |

**Status badges** (mono pills): `AUTO` green · `REGLA` blue · `MANUAL` amber ·
`CHECK` rose. Exact hex per badge is in the CSS and the reference.

**Components**: eyebrow/kicker, hero title, scenario cards (+ filled green
variant), process flow with `→` arrows, left-border callout, numbered TOC,
mapping table, two-column cover footer, running page footer. All are in
`assets/template.html`.

## Common mistakes

- **Inventing colors or fonts.** Use only the tokens in `style.css`. If a need
  isn't covered, pick the closest existing token — don't add new ones.
- **Dropping the eyebrow.** Every title is preceded by a mono uppercase green
  kicker; titles never stand alone.
- **Wrong font for code/labels.** Paths, tags, table headers, badges, and
  footers are always IBM Plex Mono — never Archivo.
- **Editing the original PDF.** Out of scope. Produce a new file only.
- **Skipping verification.** Render, open the PDF, and compare side-by-side
  with the source before declaring done.
