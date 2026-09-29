<!--
-*- markdown -*-
-*- coding: utf-8 -*-

michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# Crews

This note describes how the work a reader generates is divided among worker processes, and what
the census of the NISAR products and the measurements of the pyramid imply for that division. It
is a working document: the broad strokes are agreed, the details are to be refined as the pieces
are implemented and measured. `doc/teams.md` describes the teams as they are, and the words used for
them.


## Where things stand

Each reader has two teams, described in `doc/teams.md`: the builders, sixteen members by default,
make first contact and build the pyramids of its rasters; the tile team, four members by default,
renders the tiles a client asks for at full resolution. Every member is forked by the helper, opens
its own copy of the product, and opens it with the cache budgets of its team, described under
"What is in place" below. The builders stand down once there is nothing left to build.

Before the split, one team per reader did everything, from one workplan served newest first, and
the tiles waited behind the runs of the build. The measurements of the split, next to the data, are
under "Tiles during a build, on teams of their own".


## What the measurements say

**Local data and data in S3 are bound on different things.** A tile from a local product is
computation, and four workers were the best team on 16 cores. A tile from a product in S3 spends
three quarters of its time waiting on the bucket, and the throughput of a team grew all the way
to 16 workers; the construction of a pyramid kept improving to 32, with a serial fraction of
about six percent.

**The unit of fetch is the page.** The HDF5 driver for S3 reads whole pages of 4 MiB, each
holding about four compressed chunks. A page pays for itself only when every chunk it carries is
used. Most products interleave their rasters on the pages: a GSLC polarization read alone moves
1.37 times its bytes and 1.05 times when read with its sibling; the small layers of a GUNW move
4.5 to 9 times their bytes alone and 1.3 times together; a mask read alone moves tens to a
thousand times its bytes, because its chunks are scattered over the pages of the other rasters.

**The page buffer grows as pages are fetched; it is not allocated up front.** Opening a local
GSLC with a 4 GiB page buffer added 4 MiB of resident memory. Reading an 8192 by 8192 block
missed on 92 raw data pages and grew the process by about 370 MiB, the size of those pages. So
the configured size is a ceiling that a worker climbs toward, and a team of N workers may
eventually hold N times as much.

**The default chunk cache holds four chunks.** A complex chunk of 512 by 512 cells is 2 MiB
before compression, and the default cache is 8 MiB. Reading the same block twice from a local
GSLC:

| Block | Chunks | Default 8 MiB: first, again (ms) | 64 MiB: first, again (ms) |
|------------|------|-----------|-----------|
| 512 × 512 | 1 | 2.4, 0.1 | 2.3, 0.1 |
| 1024 × 1024 | 4 | 13.9, 0.6 | 13.8, 0.5 |
| 2048 × 2048 | 16 | 58, 74 | 57, 2.9 |

Once the working set is larger than four chunks, the default cache thrashes and a second read
costs more than the first; sized to fit, the second read is twenty times cheaper. qed does not set
the chunk cache anywhere today.

**The page cache minimizes fetches; the chunk cache minimizes decoding.** Which one matters
depends on the activity, and the activities of a reader are very different from each other.


## Two kinds of team

A reader goes through two phases. At first contact, nothing is known about the product beyond
its metadata, and the work is bulk: survey the file, build the pyramids of its rasters, derive
the thumbnail and the statistics. Once the levels exist, zoomed out views read them through a
memory mapping, and the only work left for a crew is the tiles at full resolution, which revisit
the same few chunks as the user pans.

The two phases get two kinds of team:

- **The build team** starts hot as soon as the reader is known and builds a complete picture of
  the file: the survey, the pyramids of all its rasters, the thumbnail. It streams: every page is
  fetched once, every chunk is decoded once. It needs no chunk cache, and a page buffer only as
  large as the pages of the task it is working on. It is short lived, and can be large: its size
  follows the measurements of the pyramid construction, and it is released when the build is
  done.
- **The tile team** is formed warm, and is ready to serve tiles of the selected dataset when the
  user gets around to panning. It revisits: its chunk cache is sized to the working set of a
  view at full resolution, e.g. a screen of 32 tiles over a complex raster is 32 chunks, or 64
  MiB, and its page buffer holds the pages whose other chunks the neighboring tiles are about to
  need. It is small and long lived.

The fleet owns the memory these caches take. Page buffers and chunk caches are set per kind of
team, as budgets, not left at ceilings that every member of a large team can grow into.


### What is in place

Each reader has both teams. The builders, `qed.nexus.teams.build`, sixteen members by default,
configured as `{fleet}.{reader}.builders`, make first contact and run the pyramid builds; the team
that serves tiles, `qed.nexus.teams.tile`, configured as `{fleet}.{reader}`, renders tiles only.
Each team marks the tasks it runs with the budgets of its caches, and a member opens its reader with
them, for the settings the reader has: the builders use a page buffer of 64 MiB and the library's
chunk cache, the tile team the reader's page buffer and a chunk cache of 256 MiB per dataset. The
store releases the builders of a reader once none of its datasets is being built; they stand down,
rather than disband, since pyre hands back the same team for the same name and a disbanded one can
never work again, and the next build brings them back. A reader that is disconnected has its team
stand down for the same reason.

Every run of a build reports the pages it fetched, as the misses of the page buffer of the worker's
file, and a build adds them up (`RasterBuild.fetched`, and `measure pyramid`). A dataset leads the
builds of the rasters it is read with: their first levels are made in the same runs, tile by tile,
so a page is fetched once for all of them while it is in the page buffer. A run longer than a row
of tiles carries on into the next row, so that a run can be a band of rows.

On the covariance fixture, HHHH of frequency A and its mask, whose chunks occupy 219 distinct
pages, the builds fetched:

| Builders | Runs of 8 tiles | One band each | Each raster on its own |
|----------|-----------------|---------------|------------------------|
| 1        | 183             |               | 183                    |
| 4        | 313 to 318      | 269           | 318                    |
| 16       | 370 to 376      | 356           | 375                    |

Building the rasters together changes little on its own, because their builds already run at the
same time and their runs meet on the same workers. What multiplies the pages is the number of
workers: the chunks of the mask are scattered over 193 pages, those of the other covariance term
included, so every region of the raster needs pages from all over the file, and any division of
the raster among workers fetches some pages more than once. Bands of rows help a little, and slow
the build when they leave workers idle. Doing better takes the plan below: the work ordered by where
the pages are in the file, not where the tiles are in the raster, and balanced by bytes. The fixture
is small, 219 pages in all, and a product in a bucket is where the difference is worth measuring.
The count of pages for the mask built alone, 159, is below the 193 pages its chunks occupy, which
is still to be explained.


## Planning from the chunk table

The chunk table of every raster, together with the page size of the file, is cheap to read, even
from a bucket: opening a GSLC next to the data takes 65 ms. It is the plan of the build:

- the page of every chunk, which is its address divided by the page size;
- the chunks that were never written, which cost nothing and are skipped;
- the chunks that hold nothing but the fill, recognized by their stored size, which equals the
  size of the smallest chunk of their raster; these are skipped too, since their content is
  known, which spares their fetch and their decoding; the census confirmed the rule by decoding
  one such chunk in every raster;
- which rasters share each page;
- the compressed size of every chunk, which is the best available estimate of the time it takes
  to decode, and lets the tasks be balanced by work rather than by count;
- the locality of the chunks on their pages, which says how well a page serves a region.

Pages that hold only chunks of fill are never fetched.


## Fetching every page once, with the selected raster first

The build covers every raster of the file that the reader can display, masks included. The plan
is a sequence of pages, and each page appears in it exactly once:

1. Walk the level one tiles of the selected raster in the order they are wanted: the tiles that
   seed the statistics first, then the rest. For each tile, look up its chunks, and for each
   chunk, its page. Append every page not already in the sequence. At the end of this walk, the
   sequence holds every page that carries a chunk of the selected raster, in the order the
   selected raster needs them.
2. Append the pages that hold chunks of the other rasters only, in the order of their addresses.
3. Cut the sequence into tasks: consecutive runs of pages, sized by the bytes of the chunks they
   carry.

A worker that receives a task fetches its pages and decodes every chunk on them, of every
raster, into the level one of that raster. Each page is in exactly one task, so across the
whole team each page is fetched once. The worker's page buffer holds the pages of its task until
the task is done, so a page is never evicted before all its chunks have been decoded.

The selected raster is not held back by this: its pages are the first ones handed out, and its
level one is complete once the tasks of step 1 have reported. The price of the priority is the
decoding of the other chunks on those pages: in a GSLC whose pages are 76 percent HH on average,
the HH level one takes about a quarter longer than it would if the other chunks were ignored.
The alternative, decoding only HH now and the rest later, fetches every shared page twice.

The masks, which are the most expensive rasters to read on their own, come nearly for free:
their chunks are decoded from pages that are fetched for the other rasters anyway.

If the user selects another raster before the build is over, the tasks that have not been handed
out yet are put in the order of the new selection; the pages already processed are done for every
raster, so nothing is lost.

### The unit of work

A tile of level one covers two by two chunks, and those four chunks may sit on pages that belong
to different tasks. So a task does not produce whole tiles: each chunk contributes one quarter of
a level one tile, which the worker writes into its place in the level file. A tile of level one
is complete, and is marked in the occupancy record, when all its quarters have reported. The
server keeps the count. Levels two and above are built from level one, locally, a raster at a
time, as soon as the level one of that raster is complete, so the selected raster does not wait
for the others to reach its higher levels.

A chunk that straddles two pages belongs to the task of its first page. None of the products in
the census has such chunks, but the paged layout does not forbid them.


## Serving tiles

A tile at full resolution over a chunked product is one chunk on one page; the tiles that follow
it as the user pans are its neighbors, which are likely on the same page. The tile team routes a
tile to the member that owns the page of its chunk, which is known from the chunk table. That
member fetches the page once and serves the neighboring tiles from its caches: about 100 ms for
the fetch next to the data, then a few ms of decoding for each further chunk, against a fetch of
the same page by every member that happens to receive one of its tiles.

Zoomed out tiles are read from the levels through a memory mapping, which the operating system
shares between processes, so they need no routing.

The assignment of pages to members has to survive a member that dies and a team that changes
size, which suggests a consistent hash from page to member rather than a table. A page that is
very popular makes its member busier than the rest; whether that matters in practice is to be
measured.


## The view while the picture is incomplete

A zoom level whose pyramid level has not been built is disabled. This includes a zoom level named
in a configuration file, whose author expects it to apply at startup. As the levels become
available, the zoom control enables their tick marks. Zooming in is always available, and so is
full resolution. Readers that do not build pyramids are not affected.

Two things follow from how the pyramid is built. Level one is nearly the whole cost of the build,
since it reads the entire product, and the levels above it follow within seconds; so in practice
the zoomed out levels become available together, after about a minute next to the data. From
outside the region, level one can take hours, so zooming out stays disabled unless something
smaller is built, e.g. the levels of the region being viewed.

A view that asks for a disabled zoom opens at the nearest enabled level, and moves to the zoom it
asked for when that level becomes available, unless the user has changed the zoom in the
meantime.


## Preparing ahead of time

A build is paid once per product: its levels and the statistics it measured are kept in the
workspace, and a pyramid takes back the levels it finds there. It is also the one activity that
spoils the tiles while someone is looking, since it takes the connection to the bucket the tiles
need. So the build is best done before anyone looks: a user who names the products of interest can
have them prepared while away, and find the viewer fast on return.

**The tool.** A panel of the command line, e.g. `qed prep`, reads the same configuration as the
server, finds the same readers, and works in the same workspace. It goes through the configured
readers one at a time, since the construction is bound by the connection rather than by the number
of workers, and for each:

1. makes first contact, unless a saved survey of the product is in the workspace, and saves the
   survey;
2. builds the pyramids of every raster of the product, each dataset leading the rasters it is read
   with, on builders sized for the connection, about 32 next to the data, with no tile team to
   leave room for;
3. reports what it did: whether the survey was made or found, which rasters were built and which
   were already complete, the time, and the pages fetched.

A reader that fails, e.g. because its product is unreachable, is reported and skipped, and the
batch goes on. Its progress goes to a journal channel of its own, `qed.prep`.

**Keeping the survey.** What a survey learns about a product does not change, so it is kept like
the levels: the survey's record, `Discovery`, which holds plain values, is written into the
workspace next to the pyramids of the product, in a form that does not depend on the version of
qed that wrote it, e.g. JSON with a version number. The server looks for it before it sends a
reader to the builders for first contact: when it finds it, it hydrates the reader from it at once,
without touching the product, and the reader is ready as soon as it is connected. The server also
writes the record after every survey it makes, so an interactive session prepares the next one.

**Identifying the product.** The saved survey and the levels are found by the identity of the
product, which has to be known before the product is opened:

- a NISAR product is identified by its granule id, which is unique, stable, and names the version
  of the processing; the naming convention of the mission makes it the name of the file, so it is
  known from the uri alone, and it is what the pyramids already use once the product is open;
- a local file of any other kind is identified by its address, its size, and the time it was last
  written;
- a file of any other kind in a bucket is identified by its address alone, which does not notice a
  file replaced at the same address.

**Resuming.** A build commits its levels one at a time, and a level counts only once every run of it
has reported, so a batch that is interrupted, or fails on one reader, is run again and picks up at
the first level that is not complete.

**Credentials.** A batch over many products can outlive temporary credentials, e.g. a token that
lasts four hours. The builders take their credentials with every task, fresh from the reader or its
archive, so they last as long as whatever the reader resolves them from; when they expire, the
readers still to go fail with the reason, and a new run after the credentials are renewed resumes.

**What it does not do.** It prepares what the configuration names; it does not decide what is of
interest. It does not bound the disk the levels take, which is the open question of the workspace's
budget below.


## Open questions

- How large the build team should be, as a function of the source: next to the data, the
  construction stopped improving at 32 workers, and larger teams delayed the first view.
- How the builders leave the tiles their share of the connection to the bucket while a view is
  active: fewer builders while a tile team has work, a limit on the fetches in flight, or builders
  that pause while the tiles queue. Measuring the traffic of the instance during a build would
  confirm that the connection is what they share.
- The identity of files that are neither NISAR products nor local: a file in a bucket replaced at
  the same address is not noticed.
- Where the serial six percent of the construction goes: the barrier between levels, the
  bookkeeping of the server, which runs on its event loop, or the recruitment of the workers.
- Whether tasks of consecutive pages need to be shaped by locality, e.g. for the GSLC, whose
  consecutive chunks are neighbors on the raster only 62 percent of the time.
- How the build is scoped off-region, where reading the whole product is not an option.
- Whether a local copy of the fetched pages, shared by all processes, is worth building; it would
  make the routing of tiles unnecessary, and requires an HDF5 file driver of our own.
- The disk budget of the workspace: the levels of one GSLC polarization took 7.4 GB, and the
  build now covers every raster of the file.


## Measurements

Three actions of the `measure` panel supply the numbers this design depends on.

**The caches** (`qed measure caches`) read a block of chunks that hold data, in the access pattern
of each kind of team, with each page buffer size and chunk cache size, every configuration in a
fresh process that opens the dataset before the reader does: a second open of a file, or of a
dataset, in the same process shares the caches of the first, whatever its access lists ask for.
On the local GSLC, 64 chunks on 22 pages:

- streaming in the order of the addresses misses on every page exactly once with any page buffer
  of 16 MiB or more, so a build team needs a page buffer of a few pages;
- revisiting in raster order misses on every page again with a page buffer of 16 or 64 MiB, and on
  none with 4 GiB; locally the difference is invisible, since the operating system caches the
  file, but in a bucket every miss is a fetch;
- a chunk cache that holds the block makes the second pass 3 to 4 ms against 290 ms for the first:
  decoding is the whole cost of a revisit.

The same measurement over the internet, from a laptop, on the GSLC of cycle 31 in the operations
bucket, a block of 16 chunks on 10 pages:

- HDF5 2.2, on the laptop, gives a file it reads from a bucket a page buffer of 64 MiB when none is
  asked for; HDF5 1.14.4, on the On-Demand system at the time of these measurements, does not, so
  whether a reader in a bucket has a page buffer without asking for one depends on the version of
  the library;
- streaming fetches every page exactly once, whatever the page buffer;
- revisiting with a chunk cache that holds the block takes 1 to 4 ms the second time; with the
  default chunk cache and a page buffer that keeps the pages, the driver's own or 4 GiB, 82 to 87
  ms, every page a hit and every chunk decoded again; with a page buffer of 16 MiB, too small for
  the pages, 11.1 s, every page fetched again. An undersized page buffer costs a round trip per
  page, and asking for one explicitly can do worse than the driver's default.

Next to the data, on the On-Demand system, a block of 64 chunks on 30 pages:

- streaming fetches the 30 pages in about 2.1 s with a page buffer, about 70 ms for a page of 4
  MiB from one process, and in 3.2 to 3.6 s without one, when every chunk is fetched on its own;
- revisiting with a page buffer of 4 GiB hits all 30 pages the second time and takes 357 ms, all
  of it decoding, about 5.6 ms a chunk; with a page buffer of 64 MiB, which cannot hold 120 MiB of
  pages, every page is fetched again;
- a chunk cache of 64 MiB cannot hold the 128 MiB the block decodes to, so it thrashes, and the
  second pass costs what the first did; the chunk cache has to be sized to the decoded working
  set, which the local measurement shows is worth two orders of magnitude.

**Tiles during a build** (`qed measure contention`) run a build and a steady stream of tiles at full
resolution on the same crew, in one process, and then the same stream once the build is over. On
the local GSLC, 20 tiles of 512 by 512 a second: with a team of four, the build took 15.5 s and the
tiles took a median of 26.6 ms and a 95th percentile of 55.7 ms, against 20.0 and 21.1 ms after it;
with a team of eight, 7.3 s, and 20.5 and 38.6 ms. The runs of a local build are short.

Next to the data, on the On-Demand system, 20 tiles of 512 by 512 a second, while the pyramid of
the HH polarization of the GSLC of cycle 31 was built by the same team, and 200 tiles once it was
done:

| Team | Build (s) | During the build, median / p95 (ms) | After it, median / p95 (ms) |
|------|-----------|-------------------------------------|-----------------------------|
| 16   | 92        | 215 / 1,577                         | 71 / 191                    |
| 32   | 74        | 440 / 3,404                         | 70 / 168                    |
| 64   | 61        | 1,420 / 6,984                       | 71 / 173                    |

A tile that shares its team with a build waits behind the runs of the build, each of which fetches
its pages from the bucket, and a larger team, which finishes the build sooner, makes the wait
longer, up to 11.4 s for the slowest tile with a team of 64. The latency is worst in the fourth
and fifth sixths of the build. Once the build is over, a tile takes about 71 ms, whatever the size
of the team. This is the case for a team of its own for the tiles.

**Tiles during a build, on teams of their own.** The same measurement, next to the data, after the
split: a team of 16 serves the tiles and builders of each size build the pyramid of the HH
polarization of the GSLC, on an instance with 192 cores; 20 tiles of 512 by 512 a second during the
build, and 200 once it is done:

| Builders | Build (s) | During the build, median / p95 / max (ms) | After it, median / p95 (ms) |
|----------|-----------|-------------------------------------------|-----------------------------|
| 16       | 68        | 153 / 1,816 / 7,285                       | 101 / 265                   |
| 32       | 47        | 472 / 7,739 / 15,548                      | 92 / 189                    |
| 64       | 44        | 3,179 / 38,075 / 43,677                   | 90 / 203                    |
| 128      | 43        | 6,896 / 40,338 / 43,396                   | 87 / 174                    |

With 16 builders, against the single team of 16 above, the build is faster, 68 s against 92, and
the median tile is faster, 153 ms against 215, with the 95th percentile about the same. More
builders shorten the build to about 43 s, which it does not go below, and make the tiles wait far
longer, up to tens of seconds, although the tiles no longer share a workplan with the build. The
process that runs the build and the tiles is not the cause: every 100 ms it recorded how late its
event loop ran and how much cpu it had spent, and the loop was late by less than 2 ms at the 95th
percentile, with the process on the cpu 3 to 4 percent of the time, with any number of builders.
Nor is the cpu of the machine, with at most 144 workers on 192 cores. What the builders and the
tile team share is the connection to the bucket and the object they read, and a build that stops
getting faster past 32 builders is bound by it; this is the likely cause, and has not been
confirmed by measuring the traffic. Once a tile takes longer than the team can absorb, 0.8 s for 16
members at 20 tiles a second, the queue of the tile team grows with every tile, which accounts for
the waits of tens of seconds.

The division into teams is necessary but not sufficient: the builders also have to leave the tiles
their share of the bandwidth while someone is looking. Since a build is paid once per product, and
its levels are kept, the other way out is to build before anyone looks.

**The ceiling of the server** (`qed measure swarm --workload`) sends the same swarm with tiles that
cost nothing, served from the tile cache, with tiles of fill, and with tiles of data. On macOS all
three stopped at about 140 tiles/s, with the server and its clients mostly idle. The cause was the
delivery of every tile: the server mapped the spool file the worker left the tile in, and CPython's
`mmap` on macOS flushes the file it maps, about 6 ms each time. The server now sends the spool with
`sendfile` instead. On the same machine and the same swarm, cached tiles went from 138 to 3,915 a
second, tiles of fill from 142 to 1,796, and tiles of data, with a team of eight, from 147 to 833.

On Linux, next to the data, on the On-Demand system, with tiles of 512 by 512 and batches of 128
tiles, most of which finish in less than a second, so the numbers show a trend rather than precise
values: tiles served from the cache reach about 1,300 a second, about 1 GB/s from the one thread of
the server; tiles of fill, which go to a worker that reads nothing, about 600 a second, so handing
a task to a worker and taking delivery of its tile costs the server about 1 ms; tiles of data from
the bucket about 200 a second with a team of 16, 350 with 32, and no more with 64. The event loop
of the server is not what limits the tiles of data in a bucket; whether 32 is the size beyond which
a team gains nothing takes batches long enough to keep every member busy.

With batches of 2,048 tiles of 512 by 512 and up to 256 in flight, on the instance with 192 cores:

| Team | 8 in flight | 32 | 128 | 256 (tiles/s) |
|------|-------------|----|-----|---------------|
| 16   | 112         | 249 | 280 | 308          |
| 32   | 104         | 403 | 469 | 470          |
| 64   | 96          | 361 | 661 | 699          |
| 128  | 98          | 324 | 487 | 431          |

A team of 64 serves about 700 tiles a second; a team of 128 serves fewer, which is what a limit
shared by all the workers, such as the connection to the bucket, would do. With teams of 16 and 32
and 128 or more tiles in flight, the 95th percentile of the latency reaches several seconds.


<!-- end of file -->
