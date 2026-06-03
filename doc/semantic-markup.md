<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# Semantic markup convention

Every control a user can interact with carries semantic markup, for two audiences:
assistive technology (ARIA) and automated drivers — tests and agents. This note is
the convention; `etc/qed/audit/semantic.mjs` is the gate that enforces it.

## The core idea: two owners, two namespaces

A control carries two kinds of semantic information, owned by two different parties:

| | Owner | Answers | Lives in | Travels to pyre? |
|---|---|---|---|---|
| **Role + state** | the **widget** | *what kind* of control, and what state? | ARIA (`role`, `aria-*`) + `data-pyre-widget-*` | yes, unchanged |
| **Identity** | the **client** (qed) | *which* control, what does it mean here? | `data-qed-*` | no — it stays at qed's call sites |

A slider *is* a slider no matter who ships it, so `role="slider"` and
`data-pyre-widget-part="thumb"` are intrinsic and portable; they belong inside the
widget. "This is the STACK INDEX selector" is qed's statement, so
`data-qed-control="stack-index"` belongs at the qed call site. When a widget graduates
to the shared pyre widget library, nothing in the widget changes, because the
qed-specific identity was never inside it.

## Namespaces

- **`data-pyre-widget="<kind>"`** — the widget kind: `flex`, `slider`, `toolbar`,
  `tile`, `mosaic`. Emitted by the widget.
- **`data-pyre-widget-part="<part>"`** — an interactive sub-part: `resizer`, `thumb`,
  `track`, `panel`. Emitted by the widget.
- **`data-pyre-widget-name="<instance>"`** — client-supplied identity for an *internal*
  part the client cannot reach with `{...rest}` (e.g. the flex separator). The client
  passes a `name` prop; the widget re-emits it under this neutral attribute.
- **`data-qed-*`** — client identity at the call site: `data-qed-control`,
  `data-qed-value`, `data-qed-panel`. Greppable, app-meaningful, qed-only.

`data-pyre-widget-*` (not bare `data-widget`, which a third-party library might squat,
nor bare `data-pyre-*`, which is broader than the widget subsystem) reserves the
namespace for widgets specifically.

## ARIA is the single source of truth for state

Selected / checked / pressed / disabled / current-value live **only** in ARIA —
`aria-checked`, `aria-selected`, `aria-pressed`, `aria-disabled`, `aria-valuenow`. Do
**not** mirror state into a `data-*` attribute: two sources drift apart. State is already
queryable (`[aria-checked="true"]`, Playwright `getByRole`). `data-*` carries *identity*,
never state. A control that turns a mode on and off — e.g. the viewport `measure` and
`sync` glyphs — is a toggle button: `role="button"` + `aria-pressed`. The panel such a
button governs carries its own client identity (`data-qed-panel`) so the
button-governs-panel relationship is testable without scraping the panel title.

## Role and accessible name can be client-owned too

Some widgets' role is contextual. A `toolbar` is a navigation landmark in one place and
a `role="toolbar"` command bar in another. A `mosaic` is one logical raster image. The
widget sets a sensible default and forwards `{...rest}`, so the client overrides `role`
and supplies `aria-label`. Same principle: the client owns what only the client knows.

## Per-widget contract

| Widget | Element | Widget-owned | Client-owned |
|---|---|---|---|
| `toolbar` | `<nav>` | `data-pyre-widget="toolbar"`; default nav landmark | `aria-label`; `role="toolbar"` for a command bar; `data-qed-*` |
| `flex` panel | `<div>` | `data-pyre-widget="flex"` `-part="panel"` | `name`, `data-qed-panel` |
| `flex` separator | `<div>` | `role="separator"`, `aria-orientation`, `aria-valuenow/min/max`, `aria-controls`; `-part="resizer"`, `-name` | identity via the panel's `name` |
| `tile` | `<img>` | `data-pyre-widget="tile"`, `alt=""` (decorative slice) | `alt` override, `data-qed-*` |
| `mosaic` | `<div>` | `data-pyre-widget="mosaic"`, default `role="img"`, `-origin/-shape/-zoom` | `aria-label`, `data-qed-*` |
| `slider` thumb | SVG `<g>` | `role="slider"`, `aria-valuenow/min/max`, `aria-orientation`, `aria-disabled`; `-part="thumb"` | `label` (→ `aria-label`) |
| `slider` track | SVG `<g>` | `data-pyre-widget="slider"` `-part="track"` | — |

## Known gap: keyboard operability

The flex separator and slider thumb are marked as a `separator` / `slider` with live
values, but are **not yet keyboard-operable** (no arrow-key resize / value change). That
is a behavior change wiring into `doFlex` / `setValue`, not markup, and is deferred. The
`aria/coverage` test reports these as interactive controls so the gap stays visible.

## The gate — `mm qed.ux.playwright`

The convention is enforced by the `qed.ux.playwright` suite (`.mm/qed.ux.playwright`), an mm
*runner* suite that delegates to Playwright: `mm qed.ux.playwright` builds the client, then runs
`npx playwright test`, which drives the built client in a headless browser.

The suite owns its server. `playwright.config.ts` launches an isolated `qed` instance (the
installed command) from the shared, generated test-data tree (`tests/data/native/` — a 3929×6049
complex `native.flat` raster produced by the `qed.data` generators, never committed) on a
dedicated test port (8137, overridable; the port is passed through to `qed` on the command line so
parallel suites don't collide). Because the server is private to the run, the suite may be
stateful — it no longer has to be read-only against a shared server.

Playwright projects (`tests/qed.ux.playwright/`):

- **`setup`** (`setup/render.setup.ts`) — selects a channel through the client's own GraphQL
  endpoint (`viewChannelSet`) so exactly one Mosaic, and the zoom slider on `/controls`, renders.
  Without it the viewport is an empty shell and the widget checks are vacuous. The selection is
  server-side state, so it persists for the later projects.
- **`gate`** — every `identity/*.spec.ts` and `aria/*.spec.ts` must pass:
  - `identity/grammar.spec.ts` — every `data-pyre-widget` names a known kind and every
    `-part`/`-name` lives under a `-widget`; data-independent.
  - `aria/widgets.spec.ts` — every tagged widget part carries the ARIA its role implies (slider
    thumb → `aria-valuenow/min/max`, separator → `aria-orientation`, mosaic → `role`+`aria-label`).
  - `aria/coverage.spec.ts` — every interactive control (native or `cursor: pointer`, excluding
    `aria-hidden` decorative subtrees) carries a `role`, a `data-pyre-widget`, or a `data-qed-*`.
    The phase-2 rollout is complete, so this is now a hard gate, not a backlog.
  - per-control identity specs — `channels`, `detail`, `sync`, `icons` (nav rail + viewport
    actions), `actions` (viewport toggle buttons + the panels they govern), `slider` (decorative
    scale + minimap), `doc` (table-of-contents topics) — assert the exact role/ARIA/`data-qed-*`
    each control owes, so a regression is pinned to a single control.

`mm qed.ux.playwright` runs only the `gate` project, so a clean tree is green; failures print one
line per problem. The framework lives in a dedicated `node_modules` kept out of the client bundle
(`tests/qed.ux.playwright/config/package.json`); browser binaries are located by `PLAYWRIGHT_BROWSERS_PATH`
(set once in your shell profile). mm installs both on first run.

The GraphQL setup runs from inside the page (browser `fetch`), exactly as the client does — pyre's
minimal HTTP server is happy with the browser's requests but not with Playwright's node-side
`request` fixture.

Detection caveat: `coverage` uses `cursor: pointer` as its proxy for "interactive",
because React's event delegation hides `onClick` from the DOM. This catches icon-style
controls but misses clickable elements that do not set a pointer cursor (e.g. the
selector value chips). Those are covered once they carry `data-qed-*` in any case; a
convention worth adopting is that every interactive control sets `cursor: pointer`.


<!-- end of file -->
