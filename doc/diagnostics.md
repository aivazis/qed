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
Three options, in increasing order of cost:

1. *Leave workers out of the first version.* The console shows the server's own
   diagnostics, which after the staging work includes every survey failure, since the
   reason travels back in the failure report. Cheapest, and already useful.
2. *Piggyback on the existing crew channel.* Entries produced while a task runs accumulate
   in the worker and ride back with its report. No new plumbing, but entries arrive in
   batches at task completion rather than as they happen, and a worker that dies takes its
   last words with it — which are exactly the words one wants.
3. *Give each worker a diagnostics channel of its own*, registered with the event loop the
   way the crew channel already is. Faithful and live, and the most work: a second
   descriptor per worker, its own framing, and a policy for what happens when the reader
   is slower than the writer.

The honest recommendation is to start at (1), which is genuinely useful on its own, and to
treat (3) as the eventual answer with (2) as a stepping stone only if it turns out that
task-scoped batching is enough in practice.

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
it does not ship in the first version.

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


<!-- end of file -->
