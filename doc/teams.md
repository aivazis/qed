<!--
-*- markdown -*-
-*- coding: utf-8 -*-

michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# Teams

The qed server does its heavy work in worker processes, organized in teams. This note lists the
processes a server runs, the teams it forms and when, the units of work each team carries out,
and the words used for all of them in the code, the configuration, the GraphQL surface, and the
other notes. `doc/crews.md` explains why the teams are divided the way they are; this note
describes what they are.


## The processes

A running server is one process with one event loop, and every other process descends from it.

- **The server** answers HTTP requests, owns the store, the fleet, and the tile cache, and runs
  every team's side of the conversation with its members on its event loop. It never renders a
  tile or reads a product.
- **The helper** is spawned while the server activates, from the server's own command line, as
  `qed --shell=forkserver`. It loads the same code and configuration as the server and does
  nothing but fork members on request, so every member is a copy of the application as it started,
  and not of the server after it has touched a product. The helper reaps the members it forks and
  reports their exits to the server.
- **The members** are the worker processes. Each is forked by the helper for one team and stays
  with it until the team lets it go. A member has one thread; it talks to its team over a unix
  socket pair, which carries tasks one way and reports the other, and rendered tiles as open file
  descriptors; its journal travels over a second channel and is replayed in the server, so its
  entries reach the terminal and the browser.

A process that measures with `qed measure` plays the part of the server: it forms the teams,
starts the helper, and runs the members' side of the conversation on its own event loop.


## The fleet

The fleet, `qed.nexus.fleets.tile`, is the server's registry of teams. There is one per server,
configured as `{server}.fleet`, which is `qed.app.nexus.services.web.fleet` for the web shell.
It forms each team the first time it is needed, hands every team it forms its recruiter,
`{fleet}.recruiter`, and owns the cache of rendered tiles, `qed.nexus.caches.tile`, configured as
`{fleet}.cache`, which all the tile teams share. The server sets the fleet's recruiter to
`qed.nexus.forkserver`, which asks the helper for members, at a priority that configuration
overrides; the default elsewhere is `qed.nexus.fork`, which forks members from the process that
forms the team.


## The teams

Each team is a pyre staff: a standing team of members that parks the idle ones, replaces the ones
that die, and delivers the outcome of each task to whoever asked for it. The fleet forms three
kinds.

| Team | Class and family | Serves | Formed | Members | Configured as | GraphQL `kind` |
|------|------------------|--------|--------|---------|---------------|----------------|
| tile team | `Team`, `qed.nexus.teams.tile` | one reader | with its first tile | 4 | `{fleet}.{reader}` | `tile` |
| builders | `Builders`, `qed.nexus.teams.build` | one reader | with first contact, and with each build | 16 | `{fleet}.{reader}.builders` | `build` |
| scouts | `Scouts`, `qed.nexus.teams.archive` | one archive | with its first listing | 1 | `{fleet}.{archive}` | `scout` |

- **The tile team** renders the tiles a client asks for at full resolution, which revisit the same
  chunks as the user pans. Its members open the product with the reader's page buffer and a chunk
  cache of 256 MiB for each dataset. It is small and long lived.
- **The builders** make first contact with a product and build the pyramids of its rasters,
  reading every page of the product once. They open the product with a page buffer of 16384 pages
  of 4 KiB, 64 MiB, and the library's chunk cache. They are large and short lived: the store
  releases them once a survey is in and none of the reader's datasets is being built, and the next
  build brings them back.
- **The scouts** list the folders of an archive for the tree the client shows. An archive's
  listings are slow, e.g. a bucket or a catalog query, so they run on a team of their own and never
  hold up a tile.

A team stamps each task with the budgets of its caches, `pages` and `chunks`, and a member applies
them to the reader it opens for the task, for the settings the reader has.

The server's GraphQL surface lists every team under `server { fleet { teams } }`, with its `name`,
`kind`, `owner` (the reader, or the archive of a team of scouts), `size`, and the counts of its
idle, active, queued, and pending work; the heartbeat in the journal reports the same counts.

### Letting teams go

A team that **stands down** sends its members home and recruits nobody in their place; its next
task brings it back to full strength. A team that is **disbanded** sends its members home for good.
Since pyre hands back the same team for the same name, a disbanded team can never work again, so
the fleet stands teams down whenever the same name may come back:

- a reader that is disconnected has its tile team and its builders stand down
  (`Fleet.dismiss`);
- the builders stand down when there is nothing left to build (`Fleet.retire`);
- an archive that is disconnected has its scouts disbanded (`Fleet.recall`), which an archive
  connected again under the same name would trip over; this is an open defect;
- the server disbands every team when it shuts down.


## The units of work

A unit of work is a task, `pyre.nexus.task`; the ones qed defines share the base `Chore`, which
carries the recipe of the reader, so a member can rebuild the reader in its own process, the
credentials of the archive the reader came from, and the budgets its team stamped.

| Task | Team | Does | Hands back |
|------|------|------|------------|
| `Tile` | tile team | renders one tile of a channel of a dataset at a zoom | the tile, in a spool: an unlinked temporary file whose descriptor travels to the server, which sends it to the client with `sendfile` |
| `Survey` | builders | makes first contact with a product and describes its datasets | a `Discovery`, with one `Finding` per dataset, from which the server's reader builds its datasets without opening the product |
| `Decimate` | builders | builds one run of tiles of one level of a pyramid, for its dataset and for the rasters read with it, writing them into the level's file; level one reads the product, every level above reads the level below | a record per tile of whether it holds anything, and the pages it fetched |
| `Listing` | scouts | lists one folder of an archive | a `Manifest` of the folder's entries |

A **build**, `qed.nexus.build`, is not a task: it lives in the server, lays out the levels of the
pyramid of one raster, hands its runs to the builders as `Decimate` tasks, keeps track of which
tiles hold anything from their records, and commits each level once its runs have all reported,
before it hands out any run of the level above. A dataset's build leads the builds of the rasters
it is read with, so their first levels are built in the same runs and the pages of the product
they share are fetched once.


## Words

- **fleet**: the server's registry of teams, one per server.
- **team**: a group of members that serves one reader or one archive; the fleet forms three kinds,
  the **tile team**, the **builders**, and the **scouts**.
- **member**: one worker process of a team. In pyre, the class of a member is `pyre.nexus.crew`,
  and a member is a *crew member*.
- **crew**: used loosely, in these notes and in `qed measure`, for a team or for its members; see
  below.
- **helper**: the clean copy of the application that forks every member; also the **forkserver**,
  after the recruiter that talks to it.
- **recruiter**: the strategy a team recruits its members with; `fork` forks them from the team's
  process, `forkserver` asks the helper.
- **task**, **chore**: a unit of work; `Chore` is qed's base for the tasks that open a product.
- **workplan**: a team's queue of tasks not yet handed to a member.
- **run**: a stretch of tiles of one pyramid level that one `Decimate` builds.
- **budget**: the page buffer and chunk cache a team's members open products with.
- **standing down**, **disbanding**: letting a team's members go, so the team can come back, or
  for good.
- **spool**, **discovery**, **finding**, **manifest**: what the tasks hand back, above.


## Open questions of naming

- **Crew.** pyre's `Crew` is one member, while `qed measure` reports "a crew of 16" and
  `doc/crews.md` speaks of crews as teams. One of the two meanings should go; *team* and *member*
  say both without ambiguity.
- **The builders and the scouts** go by several names: `Builders`, the build team,
  `qed.nexus.teams.build`, `{reader}.builders`, and the GraphQL kind `build`; `Scouts`,
  `qed.nexus.teams.archive`, and the kind `scout`. The families do not end with the names the
  classes are published under, which the family naming pass on the to-do pile is about.
- **The tile team** has no name of its own in its configuration, `{fleet}.{reader}`, while the
  builders of the same reader are `{fleet}.{reader}.builders`.


<!-- end of file -->
