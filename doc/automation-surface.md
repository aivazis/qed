<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# Automation surface (`window.qed`) — design for review

> Status: **proposal**. This is recommendation 1 of [the DOM-automation plan]; the semantic
> markup (recs 2–4) has shipped, and the driveability audit (`doc/semantic-markup.md`) now
> shows every control is findable. This doc proposes the remaining piece: a scriptable
> command/query surface so a driver acts and reads state through one stable facade instead of
> synthesizing DOM events and scraping attributes. Nothing here is built yet.

## Why

Two gaps remain after the markup work:

1. **Stateful setup is still DOM choreography.** To put the app in a known state a driver must
   click the right control in the right order, polling for each to settle. The playwright suite
   sidesteps this by calling `fetch("/graphql")` from inside the page — but a raw fetch mutates the
   *server* store without telling the page's **Relay** store, so every helper must then
   `page.goto(...)` to force a refetch (see `behavior/markers.spec.ts`, `nisar/selectors.spec.ts`).
   That reload is slow, drops client state, and is a constant footgun.

2. **There is no API-level contract.** The resolvers are only as tested as the browser paths that
   call them; there is no place to assert "this mutation does this" independent of the UI.

A `window.qed` facade wired to the **live Relay environment** fixes both: a command commits the
same mutation the component would, so the UI re-renders normally (no reload), and the facade is a
single documented surface that tests and agents — and a future API-contract suite — share.

## Shape

A single global, published once at app mount, with a query half and a command half. Everything is
keyed by `viewport` index (the same int the mutations already take), defaulting to the active one.

```js
window.qed = {
  // --- queries: read the view model without scraping the DOM ---
  state(viewport = active) → {
    viewport, reader, dataset: { shape:[rows,cols], origin:[row,col], channels:[tag] },
    channel, selectors: { band, frequency, polarization|cov, ... },
    zoom: { vertical, horizontal },
    origin:[row,col], view:[rows,cols],          // visible window, source pixels
    measure: { active, closed, path:[{row,col}], selection:[idx] },
    sync: { scroll, channel, zoom, ... },
  },
  viewports() → [stateForEach],                  // all of them, for split layouts
  readers() → [{ name, selectors:{...} }],       // the catalog

  // --- commands: act without synthesizing clicks ---
  selectReader(reader, viewport?),
  selectValue(selector, value, viewport?),       // band/frequency/polarization/cov/channel
  setChannel(tag, viewport?),
  setZoom(level, viewport?),                      // or {vertical, horizontal}
  centerOn(row, col, viewport?),                  // setOrigin in source pixels
  split(viewport?), collapse(viewport?), setActive(viewport),
  measure: {
    toggle(viewport?), reset(viewport?),
    add(row, col, index?), move(handle, row, col), split(handle), remove(handle),
  },
}
```

Design choices:

- **Row-major, source pixels, everywhere** — `state()` returns the same coordinates the markup
  publishes (`data-qed-source`, the viewport/minimap region metadata), so a driver never converts.
  The underlying mutations are column-major (`x`,`y`); the facade is the one place that translates.
- **Commands return a promise** that resolves when the mutation's `onCompleted` fires, so a driver
  `await`s a settled state instead of polling.
- **Queries read the Relay store first**, falling back to a `fetchQuery` when a field is not yet
  resident — cheap and synchronous for the common case.

## Where it lives

A small module — `ux/client/automation/` — mounted once near the Relay `<RelayEnvironmentProvider>`
and the viewports context (`useViewports`). It needs three things the components already have:

- the **Relay environment** (to `commitMutation` against the live store — this is what makes the UI
  update without a reload);
- the **viewports controller** (`activeViewport`, the registrar) to resolve the default viewport;
- the existing **mutations**, reused verbatim — `viewSelectReader`, `viewChannelSet`,
  `viewToggleCoordinate`, `viewZoom*`, `viewMeasureAnchorAdd/Place/Split/Remove`, `viewMeasureReset`,
  `viewMeasureToggleLayer`. The facade is a thin typed wrapper over these, not new server code.

Publishing to `window` is deliberate: it is reachable from Playwright's `page.evaluate`, from an
agent driving a headless browser, and from the devtools console, with no bundler coupling. Gate it
behind a build flag or a `?automation` query param if we don't want it in production bundles.

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

The existing `behavior/*` and `nisar/*` specs collapse to this: set up through `window.qed`, then
assert the rendered DOM (the markup) *or* `window.qed.state()` (the model). The reload dance and the
raw-fetch staleness footgun disappear.

## Relationship to the markup

The markup (recs 2–4) and this facade are complementary, not redundant:

- **Markup** answers *"what is on screen, and can I point at this control?"* — needed to verify the
  rendered result and to drive controls that have no command (or to test the controls themselves).
- **`window.qed`** answers *"put the app in state X"* and *"what is the model?"* — the fast,
  stable path for setup and read-back.

A driver uses the facade to arrange state and the markup to confirm the pixels followed.

## Open questions

- **Annotations as first-class state.** Rec 4's markers are the measure path; if we grow a separate
  annotation layer (`addAnnotation/removeAnnotation/annotations`), it joins `measure` here.
- **Production exposure.** Always-on, or behind a flag/param? Leaning: behind `?automation` so it is
  trivially available in dev and tests but absent from default production bundles.
- **A standalone API-contract suite.** Once the facade exists, a thin suite can assert each
  command/query against the server with no browser UI — the missing resolver-level coverage noted in
  `doc/semantic-markup.md`. Worth doing as a follow-up, not part of the first cut.
- **Typing.** A `.d.ts` for `window.qed` so specs and agents get completion and the surface is
  self-documenting.

[the DOM-automation plan]: ./semantic-markup.md


<!-- end of file -->
