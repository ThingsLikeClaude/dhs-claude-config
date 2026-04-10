---
name: stalab-ppt
description: >
  STALAB corporate presentation generator. Produces single-file HTML presentations
  with 1920x1080 fixed design, persistent header/footer, fragment animations,
  CSS-only charts, Mermaid diagrams, and 4 layout modes.
  Triggers: "STALAB presentation", "stalab ppt", "make stalab slides",
  "STALAB 발표자료", "스타랩 프레젠테이션", "스타랩 PPT"
---

# STALAB PPT

Generate STALAB-branded single-file HTML presentations.

## Reference Files (On-demand Read)

| File | Purpose | When to Read |
|------|---------|-------------|
| `references/slide-template.html` | Template source (copy base) | Step 3: HTML generation |
| `references/layouts-core.md` | 8 core layouts + content limits | Step 3: Slide markup |
| `references/layouts-extended.md` | 16 extended layouts | Step 3: Extended layouts |
| `references/svg-templates.md` | 4 SVG diagram templates | Step 3: Diagram slides |
| `references/decision.md` | Layout selection decision tree | Step 2: Outline design |
| `references/chunk.md` | Chunked generation workflow | Step 1: If >10 slides |
| `references/research.md` | Research phase workflow | Step 0: Topic-only input |

## Architecture

```
.deck (viewport — 100vw x 100dvh)
  ├── #gridCanvas (cover-only interactive grid)
  └── .slides (1920x1080 fixed, transform:scale — Math.max fills screen)
        ├── .slides::before (24px grid background)
        ├── .persistent-header (logo + topic)
        ├── .slide-area (slide transition zone)
        │     └── section.slide ...
        └── .persistent-footer (copyright + page number)
```

Scaling: `Math.max(vw/1920, vh/1080)` — fills screen edge-to-edge.

## Layout Modes (4)

| Mode | Class | Best For |
|------|-------|----------|
| **Centered** (default) | `.slide--light` | Bullets, cards, charts, KPIs |
| **Wide** | `.slide--wide` | Data tables, full-width content |
| **Split** | `.slide--split` | Image+text, before/after |
| **Editorial** | `.slide--editorial` | Statement slides, storytelling |

## Keyboard Controls

| Key | Action |
|-----|--------|
| `←→` `Space` `PageUp/Down` | Navigate slides |
| `F` | Fullscreen toggle |
| `Ctrl+Shift+F` | Chapter navigation (2-level drill-down) |
| `S` | Speaker notes popup window |
| `Escape` | Close nav / exit fullscreen |
| Mouse wheel | Navigate (400ms debounce) |

## Color System (CSS Custom Properties)

All colors use `:root` variables — override them to re-brand:

| Variable | Default | Usage |
|----------|---------|-------|
| `--c-primary` | `#2d2d8e` | Logo, charts, accents |
| `--c-heading` | `#1a1a2e` | Headings, code bg |
| `--c-body` | `#444` | Body text |
| `--c-bg` | `#f0f0f0` | Background |
| `--c-card` | `#fff` | Card backgrounds |
| `--c-border` | `#e0e0e0` | Borders |
| `--c-positive` | `#059669` | KPI increase |
| `--c-negative` | `#e11d48` | KPI decrease |

## Slide Types (24 total)

**Core 8:** Cover, Text, Two-Column, Card Grid, Chart (Bar/Line), KPI, Code Block, Image/SVG
**Extended 16:** Timeline, Step-by-Step, Funnel, Cycle, Roadmap, Before/After, Pros/Cons, Comparison Matrix, Data Table, Icon Grid, Bento Grid, Quote, Section Divider, Pyramid, Agenda/TOC, Venn
**Extended Charts (9):** Donut, Gauge, Progress List, Waterfall, Area, Heatmap, Sparkline, Treemap, Radar

## Features

- **Fragment system**: 6 animations (fade-up/down/left/right, zoom-in, blur-in) with auto-stagger
- **Chart animations**: Entry animations triggered on slide activation (11 chart types)
- **Prism.js**: Conditional CDN for syntax-highlighted code blocks (JS/TS/Python/Bash)
- **Mermaid.js**: Conditional CDN for auto-rendered diagrams with STALAB theme colors
- **Speaker notes**: Popup window (`S` key) with current notes + next slide preview
- **PDF export**: `@media print` CSS — `Ctrl+P` for landscape PDF
- **KPI counters**: Animated count-up with IntersectionObserver

## Workflow

### Step 0 — Research (topic-only input)
Read `references/research.md`. Use web search to gather data for the topic.

### Step 1 — Analyze Input
- Determine slide count: 5min→10, 10min→15, 15min→22, 20min→28, 30min→35
- If >10 slides: Read `references/chunk.md` for chunked generation
- Detect language from user conversation

### Step 2 — Design Outline
Read `references/decision.md`. Create slide-by-slide outline:
- Slide number, layout type, title, key content, fragment steps
- Present to user for approval before generating

### Step 3 — Generate HTML
1. Read `references/slide-template.html` — copy as base
2. Read `references/layouts-core.md` (always) + `layouts-extended.md` (if needed)
3. Replace demo slides with user content
4. Keep: header/footer, navigation JS, grid canvas, fragment system, chart animations
5. Customize: header text, footer copyright, cover title/subtitle
6. Add `data-notes="..."` on each slide for speaker notes
7. Include Prism.js CDN only if code blocks exist
8. Include Mermaid.js CDN only if mermaid diagrams exist

### Step 4 — Deliver
- Save as `index.html` (or user-specified filename)
- Tell user to open directly in browser — fully self-contained

## Content Rules

- Text slides ≤40% of total (use visual layouts instead)
- Max 5 bullets per slide, max 4 lines per paragraph
- Overflow → split into 2 slides
- Dollar amounts: include KRW conversion (e.g., $2B → approx 2.8 trillion KRW)
- Layout centering: `.agenda-list`, `.step-flow` etc. must have `margin: 0 auto`

## CDN Dependencies

```html
<!-- Fonts (always) -->
Freesentation: cdn.jsdelivr.net/gh/fontbee/font@main/Freesentation/
JetBrains Mono: fonts.googleapis.com/css2?family=JetBrains+Mono

<!-- Conditional -->
Prism.js 1.29: cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/
Mermaid 10: cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
```
