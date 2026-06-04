<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# Stack membership — replacing the stack-index slider

> Status: **Wave 1 complete and tested** (branch `stack-membership`, builds clean via `mm`). The
> client ships the raw per-member toggles. The **reset** capability landed server-side (resolver +
> `viewResetMembers` mutation) but its client buttons are **deferred** — we want to show the raw
> capability and gather feedback before committing to the All / Invert / Reset UI. All / Invert
> were client-only sugar and are not yet built.

## Why

The current stack control (`ux/client/views/viz/reader/stack.js`) is a `Slider` with one tick
per member. Clicking pins a single member; clicking the pinned tick again clears the pin and
returns to the collective aggregate. It does not scale past a handful of members, the un-pin
gesture is invisible, it shows an index rather than member identity, and "aggregate vs. member"
is implied by the *absence* of a marker.

We replace it with a row of toggle buttons — one per member, styled identically to the other
selectors — where each button toggles whether that member **participates in the aggregate**.
All members participate by default; the default is configurable on the `Stack`.

## Key insight — this generalizes, it does not replace

The proposed model is a strict superset of today's behavior:

- old "pin member *k*" ≡ new "all off except *k*"
- old "clear pin" ≡ new "all on"

So the single-member path (swap in the member's own dataset, expose its native channels, widen
availability, validate selections) is *reused unchanged*. The only genuinely new behavior is
aggregation over an arbitrary subset.

## Decisions (settled)

1. **Single active member → that member's native channels** (the existing `_pinnedDataset`
   path), not aggregate-of-one. Preserves phase for complex members and reuses built machinery.
2. **Membership default is a `Stack` trait** that primes the initial mask in the `Stack`
   constructor; **empty ⇒ all**. After construction the live mask is **per-View**, seeded by
   copying the trait-resolved default. Per-View (not global) preserves the ability to show
   different subsets in different viewports — the point of having viewports for comparison.
3. **Order-preserving structure.** The mask is a positional `list[bool]` aligned to the already
   ordered `Stack.readers`; never a `set`. Member order is canonical config (qed.yaml) order.
4. **Convenience actions (All / Reset / Invert)** are Wave 2, on top of the proven mutation.
   "None" is omitted — the empty set is forbidden at runtime. All / Invert are pure client
   computations over the current mask; **Reset is a server action** (`viewResetMembers`) so the
   default never leaves the server. The client UI is deferred pending feedback (see Wave 2).

## Vocabulary

- **`Stack.membership`** — config trait, ordered list of member identifiers active at startup;
  empty ⇒ all.
- **`Stack.defaultMask`** — `list[bool]`, length `extent`, aligned to `Stack.readers`; computed
  once in `__init__` from `membership` (empty ⇒ all `True`; all-`False` guarded back to all-`True`).
- **`View.members`** — `list[bool]`, the per-View live mask; replaces `View.stackIndex`.
- Rule everywhere: `active = [i for i, on in enumerate(members) if on]`. `len(active) == 1` →
  that member's native dataset; `> 1` → aggregate over the subset; `== 0` → forbidden.

## Render path (why C++ is untouched)

`View → Dataset.render → channel.tile`. `MeanPower.tile`/`StackCoherence.tile` build the C++
member vector from the `members` they are handed, then call `qed.libqed.nisar.stack.meanpower`
(`lib/qed/nisar/stack/meanpower.h`), which already reduces over *whatever vector it is handed*.
A subset is just a shorter vector — so the subset logic is pure Python and the C++ engines need
no change. The aggregate `Dataset` is shared across all Views (built once in
`Stack._loadDatasets`), so per-View membership must be threaded down at render time, never
stored on the shared dataset: `Dataset.render` resolves the participating members (full list, or
the mask's subset) and names them explicitly to the channel, which has no fallback of its own.

## Wave 1 — the spine

1. **`pkg/stacks/Stack.py`** — add `membership` trait; in `__init__` resolve `self.defaultMask`
   (empty ⇒ all `True`, preserving `readers` order, guard all-`False` → all-`True`).
2. **`pkg/readers/nisar/products/channels/MeanPower.py` + `StackCoherence.py`** —
   `tile(self, source, …, members, **kwds)`: build `sources` from the required `members` list;
   no `source.members` fallback (render always names them).
3. **`pkg/stacks/Dataset.py`** — `render(self, channel, …, mask=None, **kwds)`: resolve
   `members = self.members if mask is None else [m for m, on in zip(self.members, mask) if on]`
   and pass it explicitly to `channel.tile`. `_collectStatistics` stays over the full set for
   now (known limitation, see below).
4. **`pkg/ux/View.py`** —
   - trait `stackIndex` → `members` (`list[bool]`);
   - `pyre_configured`: seed `self.members = list(reader.defaultMask)` when the reader is a stack
     and the mask is unset;
   - `setStackIndex(index)` → `setMembers(members)`: validate length and reject empty, store,
     `resolve()`, new `session`;
   - `_pinnedDataset` → `_effectiveDataset`: branch on `len(active)` (`== 1` reuses the existing
     member-swap path with `active[0]`; else the aggregate stands);
   - `availableSelectors`: same branch;
   - render dispatch: pass `mask=self.members` into `dataset.render` when the aggregate stands;
   - `clone()`: `members=list(self.members)`.
5. **`pkg/ux/Viewport.py` + `pkg/ux/Store.py`** — `setStackIndex` → `setMembers` forwarders.
6. **GraphQL** — `pkg/gql/views/View.py`: `stackIndex` → `members` (`[Boolean!]`), rename
   resolver; rename `SetStackIndex.py` → `SetMembers.py` (args `members: [Boolean!]!`); update
   `views/__init__.py` and `Mutation.py` (`viewSetMembers`).
7. **Client** — `useSetStackIndex.js` → `useSetMembers.js` (mutation `viewSetMembers`, same
   updater/fragment-spray/`pending` guard); `context.js` (`stackIndex` → `members`); `stack.js`
   (row of toggle buttons styled like the NISAR band/frequency/polarization selectors; flip bit
   *i* and commit the full mask; no-op when *i* is the only active member; keep the
   `stackExtent < 2` early return).

## Wave 2 — convenience actions

**Reset** is the only part with a server side, and it **landed**: `View.resetMembers`
(restores `reader.defaultMask` via `setMembers`) → `Viewport`/`Store` forwarders →
`viewResetMembers` resolver and SDL mutation. The default stays server-internal; **no
`Reader.defaultMask` is exposed** (an earlier draft did; it was backed out — the client never
needs the default).

**All** (all `True`) and **Invert** (flip, with the empty-set guard) are pure client computations
over the current mask. "None" is omitted — the empty set is forbidden.

The client UI for all three (`action.js`, `useResetMembers.js`, the actions row in `stack.js`)
was built, then **backed out** so we can demo the raw per-member toggles first. Re-wiring is
purely client work against the already-present `viewSetMembers` / `viewResetMembers` mutations.

## Tests

Landed (`tests/qed.pkg`, stand-in based, no NISAR data needed):
- `stacks.py` — `Stack._resolveMask` (empty ⇒ all, named subset, order preserved, no-match
  fallback) and `Dataset.render(mask=…)` (subset selection + no-mask full-list passthrough).
- `membership.py` — `View._activeMembers` (mask → indices) and `View.setMembers` (empty-set
  rejected; real mask stored and re-resolves).

> Gotcha learned here: pyre components are keyed by name — reusing a component name returns the
> cached instance, so each test dataset needs its own name (this silently fed an old dataset's
> members into a later test).

Deferred until we synthesize a NISAR stack fixture (need a real stack reader):
- `_effectiveDataset` single-member swap to native channels; `availableSelectors` widening;
  `setMembers`/`resetMembers` → `resolve` across the single-member boundary; the end-to-end
  mean-power/coherence subset render with real data; the `viewSetMembers`/`viewResetMembers`
  GraphQL round-trips; the `tests/qed.ux.playwright` driveability test.

## Automation surface tie-in

Each member toggle carries stable identity in `data-qed-stack-member` (the index) with its
participation state in ARIA `aria-checked` — following the codebase convention (see
`coordinate.js`) that identity lives in `data-*` and state lives in ARIA, never mirrored into
`data-*`. The member group is `data-qed-control="stack"`. Per-member targets are far more
driveable than the old slider geometry and slot directly into the automation-surface work — the
reason this redesign precedes it.

## To confirm during implementation

1. **Re-seed on reader switch** — `pyre_configured` covers the initial bind; verify the runtime
   reader-change path re-seeds `members` (or seed lazily on first access if it bypasses the hook).
2. **Subset-aware stats** — deferred; the color range is computed over all members, so a subset
   may stretch slightly off. Same class as the existing center-sample limitation; flagged, not
   silent.
3. **Trait identifier form** — resolved: `Stack.membership` lists member *names*, matched
   against each member reader's `pyre_name` in `_resolveMask` (robust to yaml reordering).

<!-- end of file -->
