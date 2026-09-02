<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# staging: first contact to first tile

> **Status, 2026-09-02.** The lifecycle described here is current, but the account of what
> happens between selecting a dataset and seeing it is not: it predates the chunk pyramid, so
> it describes a zoomed-out render that strides the base rather than reading a decimated level.
> Preparation now builds a pyramid for the dataset a view binds, and that pass is what produces
> the statistics as well. `pyramid.md` describes how those levels are stored and why the
> storage is changing.

> Status: **approved in outline; phase 1 pinned 2026-08-29** — the trigger design (T1)
> and the deferral sequencing are settled; the remaining open questions are at the end.
> This document records the verified timeline of what
> happens between a data product's first contact with qed and its first rendered tile, for
> each of the three actors — client, server, crew — followed by the load-bearing assumptions
> the current model makes, and a proposed redesign of the staging/launching sequence. The
> redesign is not constrained to the current state model. Companion: `doc/statistics.md`
> records the statistics knowledge and invariants; `doc/performance.md` the measurement
> program this builds on.

## The charter

Four moments to rethink, deliberately:

1. when the server has first contact with a dataset, and what happens during that time;
2. what the client displays while the server is getting its bearings with a new product;
3. what happens once the client has collected a fully populated selector from the user and
   sent it to the server — all prerequisites for rendering the first tile satisfied;
4. when the client constructs the mosaic that makes the tile requests.

The design that prompted this — grafting statistics seeding onto the current model — was
judged too naive; the honest move is to lay out the current lifecycle truthfully and then
design the sequence we actually want.

## The client timeline

### Path A — product present at page load

- **A0.** The bundle configures lazysizes before React exists: load only when visible, with
  the trigger rect shrunk by 20px. This is the only knob governing when a tile is requested.
- **A1.** The live-sync `EventSource` opens before any data is fetched (it mounts outside
  the Suspense boundary).
- **A2.** One application query fetches everything — readers with selectors, availability,
  datasets, and channels; every view with reader/dataset/channel/shape/origin/tile/session —
  in a single round trip. The whole app suspends behind the only full-page loading
  affordance in the client (the flame logo and "loading; please wait...").
- **A3.** The viewer gate is `reader.id && dataset.id && channel.id` — three ids; shape,
  tile, and session play no part. Gate closed: a static "data" icon (`Blank`), no spinner,
  no explanation. The tab shows only collapse/split.
- **A4.** Gate open: the viewport destructures `dataset.shape/origin/tile` **unguarded** — a
  null crashes into the root ErrorBoundary and replaces the entire application with the
  dead screen. The mosaic partitions the shape into `<img>` elements carrying only
  `data-src`; the network stays idle until lazysizes' next visibility pass swaps `data-src`
  into `src` — the first tile request happens asynchronously after paint, with nothing on
  screen marking it. A server-carried center scrolls in a post-paint effect, racing
  lazysizes and potentially doubling the first request set.
- **A5.** Tiles pop in individually. No ordering, no progress, no completion signal, no
  error path, no retry. The `.lazyload` class has no CSS rule — it is purely functional.

### Path B — runtime connect through the explorer

- **B0.** Navigating to `/explore` unmounts the entire viz layout. Explorer state is
  client-only.
- **B1.** Clicking a file is local state only; the connect form appears. The NISAR flavor
  suspends behind a real ring while sniffing product metadata; the native/isce2 flavors
  render an eager pre-connect preview image through the `/preview` endpoint.
- **B2. The gap.** Clicking "connect" runs the `connectReader` mutation, whose resolver
  performs full first contact — `source.open()` — synchronously. On a cold or S3-backed
  HDF5 product this is seconds to tens of seconds during which **nothing on screen
  changes**: the hook computes `isInFlight` and never renders it (the archive-connect
  forms render theirs — a local inconsistency); repeat clicks are silently dropped.
- **B3.** Success: the form closes and the user is left on `/explore` with no confirmation;
  the new reader appears in a panel they are not looking at.
- **B4.** Failure: the server catches the exception and returns `{"reader": null}` as a
  **successful** mutation. No error is shown; the form closes as on success; the client's
  updater writes a **null into `QED.readers`**. A race decides what happens next: the
  self-inflicted SSE refetch usually heals the store, but if the user reaches the datasets
  panel first, mapping `reader.id` over the null kills the whole app.

### Selection

- The red star marks an unsatisfied axis **only on the active reader**, and it gates
  nothing — it is decoration. The real gate is invisible: the server clears `dataset`
  until `len(selections) == len(selectors)`.
- Availability narrowing is computed **client-side**: for each coordinate, a brute-force
  scan of `reader.datasets` tests whether the extended selection is realizable.
  `view.available` from the server is static.
- Each coordinate click: the mutation returns the whole view (fourteen fragments, spliced
  wholesale into `QED.views` at a client-held index) **and** the self-inflicted SSE change
  frame triggers a full application refetch — two full state round trips per click.
  Clicks during flight are silently dropped.
- A coordinate click on an axis with a single available value is **inert by design** — the
  client only fires the toggle when `available.size > 1`. Single-valued axes are expected
  to arrive pre-selected from the server's open-time auto-pick. (This interaction is what
  turned the passive-construction reordering into a visible regression; see the hotfix.)
- Selection completes when the *last* coordinate response binds `dataset` (and `channel`
  too, when the dataset has exactly one). That same commit opens the viewer gate: the
  Blank icon becomes a dark rectangle, and tiles trickle in some frames later. There is no
  intermediate state and no signal that work has started.
- On a session roll the mosaic does not remount: `data-src` attributes change, the
  lazysizes `attrchange` plugin re-arms, and stale pixels persist until replacements
  decode. No indication distinguishes stale from current.

The one well-modeled loader in the client is the minimap thumbnail: a load ledger,
generation keys, retry rounds, and an explicit pending/ready state. It is the natural
template for a tile lifecycle.

## The server timeline

Everything runs on one thread — the pyre selector event loop. The only concurrency is the
forked crew.

### Boot (persistent sources)

- **S0.** Store construction, pre-loop: sources resolved one config entry at a time, all
  **passive** (`datasets == []`, `available == {}`); the dataset index is empty; viewports
  are built. Each View's `pyre_configured` — which runs inside `Component.__new__`,
  *before* `__init__` — copies `reader.selections` (empty, pre-contact) and mints the
  session token; `__init__` builds an empty pipeline table; `resolve()` drops all
  selections against the empty availability. Single-source auto-selection happens here,
  pre-contact.
- **S1.** `Server.activate`: the socket binds first; the fleet is wired; then
  `Store.open()` performs the whole of first contact **serially and blocking**: per
  source, `open()` (structure walk, discovery, availability, and — inside every dataset
  constructor — the legacy center-sample statistics and an autotune of every channel);
  casualties are logged and disconnected, **the reason discarded**; survivors are
  re-registered (the dataset index populates only now); then every viewport refreshes
  (pipeline table construction, N×C component instantiations per product, on the loop).
  No SSE fires. This is the largest serialized block in the server.

### Runtime connect

One HTTP POST executes the resolver on the loop: passive construction, then `open()`
**inline** — the loop is dead to all clients for the duration — then registration.
Failure returns `{"reader": null}` as a successful mutation (which still broadcasts the
change frame). The mutation binds nothing to any viewport.

### The view state machine

- Traits: `reader`, `dataset`, `channel` (a per-view pipeline **clone**), `selections`,
  `session`, cloned `center/measure/sync/zoom`, `members`; plus the `_pipelines` clone
  table. The viewport caches one View per reader name, so switching readers preserves
  each reader's view state.
- `viewReaderSelect`: a cache miss constructs the View — with the full pipeline table,
  eagerly. If every axis is single-valued the view can be renderable at the end of this
  one mutation.
- `viewCoordinateToggle`: selects the source first (a coordinate click also switches
  readers), toggles, resolves. Incomplete selections → `dataset = None`; complete → a
  linear scan binds the dataset; a single-channel dataset auto-binds the channel.
- `viewChannelSet` walks the channel-synced peers and installs the clone by tag.
- The session token mints at View construction and **rolls only** on controller
  update/reset and stack-membership changes — never on reader/coordinate/channel changes;
  statistics widening deliberately never rolls it.
- Every successful mutation broadcasts the constant `{"type":"change"}` SSE frame — the
  single choke point; the only non-mutation broadcaster is statistics widening.

### "All prerequisites satisfied"

The predicate `reader && dataset && channel` exists **only in the client**. The server has
no renderability notion. By that moment the server has already done everything — open,
autotune, pipelines, binding — and what remains is deferred entirely to the first `/data`
request: team formation, fork, and the worker-side re-open.

### The first `/data` request

Parse → view lookup → bounds check (skipped entirely when the view has no dataset) → task
build on the loop (full reader recipe and controller-tree harvest) → cache miss →
deferred parking → **team formation and 4× `os.fork()` synchronously on the loop** (the
children inherit the opened team-side reader, including the 4 GiB HDF5 page buffer) → the
worker rebuilds the product from the recipe and re-opens it (full discovery plus the
legacy sample, whose autotune is then overwritten by the client's controller state — pure
waste) → render → spool → descriptor over the crew channel → collect on the loop
(subscriber callbacks, statistics merge and the full controller reconciliation walk,
cache insertion) → the BMP written blocking on the loop. Measured serial fraction
s ≈ 0.7; ceiling ≈ 143 tiles/s (`doc/performance.md`).

### State the server does not track

No opening/ready/failed status anywhere visible — only a private `_opened` boolean per
reader family, absent from the protocol and the schema. No failure state: reasons are
discarded. No tuned/seeded state: tuning is implicit in dataset construction. No
renderability state. No team/warmth/progress visibility. The natural homes, when they are
wanted: a status on the reader component; a per-source record in the `Sources` catalog;
`status`/`error` on the gql Reader type; a derived `ready` on the gql View type;
cross-cutting state in the Store.

## The crew timeline

The crew clock starts when the first tile task for a reader reaches the fleet.

- **C0.** The dispatcher builds the task from live view state: reader recipe, selector,
  channel tag, controller tree, tile spec. On the loop.
- **C1.** `Fleet.render` → `Fleet.team(...)`: the team is formed — wired to the shared
  dispatcher, cache, and stats sink — but no processes exist. Only the reader *name* is
  known here; the recipe rides the task.
- **C2.** `team.assign`: the task enters the workplan — an insertion-ordered dict served
  **LIFO** (newest first, deliberately); the callback ledger is keyed by task identity;
  identical in-flight tasks dedup by absorbing callbacks and renewing priority.
- **C3.** The first assign recruits: all `team.size` workers fork at once, asynchronously
  registering; only then can any receive work.
- **C4.** A worker receives the task, rebuilds the reader from the recipe, and calls
  `reader.open()` — full discovery, the legacy sample, the throwaway autotune.
- **C5.** Render; spool; then a second pass over the same decimated footprint produces the
  mergeable statistics record (where `sample()` exists: memmap and NISAR only).
- **C6.** The report crosses the crew channel: a pickled triple; the spool's descriptor
  rides as ancillary data — conditionally, on both ends, so a non-Spool result travels
  cleanly.
- **C7.** `Team.collect`: subscribers first (the parked HTTP responses resolve), then the
  statistics drain to the store (merge → widen → coalesced SSE if bounds moved), then the
  cache takes the spool.
- **C8.** Later tiles: warm registry, cache hits.

Sharp edges: the LIFO workplan (tasks enqueued at formation run *after* the task that
triggered formation); `assign` requires a real callback (fire-and-forget trips a
"duplicate delivery" firewall); a disband hands pending callbacks a `RecoverableError`.

## Load-bearing assumptions of the current model

Client:
1. `shape`/`origin`/`tile` are non-null the instant `dataset.id` is (unguarded).
2. A reader listed in `QED.readers` has completed first contact.
3. `connectReader` returns a reader or raises; `QED.readers` never contains null.
4. Mutations are fast enough to need no progress UI (the flags exist; they only drop input).
5. `view.available` is static; the client re-derives narrowing from the resident catalog.
6. A whole-application refetch is a safe response to any change — including the acting
   client's own click and statistics accumulating from tiles still in flight.
7. Tiles need no lifecycle.

Server:
8. `open()` is synchronous, idempotent, and complete before anyone sees the reader.
9. Discovery is deterministic: a worker rebuilding from the recipe finds the same datasets.
10. Statistics belong to dataset construction; a dataset cannot exist untuned.
11. Controller bounds are presentation (`cosmetic`, outside tile identity); picks are
    identity — anything that moves a pick must roll sessions and broadcast.
12. Every state change is a mutation POST; an async completion has no path to the client
    except the notifier back door.
13. Readiness is the client's business.
14. Fork happens on the request that needs it; the loop can afford the whole serialized
    path (measured s ≈ 0.7).

Crew:
15. Work exists only as a consequence of a tile request.
16. A casualty is structural, never retried.

## The redesign: staging as a crew-run survey

The central move: **the server process never touches a data file.** First contact becomes
an asynchronous, observable **staging** phase executed by the product's own crew — the
actor that must open its own copy anyway. What makes this possible is a property the
current code already proves daily: a passive reader is fully reconstructible from its
traits (the worker rebuild does exactly this), so first contact can happen *anywhere*.

The product lifecycle becomes explicit — a per-source record in the `Sources` catalog,
exposed through the schema:

    connected ──> staging ──> ready
                     └──────> failed   (error retained; retry / disconnect affordances)

### The new timeline

- **T0 — connect** (mutation or boot): passive construction; the source registers with
  status `connected`. Boot does nothing further: the server binds, wires the fleet, and
  serves — it never initiates staging on its own. A runtime connect stages its one new
  source immediately — the mutation is client contact by definition — and **returns at
  once**. The SSE change frame fires and the client panel shows the product with a busy
  affordance (the ring the archive-connect forms already use).
- **T1 — the trigger** (pinned 2026-08-29): the monolithic application query stays — the
  contentless SSE change frame obligates a refetch-everything client — and becomes
  answerable passively: names, uris, statuses, declared selectors; no file contact. Its
  firing therefore carries no meaning (it fires on `/explore` just as on the viz routes);
  catalog relevance is declared instead by an explicit `stage` interaction: the viz
  activity, observing readers with status `connected`, asks the server to stage them.
  The same verb pointed at a single source is the retry affordance for `failed`.
  Readiness arrives per source as surveys land, so clients refresh progressively — the
  panel lights up product by product — coalesced by the existing hub. A stale client
  converges through the same frames; tile requests it fires before its refresh fall to
  the inline path and are refused harmlessly.
- **T2 — survey**: the fleet forms the product's team *now* — not at first tile — and
  assigns a survey task. One worker builds the reader from the recipe, performs the only
  first contact anywhere, and ships back a picklable **discovery record**: per-dataset
  metadata (selector, shape, origin, tile, cell/datatype, channel set), the availability
  map, and per-dataset seed statistics **in exactly the shape that dataset's channels
  expect** — a triple, or the unwrapped flavor's list of two — because the record is
  authored by the reader flavor itself, dissolving the shape hazard of a uniform seed.
  Additional stats stripes can fan out across the team as follow-on tasks that refine
  through the existing widen path. The survey is not a parallelization device: discovery
  of even the richest product is serial work performed by one worker, and no intra-product
  speedup is sought. The crew's involvement buys placement, not speed — the loop never
  blocks, a defective file kills a worker instead of the server, products survey
  concurrently with one another, and the surveying worker keeps the product open exactly
  where tiles will be rendered.
- **T3 — hydration**: the record lands (a staging sink beside the stats sink on the team).
  The team-side reader **hydrates**: datasets materialize as metadata-only objects
  configured from the record; controllers autotune from the seed — the one legitimate
  pick-setting moment, guaranteed to precede any view binding the dataset, so no session
  roll and no re-render moment ever exists. Status flips to `ready`; SSE fires; the panel
  lights up with selectors and availability. A survey failure flips to `failed` with the
  error retained and displayed; the source stays listed, with retry and disconnect
  affordances.
- **T4 — selection**: exactly as today; all metadata is local. When `resolve()` binds
  dataset and channel, the View exposes a server-computed `ready`, and the client gate
  reads it instead of inferring readiness from three nullable joins.
- **T5 — first tile**: the crew is formed **and warm** — the survey opened the product in
  the worker registry. No fork storm on the request path, no worker re-open, no throwaway
  autotune, and the first paint is correctly tuned. The first-paint UX question from
  `doc/statistics.md` **dissolves**: tiles cannot be requested before the seed, because
  the selector panel does not populate until the survey lands.

### What this retires

The center-256² sample (`_collectStatistics` in every dataset constructor); the worker-side
throwaway autotune; the blocking `open()` in the connect mutation and in `Store.open`; the
fork-on-first-tile stall; the multi-GiB HDF5 page buffer in the server process (and its
forked copies); the null-reader and silent-failure pathologies.

### What survives untouched

The view state machine and its mutations; the session discipline; the identity/cosmetic
guardrails; widen-after refinement; the tile cache; the client selection mechanics.

### The legacy escape hatch

Server-side dataset objects retain the *ability* to open lazily on first pixel touch (the
house sentinel idiom), so the inline render fallback, `/profile`, `/preview`, the gql
pixel peeks, and the measure CLI keep working without the fleet. Nothing on the serving
path uses it.

## Implementation phases (each its own PR)

- **Phase 1 — the deferral.** The trigger machinery wrapped around today's blocking open,
  in three commits that each leave the suites green: (1) a `stage` mutation whose resolver
  runs `Store.open()` — already idempotent, since every reader guards with `_opened` —
  plus a minimal `Reader.status` in the schema so a client can observe an unstaged
  catalog; (2) the viz activity fires `stage` whenever it observes readers with status
  `connected` — a no-op while boot still opens; (3) `Server.activate` stops calling
  `ux.store.open()`, and the trigger carries the load. A side benefit: the trigger moves
  from the nexus server's `activate` into the API layer, so staging becomes server-flavor
  agnostic. Accepted interim warts, both dissolved by later phases: the stage resolver
  blocks the loop exactly the way the connect mutation does today, and a fresh client
  briefly renders the passive catalog until the stage round trip lands. Checks: every gql
  resolver tolerates the passive state; the playwright awaits absorb the new startup
  timing.
- **Phase 2 — the survey.** A `Survey` task reusing the `Tile` core (recipe harvest,
  worker-side locate/open, `RecoverableError`, identity) minus pipeline/controllers; the
  flavor-authored discovery record; a staging sink on `Team`/`Fleet`; reader hydration
  (metadata-only datasets plus the lazy-open escape hatch); `Fleet.stage(reader)` forming
  the team eagerly. The LIFO workplan is harmless here: the survey is assigned before any
  tile can exist.
- **Phase 3 — lifecycle state, schema, and client affordances.** DONE. The per-source
  `Lifecycle` record in `Sources` (status, error, elapsed); `Reader.error` and `View.ready`
  joined the schema (`Reader.status` arrived in phase 1, and now reads the record); the
  stage resolver delegates to the fleet, so the mutation returns in milliseconds and the
  outcome arrives over SSE; the connect mutation constructs passively and stages; the
  panel gained busy/failed/retry (retry is the `stage` verb pointed at one source); the
  null-reader poison and the unrendered `isInFlight` are fixed; the viewer gate reads
  `View.ready`.

  Two policies changed, deliberately: a source whose first contact fails **stays listed**
  with its reason instead of being disconnected, and a view bound to it keeps its binding,
  since the source is no longer dangling. The escape hatch had to land here rather than
  later: a hydrated twin holds no payload, so the pixel peek and the profile broke until
  `Store.realize` was added — it opens one live copy of a product, on demand, the first
  time somebody reads values in the server process. Readers advertise `surveyable`;
  flavors without it (GDAL, stacks) and every shell without a fleet keep the blocking
  `open()`, which is now the documented fallback rather than the main path.
- **Phase 4 — statistics retirement.** DONE. Measurement left dataset construction for an
  explicit `measure()`, so the worker's throwaway sample is gone rather than flagged
  around; `autotune(stats=None)` is a no-op in `Controller.autotune` and in the three isce2
  unwrapped channels that index before delegating; GDAL renders from its channel's `range`
  controller instead of `self.stats` and gained `survey()` and a hydrated path, so every
  flavor is now surveyable; `doc/statistics.md` records the outcome.

  Two things went differently from the plan. The stripe-refinement tasks are not needed for
  seeding — the survey supplies the seed before any view can bind a dataset, which is what
  those tasks existed to guarantee — so they were not built; whole-extent coverage still
  arrives through the minimap thumbnail and ordinary viewing still widens. And
  `_collectStatistics` was not deleted: it is the body of `measure()`, because the seed has
  to come from somewhere and a better estimator is separable work. Replacing the center
  window is now the only real deficiency left, and it is confined to one method per flavor.
- **Phase 5 — client tile lifecycle** (optional, scoped separately): the mosaic adopts the
  thumbnail's ledger/generation model; per-tile error and retry; a loading affordance in
  the viewport.

## Verification

Per phase: the `tests/qed.pkg` suite run directly; the full playwright suite; live checks
on the c16 fixture and the GSLC — staging visible in the panel, the connect mutation
returning immediately with the busy ring showing, first tile tuned on arrival,
`qed about --shell=script` still instant. New tests: survey round-trip fidelity
(recipe-rebuilt discovery matches team-side hydration); staging failure → `failed` with
the error retained; seed-before-bind ordering; the hydrated dataset's lazy-open escape
hatch; asynchronous connect.

## Open questions

1. **Seed coverage before `ready`**: does the first stripe suffice (fast staging; widen
   refines as the rest land), or should a whole-extent deep sample complete first (slower
   staging on compressed HDF5; better first picks)?
2. **Availability narrowing**: move it server-side while the panel is open for surgery, or
   leave the client-side scan?
3. **Tile-lifecycle scope** (phase 5): adopt the tile ledger now or defer?
4. **The unit of work for chunked products**: every workload qed builds — the tile request,
   the thumbnail slice, the measurement sweeps — is a fixed square of *output*, while the
   cost of serving one is set by the *chunks* its source footprint covers. The two diverge
   with zoom, so a whole-dataset pass at deep decimation is carved into a handful of tasks
   of wildly unequal cost. This is recorded against the crew measurements in
   `doc/statistics.md`, whose parallel ceiling is probably an artifact of it. The likely
   answer is to decouple the crew's unit from the client's: tasks sized in chunks, mosaics
   assembled from whatever set of them covers a display tile.
5. **Warming the rest of the team**: the survey leaves only one worker with an open
   product; the others pay a cold open on their first tile, which lands on the critical
   path of the first mosaic. Candidate: post-survey warm-up tasks that fan out to the
   remaining members under cover of human selection time — noting that the workplan's
   join-equal semantics require per-member task identities, and that the phase-4
   statistics stripes would produce the same warmth as a side effect of useful work.

(Resolved: the interim selection hotfix — `View.refresh()` adopting `reader.selections`
for views built before first contact — merged as PR #94 on 2026-08-29. Under phase 1 the
adoption runs at stage time instead of boot time; the solo playwright server guards it.)


<!-- end of file -->
