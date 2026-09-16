<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# data archives: moving their state to the server

> **Status, 2026-09-10.** An assessment, written before any code. It records where the state of a
> connected archive lives today, what it would take to move it to the server so it can be
> persisted and shared, and how a refresh fits once it is there. The open questions at the end
> are decisions, not gaps in the survey.

## 1. What an archive is today

An archive is a `qed.archives` component with one trait, `uri`, and one obligation,
`contents(uri)`, which lists the folders and files at a location inside the archive
(`pkg/protocols/Archive.py`). There are three flavors:

- **local** (`pkg/archives/Local.py`): mounts a `qed.filesystem.local` over the root at
  construction and answers `contents` by re-discovering one level along the path and then the
  target folder itself. Folders first, then files, each sorted; dot entries hidden unless `all`.
- **s3** (`pkg/archives/S3.py`): mounts a `qed.filesystem.s3` over the bucket, discovering one
  level eagerly at connect time; `contents` re-discovers the requested folder. Not sorted. Its
  `credentials()` freezes the boto3 session for the readers.
- **earth** (`pkg/archives/EarthAccess.py`): no tree at all. `contents` ignores its argument,
  runs `earthaccess.search_data` with the archive's filters, and yields one flat file per
  granule as an `s3:` uri. Every call is a fresh remote search.

Both filesystems prune entries that vanished since the last discovery (`pyre.filesystem.Local`
and `S3.discover` both keep a `dead` set), so re-discovery is an honest refresh, not a merge.

## 2. Where the state lives now

**On the server, already:**

- The list of connected archives: `Store._dataArchives`, an `Archives` catalog keyed by the
  uri string (`pkg/ux/Archives.py`), seeded at boot from the plexus `archives` trait, whose
  default is one local archive rooted at the launch directory (`pkg/shells/Plexus.py:28`).
  `connectArchive`, `connectEarthAccessArchive`, and `disconnectArchive` mutate it in memory.
- The archive list is on the app query (`QED.archives`), and every successful mutation
  broadcasts the SSE change frame (`pkg/ux/GraphQL.py:119`), so a connect on one client already
  shows up on every other client. The list is shared; it is just not persisted.
- The filesystem node tree hanging off each archive, `self.fs`. It is a cache of everything
  ever discovered, for the life of the archive, and nothing reads it except `contents`.

**Only on the client:**

| state | where | lost when |
|---|---|---|
| which folders are expanded | one `useState` per `Tray` (`ux/client/widgets/tray/tray.js:34`) | the tray collapses, the route changes, the page reloads |
| the listings of expanded folders | the Relay store, root field `contents(archive, path)`, fetched by `useQueryLoader` on mount with `store-and-network` (`views/explorer/archives/directory.js`) | the query ref is disposed, which is when the tray collapses |
| which archive and file are "selected" in the explorer | a client `views` array in the explorer context (`views/explorer/explorer/context.js:36`) | leaving `/explore` |
| connect-form contents | `useState` in `archive/local.js`, `s3.js`, `earth.js` | leaving the form |

Nothing is persisted browser-side either; the only `localStorage` key is the automation flag.

**Persisted nowhere:** the `views` and `archives` traits are boot seeds. Nothing writes back.
`viewPersist` exists as a mutation and calls `Store.pyre_dump`, which prints a report and
touches no disk (`pkg/ux/Store.py:1450`). So the hook for "persist the session" is already
named and wired; it has no body.

**Refresh today:** there is none. The server re-discovers on every `contents` call, so a
listing is fresh on mount, and the only way to get a fresh one is to collapse and re-expand a
folder. The live-sync refetch re-issues only the app query, which does not include `contents`,
so a file that appears on disk inside an expanded folder is invisible to every client until
each of them collapses and re-expands it.

Collapsing a folder unmounts its whole subtree, so re-expanding a deep path costs one round trip
per level and loses the expansion state below it.

## 3. The proposal: the tree is server state

The central move: **an archive's view, meaning the set of expanded folders and their listings,
becomes server state, carried by the app query.** Once it is, persistence, sharing, and refresh
all fall out of machinery that already exists.

- Persistence is writing the store's archives, expansion included, to a record beside the
  work, and reading it back at boot.
- Sharing is free: the change frame after every mutation already makes every live client
  refetch the app query, and the tree rides on it.
- Refresh is a mutation that re-discovers the expanded folders and broadcasts.

This also aligns with a decision pinned in `doc/staging.md`: the app query stays monolithic and
must be **passively answerable**. Today the `contents` query does discovery inside a resolver.
In the proposal, discovery happens only inside mutations (expand, refresh); the query resolvers
read the archive's node tree and never touch the filesystem or the network.

### 3.1 Server model

- The archive protocol grows a trait, `expanded`, the list of folder uris on display. As a trait
  it is configurable, so a `qed.yaml` can pre-expand a folder, and it serializes with the rest of
  the archive's state, which is what persistence needs.
- The base archive gains the tree operations the store delegates to: `expand(uri)` discovers the
  folder and records it; `collapse(uri)` forgets it and every folder beneath it; `refresh()`
  re-discovers every expanded folder, root included; `listing(uri)` reads the node tree of an
  expanded folder without discovering. `contents` stays as the primitive the flavors implement.
- **earth** implements the same interface over search results, with the hierarchy of section
  3.6 imposed on them. Today's behavior of re-searching on every expansion goes away, which is
  the point.
- The store keeps the catalog it has and adds `expandFolder`, `collapseFolder`,
  `refreshArchive`, each returning the archive so the mutation payload can carry it.
- **Built 2026-09-15.** A listing is a `qed.nexus.listing` task: a chore that carries the
  archive's family and recipe and the folder uri, mounts the archive on the worker from the
  recipe, keeps it in the crew member's archive registry, and returns a `qed.nexus.manifest`.
  Each archive gets its own team of scouts, `qed.nexus.scouts`, a team flavor of one member,
  keyed by archive name and disbanded on disconnect; `Fleet.browse` routes to them. Without a
  fleet the listing runs in the server process. A failed listing leaves the folder on display
  with its reason recorded, the way a failed survey does.

### 3.1.1 The archive is a pyre filesystem

The local and s3 archives are already thin wrappers over `pyre.filesystem`: each mounts one at
construction, and `contents` is `folder.discover(levels=1)` plus a partition of `folder.contents`.
`Folder.resolve(path)` already descends one level at a time discovering as it goes, which is the
loop `Local.contents` reimplements. Every discovered node carries a `sync` timestamp in its
`Info`, so the filesystem already records what has been discovered and when. The tree operations
in 3.1 are therefore the filesystem's own API: expand is `resolve` then `discover(levels=1)`,
listing is `folder.contents`, refresh is `discover` over the expanded folders, collapse drops a
folder's contents, and the `sync` stamp is the "last refreshed" the UI can show.

Two consequences worth taking:

- **earth becomes a filesystem too.** A `Filesystem` subclass whose `discover` runs the search
  and attaches one node per granule, with the `s3:` uri in the node's `Info`. Then every flavor
  is a name plus a mounted filesystem, the base archive implements the whole tree interface once
  over the filesystem API, and `contents` disappears from the protocol.
- **The catalog can be a filesystem.** `Folder.mount(uri, filesystem)` inserts a whole
  filesystem as a node, and `discover` dispatches to the owning filesystem, so the store's
  archives could hang off one virtual root, `/<name>/...`, giving the session one uri space and
  `find(pattern)` for free. Optional; the archive-as-filesystem move stands on its own.

Nothing in pyre serializes a filesystem (`Node.dump` is a debugging tree print), and that is
fine: what persists is the archive's spec plus its `expanded` list, never the node tree. The
wrinkle is boot: a persisted expansion has to be re-discovered before the app query can show it,
and boot is pinned to do nothing. Either the expanded folders are discovered at boot, one
catalog read per folder, or they load marked stale and the first refresh fills them.

**Built 2026-09-15.** The tree lives in two places, by process. Where an archive is mounted,
on a crew member, or in the server when no fleet is attached, it is a pyre filesystem and
`contents` walks it; the earth archive mounts `pyre.filesystem.earthaccess` with a layout that
hangs granules under their stack and acquisition date, both read off the granule id by the
grammar of 3.8. Where the tree is kept, in the store, an archive holds its `expanded` list and
a table of manifests, one per folder on display: the `(name, uri, isFolder)` entries the
listing returned, the moment it was taken, and the catalog count for query backed archives. A
worker ships a manifest back the way a survey ships a discovery record, so the store mounts
nothing, and `Archive.items` is read off the manifests. Each folder on display also records
whether its listing is under way and, when it failed, why. Persistence needs only the spec and
the `expanded` list, as above; a persisted expansion boots pending and its first listing fills
it.

### 3.2 GraphQL

- `Archive` gains `items: [Item]`, a **flat** list of every item in every expanded folder, with
  `Item` gaining `parent: String` and `expanded: Boolean`. Flat rather than recursive because
  Relay fragments cannot recurse; the client rebuilds the nesting from `parent`. The root's items
  have the archive uri as parent.
- Mutations, per `doc/graphql-conventions.md` (session-level, verb-first, single input, payload
  named for the entity): `expandFolder(input: {archive, uri})`, `collapseFolder(input: {archive,
  uri})`, `refreshArchive(input: {uri})`, each returning `{ archive { ...items } }`.
- The `contents` query is retired once the client no longer issues it. `useFetchDirectoryContents`
  (the `useLazyLoadQuery` variant) is dead and broken already and goes with it.
- **Built 2026-09-15.** `Item` carries `parent`, `expanded`, `pending`, and `error`; `Archive`
  carries `items`, its root's `expanded`, `pending`, and `error`, and `hits`. The three
  mutations are registered. `contents` still answers, with its items described the same way.

### 3.3 Client

- The explorer fragment on `QED` selects `archives { ...items { parent expanded } }`. `Directory`
  and `Contents` render from the fragment instead of loading a query on mount; the busy fallback
  moves to the mutation's in-flight state.
- `Tray` gains a controlled mode (`expanded` and `onToggle` props) beside its local-state mode,
  which the sync and viz trays keep. Archive and folder trays become controlled, and toggling
  fires the mutation.
- A refresh badge on the archive header fires `refreshArchive`. The connect and disconnect
  updaters that hand-edit `QED.archives` can stay for immediacy; the refetch after the change
  frame reconciles either way.
- What stays client-side, deliberately: the connect forms and the explorer's transient
  selection. They are per-user gestures in progress, not session state. See open question 2.

### 3.4 Persistence

- The record lives in the workspace, `{workspace}/.qed/session.yaml` or similar, via the
  workspace component that already owns everything qed keeps (`pkg/workspaces/Local.py`). That
  is the directory the user launched from, so the record sits beside the work, travels with it,
  and is deleted with it. Copying or committing the directory shares it.
- Written on every archive mutation, and by `viewPersist`, which finally gets a body. Read at
  boot after the configuration file, through the same `_drain` path that already resolves the
  `archives` trait entry by entry and survives a bad one.
- **Decided 2026-09-10:** the user's `qed.yaml` is the record. Users declare their archives
  there, as `sandbox/archives/qed.yaml` already does, and qed augments that file in place with
  what the session adds: connected archives, expansion, and whatever else persists. There is no
  separate session file, and `pfg` is not supported for persistence.
- Augmenting in place needs a round-trip yaml editor. PyYAML cannot do it: it drops comments,
  flow style, and blank lines (verified with 6.0.3, and its issue #90 has been open since 2017).
  `ruamel.yaml` can (0.19.1, already in the environment, `YAML()` instance API since the
  module-level functions are deprecated). `yamlrocks` (0.6.1, Rust core, byte-for-byte round
  trip) would also do, but it has no conda-forge package, so it is not a backend (decided
  2026-09-15). Support is conditional: with `ruamel.yaml` importable the file is edited in
  place; without it, the archives load from the file as they do today and nothing is written
  back. Reading stays on the PyYAML loader pyre already uses.
- The document is edited by key path, never regenerated: an archive that came from the file
  keeps its section and its comments and gains an `expanded` key; a new archive gets a new
  section and an entry in the `archives` list; a disconnected one loses both. Credentials are
  never written; an s3 archive persists its `profile` and `region`, which is what re-creates
  the session.
- **Decided 2026-09-10:** the reusable parts live in pyre, see section 3.7.
- Precedence at boot is open question 1.

### 3.5 Tests and the facade

- `tests/qed.pkg`: a local archive over a scratch tree. Expand a folder and see its listing;
  add a file on disk, and the listing does not change until refresh; refresh sees it; delete it,
  refresh prunes it; collapse forgets the subtree; a session record round-trips through a fresh
  store. There is no `Archives` catalog test today, so one comes with it.
- `window.qed.archives()`, `expandFolder`, `collapseFolder`, `refreshArchive` on the facade,
  and a playwright spec that connects a scratch directory of its own. The destructive-disconnect
  hazard that kept archives out of the facade goes away when each spec owns its archive.

### 3.6 earthaccess: the actual layout, and the hierarchy to impose

Measured 2026-09-10 against CMR through `earthaccess` 0.18.0, from this machine:

- CMR knows 42 cloud-hosted collections matching "NISAR", of which qed can read the product
  ones: `NISAR_L{0B,1,2}_{RRSD,RSLC,GSLC,GCOV,GUNW,RIFG,RUNW,ROFF,GOFF}_{BETA,PROVISIONAL}_V1`,
  plus soil moisture, urgent-response, and ancillary collections it cannot.
- A collection holds six figures of granules: RSLC provisional 102,217; GCOV provisional
  100,452; GSLC 99,858; GUNW 54,149; L0B 35,100; the beta collections 23,000 to 24,000 each.
  An unfiltered listing is not a listing.
- A granule record carries what a hierarchy needs, in `AdditionalAttributes`: `TRACK_NUMBER`,
  `FRAME_NUMBER`, `ASCENDING_DESCENDING`, and `STACK_ID` (`004_A_018`, track, pass direction,
  frame, which is the interferometric stack identity), plus the polarizations, bandwidths,
  product version, and a `TemporalExtent`. The granule name encodes the same fields:
  `NISAR_L2_PR_GCOV_004_004_A_018_4005_DHDH_A_20251029T111130_20251029T111153_P05023_N_P_J_001`,
  with the cycle as field 4 and the track, direction, and frame as fields 5 to 7.
- A granule is 4.5 GB and ships one `s3://sds-n-cumulus-prod-nisar-products/<collection>/
  <granule>/<granule>.h5` direct link, an https twin, and six browse PNGs.
- The query builder filters on `short_name`, `concept_id`, `temporal`, `bounding_box`,
  `polygon`, `point`, `line`, `circle`, `granule_name` (with wildcards), `orbit_number`,
  `revision_date`, `version`, `provider`, `daac`, and `cloud_hosted`; anything else goes through
  `parameters`. There is no faceting: CMR cannot list the distinct tracks or frames of a
  collection, only count and page the granules matching a filter.
- Filtered queries are cheap. GCOV over the sandbox's Crete polygon: 47 granules, a `hits()`
  count in 0.3 s, the full page in 0.7 s. Those 47 group into 9 stacks of 1 to 6 granules, 17
  acquisition days, and 7 cycles. A `granule_name` pattern for one track, direction, and frame
  answers in 0.3 s.

The story, then. An earthaccess archive is a **query**, and its tree is the query refined:

- The root is the archive's own filters. **Decided 2026-09-10: an unfiltered listing is
  refused.** A collection alone is not a filter; the archive must also carry a spatial or a
  temporal constraint, or a granule pattern, before it lists anything, and an archive without
  one connects but reports why it is empty. A `count` cap bounds every listing, and the root
  reports `hits()` so the user sees "showing 500 of 2,000" and narrows the filters rather than
  pages.
- Below the root, folders are groups of the fetched page rather than further queries, because
  CMR cannot enumerate groups. Stack first: the first level groups granules by `STACK_ID`,
  which is track, pass direction, and frame, so every granule in a folder images the same
  footprint on a different date, which is what a user interferes across; the second level is
  date. This is CMR's interferometric stack, not qed's dataset stack, though a stack folder is
  exactly what a qed stack reader would take. Date first, with stacks beneath, is the
  alternative, and a trait can choose.
  Leaves are granules, one file each, with the `s3:` uri in the node's `Info` along with size,
  time range, polarizations, and the browse links, all of it already in the record.
- Refresh re-runs the query. Expanding a folder costs nothing, since the page is in hand.
- **Decided 2026-09-10:** the filters become traits of the earthaccess archive itself, one
  per query-builder parameter (`collection`, `conceptId`, `count`, `pattern`, `begin`, `end`,
  `bbox`, `point`, `circle`, `line`, `polygon`), so a `qed.yaml` section reads as a query and
  the separate `qed.archives.filters` components, the `ArchiveFilter` protocol, and the visitor
  dispatch that assembles them go away. The connect form and the
  `ConnectEarthAccessArchiveInput` already have this flat shape.

### 3.7 What goes to pyre

**Decided 2026-09-10:** the parts other projects would want live in pyre, not qed.

- **Filesystem persistence.** A pyre filesystem learns to serialize the discovered part of its
  tree and rehydrate from the record: which folders were discovered, their `sync` stamps, and
  per node the `Info` a flavor chooses to keep (for a local filesystem nothing beyond the
  layout; for earthaccess the granule fields above). The snapshot answers the boot wrinkle of
  3.1.1: a persisted expansion loads populated from the record, marked with the stamp of its
  last discovery, and the first refresh brings it current, so boot still touches nothing.
  Rehydration builds a virtual filesystem from the record and the flavor's `discover` replaces
  it level by level.
- **An earthaccess filesystem.** `pyre.filesystem.earthaccess`, the search-backed flavor of
  3.1.1, beside `local`, `s3`, `zip`, and `hdf5`; qed's archive just mounts it.
- **A round-trip yaml editor.** A codec-level `encode` that pyre's config layer lacks
  (`Codec.encode` is a stub): open a yaml document, set or delete a value by key path, write it
  back with everything else untouched, over `ruamel.yaml`, and report itself absent when the
  package is not importable. The backend is a seam, so another package can be slotted in later. qed's "augment the user's file" is a
  client of it.

The archive tree operations, the `expanded` trait, the GraphQL surface, and the client stay in
qed.

### 3.8 What comes from qef

`~/dv/qef` holds the complete NISAR granule definition, and the user has cleared cannibalizing
it until qef and qed learn to interoperate, which is on the pile. What the earth archive takes:

- **The granule id grammar**, `pkg/qef/missions/nisar/daac/`: a `tokens/` package where every
  field of a granule id is a pyre trait that also knows its lexer (`Numeric` with a width and a
  range, `Discrete` with its allowed values, `ERT` for `YYYYMMDDTHHMMSS` timestamps), and
  descriptor components (`Single` for RSLC, GSLC, GCOV, SME2; `Pair` for RIFG, RUNW, ROFF,
  GUNW, GOFF; plus RRSD, RRST, HST_DRT, Daphne) whose `sequencer` lists the tokens in id order.
  The `Descriptor` metaclass composes the regex from the lexers, and `Registrar.parse` picks the
  descriptor from the product field, so `daac.descriptor(granule=gid)` yields an object with
  `cycle`, `track`, `direction`, `frame`, the bandwidths, the polarizations, `begin`, `end`,
  fidelity, coverage, and a `gid` that round-trips. The live ids of 3.6 have exactly the shape of
  the sample ids in qef's own `tests/qef.pkg/missions/nisar/daac/descriptor.py`
  (`P05023` is environment, phase, major, minor, patch; `4005` is the two bandwidths), and the
  grammar round-trips live GCOV, GUNW, and RRSD ids from CMR: the GUNW pair parses with its
  reference and secondary cycles, and the RRSD with no frame, as their descriptors say.
- **What the grammar buys.** The stack identity, track plus direction plus frame, and the date
  come from the id alone, so the earth filesystem never has to trust CMR's
  `AdditionalAttributes`, and the same grouping applies to a local or s3 folder of granules,
  which the browser can then fold into stacks too. For pair products the stack is the same
  triple and the date level uses the reference acquisition, which is what `Pair.mark` already
  says.
- **`daac.Filter`**: builds a regex from partial token values, track or frame or direction or
  begin, with every unspecified token's lexer filling the gaps. CMR's `granule_name` filter takes
  wildcards, and the same partial specification renders as one, so a stack folder can be a
  query as well as a group, which is the escape hatch when a filtered page is still too large.
- **The canonical layout**, `missions/nisar/archives/Canonical.py`: the ops bucket
  `s3://nisar-ops-rs-fwd/products/` is laid out as `{stage}_{band}_{product}/{yyyy}/{mm}/{dd}/
  {gid}/{gid}.h5`, and `scrape` walks it a level at a time with the pyre filesystem, the same
  way qed's s3 archive browses. That layout is a second, date-first hierarchy over the same
  granules, worth knowing when the grouping question is settled.

Cannibalized form: lift `daac/` (tokens, descriptors, `Registrar`, `Filter`) into qed as
`pkg/readers/nisar/daac/`, with the descriptor and filter tests, and have the earth filesystem
name its nodes by gid and keep the descriptor in each node's `Info`. When the interop lands,
the copy becomes an import and nothing else moves. qef's own archive protocol is a different
concept, `locate` and `download` by descriptor rather than `contents`, and stays where it is.

## 4. Sequence

1. **pyre: the earthaccess filesystem.** `pyre.filesystem.earthaccess`, with its tests, on
   the pyre branch `archives`, so that every archive flavor is a name plus a mounted filesystem
   before the tree interface is written. Decided 2026-09-15 to go first; the snapshot and the
   yaml editor stay in step 3.
2. **Server model and schema.** Done 2026-09-15: the `expanded` trait and the manifest table
   on the base archive, the earth archive as a query over the pyre filesystem with the
   NISAR grammar lifted from qef, the listing task and the scouts, the store methods, the
   three mutations, the package tests. The `contents` query stays through this step so the
   client keeps working.
3. **Client.** Done 2026-09-15: the archive fragment selects the tree, `Tray` has a controlled
   mode beside its local one, `Directory` and `Folder` render from the fragment, folder trays
   and the archive header fire the expand and collapse mutations, a refresh badge sits beside
   disconnect, a failed listing shows its reason under the folder, the contents query and its
   hooks are gone on both sides. Live sync refetches once more when a change frame lands while
   a refetch is in flight, since relay would otherwise answer the second frame with the first
   frame's response; listings are fast enough to expose that.
4. **pyre.** Done 2026-09-16: the round-trip yaml editor, `pyre.config.yaml.editor`, built
   by `pyre.config.newYamlEditor`, over `ruamel.yaml`; it reads a document, answers `get`,
   `set`, `delete`, `append`, and `remove` by key path, renders, and saves atomically. What it
   does not touch comes out byte for byte as it went in; a comment block that trails an
   entry moves with the tail of its container, and a new top level section is set apart by
   the blank lines that preceded the old tail. The snapshot was dropped (decided 2026-09-16):
   with the tree kept as manifests, nothing on the store side is a filesystem to snapshot,
   and a persisted expansion boots pending, filled by its first listing.
5. **Persistence in qed.** Archives written back into `qed.yaml` through the pyre editor,
   gated on a backend being present; the boot-time read of snapshots; `viewPersist` given a
   body. The earthaccess filters become traits here too, since the persisted section is what
   they shape.
6. **Facade and playwright.**

Steps 2 and 3 are the migration the request asks for and are independent of the UX redesign of
`/explore` that is on the books; the server model does not care how the tree is drawn, and a
redesign that starts from server state is cheaper than one that has to build it.

## 5. What it costs, and the hazards

- **Discovery on the server loop.** Expand and refresh discover synchronously in the mutation,
  exactly as `contents` does today, so nothing regresses; but an S3 listing or an earthaccess
  search blocks the loop for as long as it takes. This is the same class of problem the staging
  work solved for `open` by moving it to a crew. A first cut keeps discovery on the loop; if a
  remote archive proves slow enough to matter, a survey-style task on a worker is the fix, and
  the shape of the mutations does not change.
- **App query weight.** A deeply expanded archive with large folders adds every item to every
  refetch. Coalescing keeps the count of refetches down, not their size. Worth measuring on the
  granule directories in `~/dv/data` before deciding whether the tree needs its own query.
- **Tray semantics.** Every tray in the app shares one widget; the controlled mode has to leave
  the uncontrolled ones untouched, including their aria contract that the playwright suite
  checks.
- **The stale-list hazard flips.** Today a listing is always fresh on expand. After the move,
  a listing is as fresh as the last expand or refresh, which is what makes it shareable and
  persistable, but the refresh affordance has to be visible enough that nobody is surprised.
- **Two archives, one uri.** The catalog is keyed by uri, so the session record and the
  configuration can only disagree about the same archive by name or expansion, never by
  identity.

## 6. Open questions

1. ~~Precedence at boot.~~ Resolved: there is one file, the user's `qed.yaml`, and qed edits it
   in place. What remains is the smaller question of *which* file when several configuration
   sources contribute archives (a `~/.config/pyre/qed.yaml` and a local one): the proposal is
   to write to the file the archive came from, and new archives to the local one.
2. ~~What is shared.~~ Resolved 2026-09-15: the tree is shared, like the views. Expanding a
   folder on one client expands it on all, and the `expanded` trait is what persists.
3. **Views in the same record.** The persistence step could carry the viewports and readers as
   well, and `viewPersist` suggests that was the plan. In scope now, or a separate step?
4. ~~Discovery placement.~~ Resolved 2026-09-15: on a worker from the start. Expand and
   refresh dispatch a survey-style task to the crew, the way `open` does, and the mutation
   returns the archive with the folder marked in flight; the change frame after the worker
   reports carries the listing to every client. Section 5's first-cut-on-the-loop is withdrawn.
5. ~~The earthaccess grouping.~~ Resolved 2026-09-15: stack first, then date. The refusal of
   unfiltered listings is decided, see 3.6. With the grammar of 3.8 in hand the grouping
   applies to local and s3 folders of granules as well, so it is a property of the browser,
   not of the earth archive.

<!-- end of file -->
