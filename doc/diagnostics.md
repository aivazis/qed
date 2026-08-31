<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# diagnostics: better messages, and a console in the client

> Status: **scope, not yet scheduled**. Two related pieces of work: raising the quality of
> the diagnostics qed produces, and giving the client a console that shows them. The first
> is small and independent; the second is a feature in its own right. Everything recorded
> here as a fact was read out of the source; the open questions are marked as such.
> Companion: `doc/staging.md` for the lifecycle these diagnostics describe.

## Why this came up

The staging lifecycle now retains the reason a data product failed and displays it beside
the product in the panel. That immediately exposed how poor the reasons are. A NISAR
product whose file is missing reports:

    'NoneType' object has no attribute 'objectType'

which is an internal HDF5 traversal failure, faithfully relayed. It tells the user
nothing. The lifecycle work made these messages visible for the first time; it did not
make them bad, and the fix belongs to the readers rather than to the lifecycle.

The second piece follows from the first. Once a message is worth reading, the question is
where a user reads it. Today every diagnostic goes to the terminal where the server was
launched, which is invisible to a browser client — and, in the deployments qed cares
about, may belong to somebody else entirely.

## Part one: better messages

This part is self-contained and can be done at any time.

The work is a pass over the reader flavors, replacing relayed internal failures with
diagnostics that name what was being attempted, what was expected, and what was found. A
missing file, a file that is not the declared product type, a product missing the group
the reader requires, a shape that cannot be reconciled with the file size, and expired or
insufficient credentials are all distinguishable conditions that currently arrive as
whatever exception the underlying library raised.

Two constraints shape it. First, the message now has two audiences: the terminal, and the
panel of a user who cannot see the terminal — so it must be complete on its own, without
the surrounding log for context. Second, the readers already open their products on crew
members rather than in the server, so a diagnostic raised during a survey is text that
travels back in a failure report; it must survive that trip as a plain string, which it
does today.

A domain-specific exception hierarchy for the readers, rather than the generic exceptions
now raised, is the natural vehicle: it lets the staging path distinguish a missing file
from a malformed product, and lets the client eventually offer different affordances for
each.

## Part two: a console in the client

### What is already true

These were read out of `pyre` and qed rather than assumed:

- **A journal device is a small interface.** `Device` has three methods — `alert` for
  user-facing severities (`info`, `warning`, `error`), `memo` for developer-facing ones
  (`debug`, `firewall`), and `help`. Each receives an `Entry`, which carries a `page`, a
  list of text lines, and `notes`, a dictionary of metadata that includes the severity,
  the channel name, and the source location when the entry was flushed with one.
- **One device can capture both languages.** When the bindings are present — always, in
  qed — `journal.device` is the C++ `Device` exposed through a pybind11 trampoline, so a
  Python subclass installed on the chronicler receives entries emitted by C++ code as
  well as by Python. This is the finding that makes the whole idea tractable: without it,
  the render pipelines and the firewalls in the bindings would be invisible to any device
  written in Python.
- **Devices can be installed globally, per severity, or per channel.** So the console can
  be given the whole stream, or a deliberately chosen subset, without touching call sites.
- **The event stream already supports topics.** The hub records subscribers per topic, and
  the existing change notification uses the global one. A diagnostics stream can therefore
  ride its own topic, leaving the "any message means refetch your state" contract that
  every client depends on exactly as it is.
- **Publication can coalesce.** The change frame uses this, so a burst collapses into one
  refetch. Diagnostics must not coalesce — each entry is content, not a hint that content
  changed — which means volume has to be controlled by other means.

### The shape of the work

**A device that publishes.** A journal device that, instead of writing to a terminal,
renders each entry into a record — severity, channel, the lines of the page, the source
location, a timestamp, and which process produced it — and hands it to the server for
publication on the diagnostics topic. It is installed when the web shell starts and
removed at shutdown. The device must never raise: a failure inside a diagnostic sink that
takes down the server it is describing would be an unpleasant way to learn this lesson.

**Transport.** The record travels as an event-stream frame on its own topic, so a client
that never opens the console pays nothing. Frames carry a type, so the client can tell a
diagnostic from a change notification without inspecting content. Batching matters: a
chatty debug channel can produce entries faster than a browser can usefully render them,
so entries should accumulate briefly and travel as a group rather than one frame each.

**The crew is the hard part.** Workers are separate processes. A device installed in the
server captures nothing that a worker emits, and workers are where the interesting
failures now happen — the survey opens the product, and the render pipelines run there.
Four options, in increasing order of cost and generality:

1. *Leave workers out of the first version.* The console shows the server's own
   diagnostics, which after the staging work includes every survey failure, since the
   reason travels back in the failure report. Cheapest, and already useful.
2. *Piggyback on the existing crew channel.* Entries produced while a task runs accumulate
   in the worker and ride back with its report. No new plumbing, but entries arrive in
   batches at task completion rather than as they happen, and a worker that dies takes its
   last words with it — which are exactly the words one wants.
3. *Give each worker a diagnostics channel of its own*, registered with the event loop the
   way the crew channel already is. Faithful and live, and more work: a second descriptor
   per worker, its own framing, and a policy for what happens when the reader is slower
   than the writer.
4. *Deliver journal entries over IPC*, so that shipping a diagnostic somewhere else is a
   capability of the journal rather than an arrangement qed makes. This is the subject of
   the next section.

Options 1 through 3 all make the server the collection point, which means qed builds the
fan-in itself and builds it once per producer. Option 4 removes that obligation, at the
cost of work that belongs upstream.

### Journal delivery over IPC, and the daemon question

The oldest form of this idea is a journal daemon: a process that accepts entries from
every participant and makes them available to whoever wants to read them. `pyre` had one
before a journal rewrite, and it was never reimplemented; the framework's `TODO` still
carries an empty `journal:` heading where it used to be accounted for.

It is a sound strategy, for three reasons. It dissolves the fan-in problem rather than
solving it repeatedly: the server, every crew member, and the command line shells are all
simply producers, and nothing in qed has to relay anybody else's diagnostics. It belongs
in `pyre`, where `journal` already lives and where the pieces are already present —
`pyre.ipc` supplies channels, pipes, Unix and TCP sockets, ports and picklers, and
`pyre.nexus` supplies the node, peer, and service machinery a daemon would be assembled
from. And a channel-writing device implemented on the C++ side would let C++ code ship
entries without a round trip through Python, which matters here because the render
pipelines are C++ and run inside the workers.

**The distinction that should drive the sequencing is between the primitive and the
deployment.** Delivery over IPC is the primitive: a device that marshals an entry onto a
channel. What sits at the far end is policy. Built that way, option 3 above is that device
pointed at a pipe, and the daemon is the same device pointed at a socket — so building the
device first is not wasted under either strategy, and it lets the record format and the
failure behavior be settled before a second process is introduced. That is the order worth
following: the device first, its far end inside the existing server, and the daemon as a
later deployment rather than a premise.

Two observations about what a daemon is actually worth here. Fan-in and fan-out are
separable, and qed already has fan-out: the event stream reaches every connected client,
with topics to keep the diagnostics separate. A daemon's contribution is therefore
collection; if it also owned distribution it would duplicate the server's HTTP surface,
and the more likely arrangement is that the server subscribes to the daemon and republishes
on the stream it already has. Set against that, a daemon is naturally bidirectional, and
that may be its best justification: `pyre`'s own `TODO` asks whether channels can be turned
on after an application has launched, which is exactly the control this console wants, and
a process already holding a connection to every participant is where that control belongs
— it would reach crew members that a server-side device can never touch. A collection
point is a modest thing; a control plane for the journal is not.

**What such a device must guarantee.** A diagnostic facility may never block or kill the
application it is describing. That means a non-blocking send, a bounded queue, dropping
entries rather than stalling when the far end is slow, and silent degradation to the
console when the far end is absent — a daemon that is not running must be a non-event, not
an error. Entries need a per-process sequence number alongside a timestamp, since order
across processes is otherwise only approximate. And the security posture deserves more care
than a log sink usually gets: a service that accepts entries from anyone and serves them to
anyone is both an injection sink and a disclosure channel, and diagnostics carry uris,
paths, and credential-adjacent metadata. A Unix-domain socket avoids most of that; a TCP
port does not, and should not listen beyond the loopback without authentication. Ordinary
operational friction — orphaned daemons, stale socket files, a daemon outliving the
application that started it — is the remaining cost.

Weighed for qed alone, a daemon earns the least in the case that is most common today, a
single user running a local server, and the most in the hosted multi-process deployments
that are currently rarer. That is an argument about ordering, not about merit.

**The client console.** A new activity, reached from the navigation rail like the existing
ones, showing the entries as they arrive. What it needs, in rough order of importance:

- A bounded buffer. The stream is unbounded and the browser is not; old entries are
  dropped rather than accumulated forever.
- Filtering by severity and by channel, since the channel hierarchy is dotted and users
  will want whole subtrees at a time.
- Enough structure per entry to be scannable: severity, channel, and the first line
  visible at a glance, with the remaining lines and the source location available on
  demand rather than always on screen.
- Rendering that stays responsive under volume, which for a long log means drawing only
  what is visible rather than the whole buffer.
- A way to get the text out — selecting and copying, at minimum.

**Control.** Since the device can be installed per channel, the console can also be the
place where a user turns channels on and off, which is far more discoverable than the
configuration file that governs it today. That capability is worth designing for even if
it does not ship in the first version, and it is the point at which the delivery mechanism
stops being an implementation detail: a server-side device can only reach the server's own
channels, whereas the IPC route can carry the instruction back to every participant.

### What this deliberately is not

It is not a replacement for the terminal log, which remains the record for anyone running
the server directly, and it is not a persistent store: entries live in the stream and in
whatever the browser is holding. Persisting diagnostics across restarts, searching them,
or shipping them anywhere else are separate questions that this work should not answer by
accident.

### Questions that need answering before it starts

1. **Who sees the console?** Every connected client shares server state by design, so
   every client would see every diagnostic — including, in a hosted deployment, entries
   about products belonging to somebody else. Whether that is acceptable, or whether the
   console needs a notion of scope, is a decision rather than a detail.
2. **What is on by default?** Debug channels are off by default today and the console
   would make turning them on easy. A default that floods the stream would make the
   feature feel broken.
3. **Does the console need history from before it opened?** A ring buffer on the server,
   replayed on subscription, is a small addition that changes the feature from "what is
   happening now" to "what has happened", and is much easier to design in than to retrofit.
4. **Does the IPC device get built in `pyre` first?** The console can be delivered without
   it, covering the server's own diagnostics, and gain the crew later. But if the device
   is coming anyway, the record format it defines should be the one the console consumes
   from the start, so the client is not written twice. This is a scheduling question
   across two repositories rather than a design question.


## Appendix: diagnosing a server that has stopped serving tiles

This is an inventory of what can be switched on today when tiles stop arriving, and of the
places along the path where nothing would be said at all. It was collected against the
`staging` branch on 2026-08-31.

### Turning a channel on

Two steps, both in the `qed.yaml` of the directory the server is launched from. The first
places the channel under user control, the second switches it on; there is a worked example
in `tests/data/native/qed.yaml`.

```yaml
qed.app:
    journal:
        channels:
          - debug, qed.ux.tiles
          - debug, qed.nexus.cache
          - debug, qed.nexus.fleet
          - debug, qed.nexus.pyramid
          - debug, qed.ux.dispatch
          - debug, qed.ux.stats

qed.journal.debug.qed.ux.tiles: { active: yes }
qed.journal.debug.qed.nexus.cache: { active: yes }
qed.journal.debug.qed.nexus.fleet: { active: yes }
qed.journal.debug.qed.nexus.pyramid: { active: yes }
qed.journal.debug.qed.ux.dispatch: { active: yes }
qed.journal.debug.qed.ux.stats: { active: yes }
```

Warnings, errors and firewalls are on by default, so the channels below marked as such are
already speaking.

### The path a tile takes, and what each stage says

**The request arrives — `pkg/ux/Dispatcher.py`**

| Channel | Severity | What it tells you |
|---|---|---|
| `qed.ux.dispatch.url` | debug | the recognizer's verdict on each incoming url |
| `qed.ux.tiles` | debug | one compact line per tile: client, viewport, `dataset.channel`, zoom, origin, shape, session, look-at, HTTP code, `via`, wall and cpu milliseconds |
| `qed.ux.dispatch` | debug, error, firewall | what was served; failures during generation; a tile refused for falling outside the raster |
| `qed.nexus.tiles` | warning | a task that took its crew member down, and a task that failed benignly and fell back to the inline renderer |

`qed.ux.tiles` is the one to reach for first. Its `via` field names the route the tile
actually took, and the vocabulary is the whole story: `hit` (served from the cache), `crew`
(rendered by a worker), `inline` (rendered on the server's own thread, which means the crew
path declined or failed), `refused` (out of bounds), `hangup` (the client left before the
tile was ready).

**The view and the store — `pkg/ux/Store.py`, `pkg/ux/View.py`**

| Channel | Severity | What it tells you |
|---|---|---|
| `qed.ux.staging` | warning | first contact failures, and a product that could not be reopened for a direct read |
| `qed.ux.preparation` | warning | a pyramid preparation that failed |
| `qed.ux.stats` | debug | each statistics merge and the running whole-dataset accumulation |
| `qed.ux.store` | info, firewall | view bookkeeping, and inconsistencies in it |

**The fleet, the team, the crew — `pkg/nexus/`**

| Channel | Severity | What it tells you |
|---|---|---|
| `qed.nexus.fleet` | debug | a team being formed for a product, and dismissed |
| `qed.nexus.cache` | debug | tile cache lookups and inserts |
| `qed.nexus.pyramid` | debug | which levels a worker attached, per product, and why an attach failed |
| `qed.nexus.survey` | debug | the survey round trip |
| `pyre.nexus.staff` | firewall | the only two things pyre's worker pool says at all |

**The readers**

`qed.readers.pyramid` (debug, warning), `qed.readers.statistics` (warning),
`qed.readers.native` (error), `qed.readers.native.flat`, `qed.readers.native.gdal`,
`qed.readers.isce2.xml`, `qed.readers.unw`, and one warning channel per NISAR flavor:
`qed.nisar.gcov`, `.gunw`, `.runw`, `.rifg`, `.rslc`, `.gslc`, `.roff`, `.goff`, `.rrsd`.

**The transport — `pyre`**

`pyre.http.server` and `pyre.http.headers` (debug) for the connection itself;
`pyre.ipc.selector` and `pyre.ipc.psl` (debug) for the event loop and the pickler that
carries tasks and results between processes.

### Where nothing is said at all

These are the gaps, ordered by how likely each is to be the reason tiles stopped.

1. **A parked response has no timeout and no census.** A tile that cannot be served from the
   cache parks the connection with `server.deferred()` and waits for the team. Nothing times
   that out, and nothing counts how many connections are parked. If a task is lost anywhere
   downstream, the connection hangs until the client gives up, and the server says nothing.
   This is the most plausible mechanism for "the server stopped serving tiles" and it is
   entirely silent. Wants a periodic census of parked responses and their ages.

2. **`qed.ux.tiles` logs completions, not arrivals.** Every `record(...)` call sits on an
   outcome path. A request that arrives and never finishes produces no line, so when tiles
   stop the log simply goes quiet — and a quiet log cannot distinguish "no requests are
   arriving" from "requests arrive and never complete". These are completely different
   faults. Wants an arrival line, or a sequence number paired across arrival and outcome.

3. **`pyre.nexus.Staff` is silent.** The entire worker lifecycle — `assign`, `assemble`,
   `vacancies`, `collect`, `requeue`, `abandon`, `bury`, `dismiss`, `recover` — carries two
   firewalls and nothing else. If every crew member is busy, if a casualty was never
   replaced, or if the workplan stops draining, there is no way to see it. This is a `pyre`
   change, and it is the deepest blind spot on the path.

4. **`pkg/nexus/Team.py` is silent.** `collect` is where a result is delivered, where the
   statistics are merged, and where the payload is either handed to the cache or released.
   A spool that is neither cached nor closed leaks; nothing reports it.

5. **`pkg/nexus/Spool.py` is silent.** The payload travels as a file descriptor over the
   crew channel. Descriptor exhaustion would stop tiles instantly and say nothing.

6. **`pkg/nexus/Crew.py` and `pkg/nexus/Server.py` are silent.**

7. **No queue depth or crew occupancy anywhere.** There is no line that says how many tasks
   are queued, how many crew members are busy, and how many responses are waiting.

8. **`Fleet.render` does not log the handoff.** Only team formation speaks, so a task
   accepted by the fleet and never assigned leaves no trace.


<!-- end of file -->
