<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# Automation surface (`window.qed`)

> Status: **shipped**. This is recommendation 1 of [the DOM-automation plan]; the semantic markup
> (recs 2–4) shipped first. `window.qed` is a scriptable command/query surface so a driver — a
> playwright spec, an agent driving a headless browser, or the devtools console — acts on the app
> and reads its state through one stable facade, instead of synthesizing DOM events and scraping
> attributes. The whole `tests/qed.ux.playwright` suite drives through it; no spec issues a raw
> `fetch("/graphql")`.

## Why

Two gaps remained after the markup work:

1. **Stateful setup was DOM choreography.** To put the app in a known state a driver had to click
   the right control in the right order, polling for each to settle. The suite used to sidestep this
   with `fetch("/graphql")` from inside the page — but a raw fetch mutates the *server* store without
   telling the page's **Relay** store, so every helper then had to `page.goto(...)` to force a
   refetch. That reload was slow, dropped client state, and was a constant footgun.

2. **There was no API-level contract.** Resolvers were only as tested as the browser paths that
   called them, with no single surface to drive them by name.

`window.qed` is wired to the **live Relay environment**, so a command commits the same mutation the
component would and the UI re-renders normally — no reload, no staleness. It is one documented
surface that specs, agents, and a future API-contract suite share.

## Shape

A single global, published once at app mount (when [enabled](#enabling-it)). Everything is keyed by
`viewport` index — the same int the mutations take — defaulting to the active viewport.

```js
window.qed = {
  // --- queries: read the model without scraping the DOM ---
  state(viewport?) → {
    viewport, reader, dataset: { shape:[rows,cols], origin:[row,col], channels:[tag] },
    channel, selectors: { band:[…], frequency:[…], … },
    zoom: { vertical, horizontal, coupled },
    measure: { active, closed, path:[{row,col}], selection:[idx] },
    sync: { scroll, channel, zoom, path },
  },
  viewports() → [state, …],                      // every viewport, for split layouts
  readers()   → [{ name, selectors:{axis:[…]} }],// the reader catalog

  // --- commands: act without synthesizing clicks ---
  selectReader(reader, viewport?),
  selectValue(selector, value, viewport?),       // a band/frequency/polarization/cov axis value
  setChannel(tag, viewport?),
  setZoom(level, viewport?),                      // a number (both axes) or {vertical, horizontal}
  toggleCoupled(viewport?),                       // flip whether the zoom axes move together
  centerOn(row, col, viewport?),                  // scroll so {row,col} is at the window center
  split(viewport?), collapse(viewport?), setActive(viewport),
  measure: {
    toggle(viewport?), reset(viewport?),
    add(row, col, index?), move(handle, row, col), split(handle), remove(handle),
  },
  sync: {
    toggle(aspect, viewport?),                    // flip a scroll/channel/zoom/path sync flag
    updateOffset(row, col, viewport?),            // the relative sync offset, in source pixels
  },
}
```

The visible window (the rendered viewport's origin and shape in source pixels) is **not** in
`state()`; it is published by the markup as `data-qed-view-origin` / `data-qed-view-shape` on the
minimap, which is also what `centerOn` reads to do its scroll.

Design choices:

- **Row-major, source pixels, everywhere.** `state()` returns the same coordinates the markup
  publishes (`data-qed-source`, the minimap region metadata), so a driver never converts. The
  underlying mutations are column-major (`x`,`y`); the facade is the one place that translates.
- **Commands return a promise.** Mutating commands resolve when the mutation's `onCompleted` fires,
  so a driver `await`s a settled state instead of polling. `centerOn` resolves after the scroll has
  had a frame to apply; `setActive` is synchronous (it only moves an index).
- **Queries hit the server.** `state`/`viewports`/`readers` run a focused `fetchQuery`, so they read
  authoritative server state and populate the store as a side effect.
- **Mutations and their updaters are reused verbatim.** A command commits the *same* `graphql`
  document the UI hook commits (each hook `export`s its document), and for the mutations Relay cannot
  auto-merge — the ones that swap or reorder views — the hook and the facade share one parameterized
  store updater (`replaceViewUpdater`, `splitViewUpdater`, `collapseViewUpdater`). So the store
  updates identically whether a user clicked or a driver scripted.

## Where it lives

`ux/client/automation/`:

- `qed.js` — the facade factory `makeQED()`: the `commitMutation`/`fetchQuery` helpers against the
  `environment` singleton, the `state`/`readers` queries, the `modelOf` reshaper (the column-major →
  row-major translation), and every command.
- `Automation.js` — a render-nothing component that publishes/withdraws `window.qed` on mount, behind
  the opt-in gate.
- `ViewportBridge.js` — a render-nothing component, mounted inside the viewports provider
  (`views/viz/viz/viz.js`), that keeps the facade's default viewport in sync with the UI's active
  viewport and hands the facade the UI's setter so `setActive`/`split`/`collapse` can move it.
- `activeViewport.js` — a tiny leaf module holding the active-viewport state, imported by both the
  facade and the bridge without an import cycle.

`<Automation/>` mounts once in `ux/client/qed.js`, under `<RelayEnvironmentProvider>`, so the facade
reaches the live environment. The reused store updaters live next to their mutations
(`views/viz/reader/replaceView.js`, `views/viz/viz/viewListUpdaters.js`).

The surface is typed by `tests/qed.ux.playwright/lib/qed.d.ts`, so specs and agents get completion.

## Enabling it

The surface is **opt-in**, so default production never exposes it. `Automation.js` publishes
`window.qed` only when one of these holds:

- the URL carries `?automation` (handy in dev and the devtools console), or
- `localStorage["qed.automation"] === "1"`.

The playwright suite seeds that flag for both servers under test through `storageState` in
`playwright.config.ts`, so every spec finds `window.qed` with no per-navigation query.

## How drivers use it

```js
// playwright, no reload, no DOM choreography:
await page.evaluate(async () => {
  await window.qed.selectReader("gslc")
  await window.qed.selectValue("frequency", "A")
  await window.qed.setChannel("amplitude")
  await window.qed.measure.add(1840, 3502)
})
const s = await page.evaluate(() => window.qed.state())
expect(s.measure.path).toContainEqual({ row: 1840, col: 3502 })
```

The `behavior/*` and `nisar/*` specs follow this shape: arrange state through `window.qed`, then
assert the rendered DOM (the markup) *or* `window.qed.state()` (the model). The reload dance and the
raw-fetch staleness footgun are gone.

## Relationship to the markup

The markup (recs 2–4) and this facade are complementary, not redundant:

- **Markup** answers *"what is on screen, and can I point at this control?"* — needed to verify the
  rendered result and to drive controls that have no command (or to test the controls themselves).
- **`window.qed`** answers *"put the app in state X"* and *"what is the model?"* — the fast, stable
  path for setup and read-back.

A driver uses the facade to arrange state and the markup to confirm the pixels followed. Together
the two reads — `window.qed.state()` (the Relay model) and a server query — also localize a failure:
server-right + model-right + DOM-wrong is a render bug; server-right + model-wrong is a client bug.

## Deferred

- **Annotations as first-class state.** Rec 4's markers are the measure path; if a separate
  annotation layer grows (`addAnnotation/removeAnnotation/annotations`), it joins `measure` here.
- **A standalone API-contract suite.** A thin suite could assert each command/query against the
  server with no browser UI — the resolver-level coverage noted in `doc/semantic-markup.md`. The
  facade is the natural seam for it.

[the DOM-automation plan]: ./semantic-markup.md


<!-- end of file -->
