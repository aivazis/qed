<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# The server through GraphQL

This note describes the part of the GraphQL schema that shows what the server itself is doing:
its process, the requests it is holding, its tile cache, its crews, the pyramids it is building,
its workspace, and eventually its configuration. The client uses it to drive behavior that
depends on the state of the server, e.g. which zoom levels to offer; people use it to see why the
server behaves the way it does; tests and measurements use it to wait for the server instead of
guessing.

Most of this is known to the server today and reaches nobody but its log: the heartbeat line
reports descriptors, parked requests, the tile cache, and the roster of every team; the tile
trace reports how each tile was served and what it cost. The schema below makes the same
information available on demand.


## Principles

- **Read only first.** The objects below observe. Controls, such as the size of a team or the
  priority of a build, come later, as mutations that follow `doc/graphql-conventions.md`.
- **One object per subsystem**, gathered under a top-level `server` field. Each is resolved from
  the component that owns the information, when it is asked for, with nothing duplicated.
- **Counters are pulled, state changes are pushed.** Counters that change on every request, e.g.
  the hits of the tile cache, are read when a client asks. Changes of state, e.g. a level of a
  pyramid becoming available, a build finishing, a team changing size, raise the change
  notification the store already sends over the event stream, so clients refetch. Progress
  within a level is announced at a bounded rate.
- **Times are seconds since the epoch**, as floats; durations are seconds.
- **Zoom is a pair.** Anything reported by zoom level carries both axes.
- Names follow `doc/graphql-conventions.md`. A status or a kind is a lowercase string, the way
  `Reader.status` is, rather than an enum.


## The schema

```graphql
type Query {
  server: Server!
}

type Server {
  process: ServerProcess  # missing when the http server is not the qed server
  requests: ServerRequests!
  cache: TileCache        # missing when there is no fleet
  fleet: Fleet            # missing when there is no fleet
  builds: [Build!]!
  workspace: Workspace    # missing when the workspace cannot describe itself
  configuration: [ConfiguredComponent!]!
}
```

### `process`

What the process is and what it holds.

```graphql
type ServerProcess {
  pid: Int!
  host: String!
  platform: String!
  cores: Int!
  memory: Float!          # bytes
  started: Float           # missing until the server is activated
  uptime: Float!
  descriptors: Int         # held; missing on a platform that cannot tell
  ceiling: Int!           # the soft limit on descriptors
  beats: Int!             # heartbeats so far
}
```

Source: the nexus server (`pkg/nexus/Server.py`), which already counts descriptors and beats, and
the host information pyre carries.

### `requests`

The requests the server is holding and the recent traffic.

```graphql
type ServerRequests {
  waiting: Int!           # tile requests parked for a worker
  oldest: Float!          # how long the oldest has waited
  zooms: [ZoomTally!]!
  tiles: [TileTally!]!
}

type ZoomTally {
  horizontal: Int!
  vertical: Int!
  count: Int!
}

# how the recent tiles were served
type TileTally {
  via: String!            # crew, hit, inline, refused, starved, hangup
  count: Int!
  median: Float!          # seconds of wall time
  p95: Float!
}
```

Source: the dispatcher, which already records every tile it serves (`Dispatcher._logTile`) and
counts the zoom levels it is asked for (`Dispatcher.usage`). The tallies cover a window of the
most recent tiles, kept in a ring.

### `cache`

```graphql
type TileCache {
  capacity: Float!        # bytes
  slots: Int!             # the most entries it may hold
  entries: Int!
  bytes: Float!
  hits: Int!
  misses: Int!
}
```

Source: `pkg/nexus/Cache.py`, whose census line the heartbeat prints.

### `fleet`

```graphql
type Fleet {
  teams: [Team!]!
}

type Team {
  name: String!
  kind: String!           # tile, build, scout
  owner: String!          # the reader, or the archive of a team of scouts
  size: Int!
  idle: Int!
  active: Int!
  queued: Int!            # tasks in the workplan
  pending: Int!           # tasks handed out and not yet back
  deaf: Int!
  waking: Int!
}
```

Source: the fleet (`pkg/nexus/Fleet.py`) and each team's census (`Team.census`). Today every
reader has one team, of kind `tile`, which also runs the builds; the `build` kind is for the build
teams of `doc/crews.md`.

### `builds`

The pyramid of each dataset a client has selected. This is what the zoom control needs: a zoom
level is offered once its pyramid level exists for the dataset and every raster it is read with.

```graphql
type Build {
  dataset: String!
  status: String!         # working, seeded, ready, failed
  error: String
  started: Float!
  seeded: Float           # when the view became worth looking at
  finished: Float
  depth: Int!             # the deepest level the build will make
  reach: Int!             # the deepest level available for every raster
  rasters: [RasterBuild!]!
}

type RasterBuild {
  raster: String!
  depth: Int!
  reach: Int!             # the deepest level available, counting from level one without gaps
  level: Int              # the level under construction, if any
  runs: Int!              # the runs of that level
  outstanding: Int!       # the runs of that level not yet back
}
```

`View` gains `build: Build`, the build of the dataset it shows, so the client can follow its own
view without searching the list.

Source: the store's preparation records and the builds behind them (`pkg/ux/Store.py`,
`pkg/ux/Preparation.py`, `pkg/nexus/Build.py`), and the pyramids, which know which levels they
hold (`Pyramid.holds`). The record keeps its pyramids after the builds are done, so `reach` stays
answerable.

A level becoming available and a build changing status are announced. Progress within a level
changes `outstanding` on every run that reports, and is announced at most a few times a second.

### `workspace`

```graphql
type Workspace {
  path: String!
  products: [WorkspaceProduct!]!
}

type WorkspaceProduct {
  kind: String!           # the kind of derived data, e.g. pyramids
  name: String!           # the product, by its granule id or a digest of its address
  bytes: Float!           # on disk, counting only the blocks that were written
}
```

Source: the workspace (`pkg/workspaces/Local.py`) and the folders of the pyramids in it. Computing
the bytes walks the folders, so it happens only when asked.

### `configuration`

The effective configuration of the server: every component reachable from the application
through its traits, the value of each trait, and the source that set it.

```graphql
type ConfiguredComponent {
  name: String!
  family: String
  traits: [ConfiguredTrait!]!
}

type ConfiguredTrait {
  name: String!
  kind: String!           # property, facility
  schema: String!
  value: String           # missing when the trait is secret, or has no value
  secret: Boolean!
  priority: String        # the category of the source of the value: defaults, user, command...
  locator: String         # where exactly the value came from
  components: [String!]!  # the components the value refers to, by name
}
```

`Server.configuration` is a list of `ConfiguredComponent`, starting with the application. The walk
follows every trait whose value is a component, or a list, a tuple, a set, or a dictionary that
holds components. Nothing in pyre prevents a component from reaching, through its traits, a
component that reaches back, so the walk describes each component once, in the order it reaches
it, and every other mention of it is a reference by name.

A trait whose value must not be shown, e.g. a credential, is marked secret where it is declared,
`credentials.secret = True`, and its value is never reported. pyre's own displays of a
configuration withhold it too. Source: `qed.ux.configuration` (`pkg/ux/configuration.py`), over
pyre's inventory, which knows the priority and the locator of every value.


## Order of work

1. `builds`, with `View.build` and the announcements; the zoom control of `doc/crews.md` depends
   on it.
2. `fleet`, `cache`, and `process`, which are views of information the heartbeat already gathers.
3. `requests`, which needs the ring of recent tiles in the dispatcher.
4. `workspace`.
5. `configuration`.

Each step adds its tests to `tests/qed.pkg`, resolving queries through the dispatcher the way
`tests/qed.pkg/graphql_chunks.py` does. What needs Linux, or a product in S3, is checked on lambda
and on the On-Demand system.


<!-- end of file -->
