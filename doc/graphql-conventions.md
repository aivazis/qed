<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# GraphQL schema conventions

> Status: **agreed** (branch `automation-surface`, 2026-06-04). Drafted from an audit
> of the graphene implementation (`pkg/gql/`) and the hand-written SDL
> (`ux/schema/qed.gql`); all decisions signed off. The reconciling renames and the
> SDL-generation step are implemented on this branch.
>
> Relay scope check: this client uses **no connections and no refetch**, so Relay's
> mandated names (`*Connection`/`*Edge`/`PageInfo`/`edges`/`node`/`cursor`,
> `node(id:)`) do not apply. Relay's naming rules govern client fragments
> (`Component_prop`) and operation names (`XxxMutation`), not server field or payload
> type names — so the server-side renames below are unconstrained by Relay.

## 0. Single source of truth

The **graphene implementation under `pkg/gql/` is authoritative.** It is the only
schema the running server executes (`pkg/gql/__init__.py` builds it;
`pkg/ux/GraphQL.py` serves it).

`ux/schema/qed.gql` is a **generated artifact**, produced from the graphene schema
(`graphql.utilities.print_schema`) and consumed only by the relay compiler at client
build time (`ux/config/package.json` → `"schema": "./schema/qed.gql"`). It is **never
hand-edited**. A `make` target (or `bin/qed` subcommand) regenerates it; CI fails if
the committed file differs from a fresh generation.

> Why this matters: before this change the SDL was hand-maintained in parallel and had
> already drifted — not just stale fields (`stackIndex`) but wrong **type names**
> (`DatasetMeasure`/`DatasetSync`/`DatasetZoom`, `ViewInfo`, `ViewInfos`) that never
> existed on the server. The app only worked because Relay matches on field *shape*.
> Generation makes the SDL truthful by construction and removes the per-change manual
> edit that made additions error-prone.

## 1. Naming at a glance

| Aspect | Rule |
|--------|------|
| Object / interface types | `PascalCase`, singular noun for the entity |
| Input types | `PascalCase` + `Input` suffix |
| Fields & arguments | `camelCase` |
| Enum values | `UPPER_SNAKE` |
| Relay id | `id: ID!` — `ID` is used **only** for the relay node id |
| Display / human name | `name: String!` — never `ID` |
| Domain reference (reader, channel, controller…) | `String` (these are pyre family strings) |

## 2. Object types

- One concept per type, named for the concept.
- Types that are relay nodes implement `Node` and carry `id: ID!`.
- **View-scoped state is prefixed `View`, not `Dataset`.** The per-view measure, sync,
  and zoom state lives on `View` and is mutated by `view*` mutations, so:
  - `Measure` → **`ViewMeasure`**, `Sync` → **`ViewSync`**, `Zoom` → **`ViewZoom`**.
  (Graphene currently emits the bare names; the SDL falsely claimed `Dataset*`. We
  converge on `View*` — correct owner, not a generic global noun.)
- `Metadata` (graphene) / `ProductMetadata` (SDL) → settle on **`ProductMetadata`**.
- The selector pair stays split but is renamed for clarity:
  - `Selector` — a *chosen* `{ name, value }` (unchanged).
  - `Selectors` → **`SelectorAxis`** — an axis `{ name, values: [String!]! }` (the
    plural-as-type-name was the single most confusing name in the schema).

## 3. Mutations

### 3.1 Field name shape

`<scope><Area><Action>` — **scope and area first, verb last.**

- **scope** — `view` for anything addressed by a viewport; **no prefix** for
  session-level operations (`connectArchive`, `disconnectReader`).
- **area** — the sub-system the mutation targets (`Reader`, `Channel`, `Coordinate`,
  `Members`, `Measure`, `Sync`, `Zoom`, `Range`, `Value`); omitted when the mutation
  acts on the viewport itself (`viewCollapse`, `viewSplit`, `viewPersist`).
- **action** — the verb (`Set`, `Reset`, `Toggle`, `Update`, `Add`, `Move`…), last.

This regularizes today's verb-first outliers and pulls the view-scoped controller
mutations (which take a `viewport`!) under the `view` scope:

| Current | Proposed | Why |
|---------|----------|-----|
| `viewSelectReader` | `viewReaderSelect` | verb-first → area-first |
| `viewToggleCoordinate` | `viewCoordinateToggle` | verb-first → area-first |
| `viewSetMembers` | `viewMembersSet` | verb-first → area-first |
| `viewResetMembers` | `viewMembersReset` | verb-first → area-first |
| `updateRangeController` | `viewRangeUpdate` | namespace under `view`; drop `Controller` noise |
| `resetRangeController` | `viewRangeReset` | "" |
| `updateValueController` | `viewValueUpdate` | "" |
| `resetValueController` | `viewValueReset` | "" |
| `viewChannelSet` | `viewChannelSet` | already conforms |
| `viewCollapse`, `viewSplit`, `viewPersist` | unchanged | viewport-level, no area |
| `viewMeasure*`, `viewSync*`, `viewZoom*` | unchanged | already area-first |
| `connect*`, `disconnect*` | unchanged | session-level, verb-first is fine |

### 3.2 Class name = field name

The graphene `Mutation` subclass is named in `PascalCase` to match its field, e.g.
field `viewReaderSelect` ← `class ViewReaderSelect(graphene.Mutation)`. Because
graphene names a mutation's **payload type after the class**, this makes the payload
type self-describing and kills the fictional `*Info` / `*Infos` SDL types (they were
never real). Payloads wrap the affected entit(ies) under a field named for them —
singular for one, pluralized for a list (see 3.4).

### 3.3 Arguments

- **Single-`input` idiom (Relay-standard).** Every mutation takes exactly one
  argument, `input: <Mutation>Input!`, and is called `foo(input: $input)`. The input
  type is named `<PascalMutationName>Input` (e.g. `ViewMembersSetInput`). This is the
  Relay convention and makes optimistic/updatable patterns available later. It holds
  even for single-scalar mutations: `viewCollapse(input: ViewCollapseInput!)` where
  `input ViewCollapseInput { viewport: Int! }`.
- Inside the input: the viewport index is always **`viewport: Int!`**; a reader /
  stack name is always **`reader: String!`** — never `source`. (The store may keep
  `source` internally; the GraphQL surface is uniform.)

### 3.4 Payload field names

The field that carries the result is named for the entity, and **pluralized when it is
a list**:

- single: `view`, `measure`, `sync`, `zoom`, `archive`, `reader`, `controller`.
- list: `views`, `measures`, **`syncs`**, **`zooms`** (today `DatasetSyncInfos.sync`
  and `DatasetZoomInfos.zoom` are wrongly singular).

The *shape* a mutation returns (one entity vs. many) follows its semantics and is not
dictated here; this rule only governs the field name once the shape is chosen. The
existing shape mismatches (`viewSyncToggleAll` → `views`, `viewSyncToggleViewport` →
`view`, `viewSyncReset` → `sync`) are flagged for an intent review during the rename.

## 4. Input types

- `PascalCase` + `Input`; fields `camelCase`.
- `connectEarthAccessArchive` is the worst offender (inline scalars mixed with eight
  structured inputs); fold its scalars into a single `EarthAccessQueryInput`.

## 5. Dead code to drop

- `VisualizationPipeline` and `PageInfo` — present only in the hand SDL, no graphene
  backing; they disappear once the SDL is generated.
- `ArchiveConnection` / `ReaderConnection` — graphene classes that are unused and
  absent from the SDL; delete unless we are about to adopt relay connections.

## 6. Adding to the schema — the checklist

1. Add or edit the graphene type/mutation under `pkg/gql/` following sections 1–4.
2. Wire the mutation field in `Mutation.py` (field name = `camelCase` of the class).
3. Regenerate the SDL (`make schema` / `qed schema export`) — **do not** edit
   `ux/schema/qed.gql` by hand.
4. Run the relay compiler; update client `.graphql` operations to match.
5. Build and test.

<!-- end of file -->
