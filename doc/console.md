<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# console: the journal in the client

> Status: **built through the channel toggles** (2026-09-05, branch `journal`): the server
> device, the `journal` route with history on subscription, the console activity with
> its filters, expansion, copy and clear, the channel listing and switch, and the facade;
> worker entries arrive through the `pyre` fan-in with no `qed` change. Not built:
> virtualized rendering, and channel control that reaches running workers. The `qed`
> half of journal delivery: a device in the server that forwards every entry to connected
> clients, and an activity panel that shows them. The generic half, a device that ships
> entries over ipc and the collection of worker entries in `pyre.nexus`, is designed in
> `pyre/doc/design/courier.md`. This supersedes part two of `doc/diagnostics.md`, whose
> options for the crew are settled here. Facts about the code that preceded this work
> were read from the source on 2026-09-04; open questions are marked.

## What the server does

### One device sees everything

The server installs one journal device on the chronicler when the web service
activates, in `qed.nexus.Server.activate` (`pkg/nexus/Server.py:45`), which is the first
point that has both the dispatcher and the event hub in hand. From then on every entry
the server flushes, from Python or from the C++ pipelines, arrives at that device
through the trampoline. Worker entries arrive at it too, without any `qed` code: the
nexus replays each record it collects from a crew member into the parent's journal,
where the same device is the default. The device therefore sees the whole application
and does not know or care which process an entry came from; the origin is in the notes
of the entries the nexus replayed, and absent from the server's own.

The device, `qed.ux.Journal`, does three things with an entry:

- **mirrors** it to the device that was installed before it, so the terminal remains
  the record for whoever is running the server directly;
- **records** it, as a record in the format of `journal.Record`, into a bounded history,
  a deque whose length is a trait of the server; and
- **queues** it for publication.

It never raises: any failure in recording or queuing is swallowed, since a diagnostic
sink that takes down the server it describes is not a trade anyone wants. It also
guards against re-entry: an entry flushed while the device is publishing is mirrored
and recorded but not queued, so a warning raised by the hub while draining a slow
client cannot loop back into the hub.

### Records, not entries

The device builds the record itself for the server's own entries, with the server's pid
and its own sequence counter; for a replayed worker entry the nexus has already written
`pid`, `seq` and `time` into the notes, and the device lifts them into the envelope
rather than stamping its own. A client thus receives one record shape whatever the
origin, and can group and order by process.

### Publication

Records travel on the event stream, on their own hub topic, `journal`, so that a client
that never opens the console pays nothing and the contentless "something changed"
contract on the global topic is untouched. The hub supports topics already
(`pyre/http/Hub.py:25-39`), and the endpoint is a second route beside `events`:
`journal`, returning `server.eventStream(topic="journal")` from `pkg/ux/Dispatcher.py`.

Two rules that differ from the change notification:

- **Never coalesce.** Every record is content. Volume is controlled by batching
  instead: the device queues records and arms a one-shot dispatcher alarm, of the
  order of a tenth of a second, the first time the queue goes from empty to
  non-empty; when the alarm fires it publishes one frame carrying every queued record
  as a JSON array, named `journal` so the client can tell it from any other frame. A
  chatty debug channel produces a few frames a second rather than hundreds.
- **Replay on subscription.** A client that opens the console wants to see what
  happened before it opened, so the first frame a new subscriber receives is the
  history. This needs a small hook in `pyre.http`: `EventStream` gains an optional
  opening payload that `Server.stream` enqueues right after the preamble. It is
  generic, and is recorded in the `pyre` change map below.

Publishing from inside the device is safe with respect to the event loop: every entry
is flushed either while a request is being served, while a worker's journal channel is
being read, or while an alarm fires, and all three are inside the loop. The
out-of-band wakeup that `pyre/doc/design/sse.md` left as an extension point is not
needed.

### Channel control

The console is the natural place to turn channels on and off, which is far more
discoverable than the configuration file. Two GraphQL operations:

- `journal { channels { severity name active fatal } }`, on the session object, listing
  the channels the server knows about. The live index in `libjournal` is not enumerable
  from Python, so the list is the union of the channels the application declared
  through its `journal.channels` trait and the channels that have appeared in records
  since the server started, which the device collects as a side effect of recording.
- `journalChannelSet(input: { severity, name, active })`, following the single-input
  convention in `doc/graphql-conventions.md`, which sets the flag on the server's own
  channel of that severity and name.

In the first version the mutation reaches only the server's channels. A worker forked
before the change keeps the state it inherited, and one forked after gets the new state
for free. Reaching running workers is the control phase of the `pyre` design, and the
mutation grows to forward the change when that exists; the client is written against
the mutation, not the mechanism.

## What the client does

### The activity

A new activity, `console`, on the navigation rail after `controls`, following the
pattern in `ux/client/activities/data` exactly: a directory with `index.js` and
`styles.js`, a shape under `ux/client/shapes/console`, one export line each in the
activity and shape barrels, and one line in `ux/client/activities/bar/index.js`. Its
url is `/console` and its label, which is also its `data-qed-nav` identity, is
`journal`.

The panel sits in the `viz` layout as a third child route beside `controls` and the
readers, so it occupies the activity panel next to the viewports and entries can be
watched while the rasters are being driven. That inherits the panel's width and scroll
behavior from `ux/client/views/viz/viz/styles.js:40-53`. A full-width layout of its own,
in the manner of `doc`, is the alternative if the panel proves too narrow; the route is
the only thing that changes.

### The stream

The console owns its subscription. A hook, `useJournal`, opens an `EventSource` on
`journal` when the panel mounts and closes it when the panel unmounts, so a client with
the console closed holds no second connection. It listens for frames named `journal`,
parses the array, and appends to a bounded buffer whose length matches the server's
history. The existing `ux/client/automation/eventStream.js` stays as it is: it opens
`events`, ignores payloads, and belongs to live sync. The two are different streams
with different contracts, and nothing is gained by multiplexing them.

The hook lives in `ux/client/views/viz/console/` with the panel, since nothing else
consumes it. If a second consumer appears, for instance a badge on the activity that
counts warnings while the console is closed, the subscription moves to a context
provider mounted beside `LiveSync` in `ux/client/qed.js`, and the hook reads from it.

### The panel

In order of importance:

- **A list of entries**, newest at the bottom, that stays responsive at the buffer's
  full length. Rendering only the visible rows is the way to keep it so; the first
  version may render the whole buffer if it is small, but the buffer size is a trait and
  virtualization is the expected end state.
- **A row per entry** showing the severity, the channel, the first line of the page,
  and the pid when the entry came from a worker. Severity colors come from the palette,
  which already has a journal slot (`ux/client/palette.js:34-37`).
- **Expansion**: a click on a row reveals the remaining lines, the source location, the
  time, and any other notes.
- **Filters**: by severity, a set of toggles; by channel, a text field matched as a
  prefix against the dotted name, so that `qed.nexus` shows the whole subtree.
- **Clear**, which empties the client's buffer and nothing else.
- **Copy**, which places the visible entries on the clipboard as text, in the form the
  terminal would have shown them.
- **Channel toggles**, a tray listing the channels from the query with a switch per
  channel that commits the mutation.

Markup follows `doc/semantic-markup.md`: the panel carries `data-qed-panel="journal"`,
the filters and toggles carry `data-qed-control` and `data-qed-value`, and toggle state
is `aria-pressed`.

### Automation

`window.qed` gains a `journal` namespace, assembled in `ux/client/automation/qed.js`
beside `sync`, `measure`, `range` and `value`:

- `journal.entries()`: the records currently in the console's buffer, when the panel is
  mounted; the facade reads them from the same store the panel renders.
- `journal.channels()`: the query.
- `journal.setActive(severity, name, active)`: the mutation.

The typings in `tests/qed.ux.playwright/lib/qed.d.ts` and the surface description in
`doc/automation-surface.md` grow accordingly, and `/console` joins the route list in
`tests/qed.ux.playwright/lib/routes.ts` so the identity and ARIA sweeps cover it.

## Tests

Server side, in `tests/qed.pkg`:

- a device installed on a chronicler with a mirror; entries of each severity reach the
  mirror and the history, and the record carries the right sink and origin;
- a replayed entry, whose notes carry `pid`, `seq` and `time`, produces a record with
  those in the envelope rather than the server's;
- the re-entry guard: an entry flushed during publication is recorded but not queued;
- batching: several entries flushed in one turn of the loop produce one frame.

Client side, in `tests/qed.ux.playwright`, modeled on `behavior/live-sync.spec.ts`:

- open the console on an observer page, cause a warning on a driver page, and assert
  the observer's row appears without a reload;
- the history: cause the warning first, then open the console, and find it;
- filters and the channel toggle, through `data-qed-control` and `aria-pressed`.

Causing a warning deterministically needs a server action that is guaranteed to log
one. A GraphQL query that names a field the schema does not have makes the handler log
a warning on `qed.ux.graphql` for every error it reports back, which is what the tests
use; a facade command that asks the server to emit a test entry remains an option if
that path ever changes.

## Change map

`pyre`, in addition to `pyre/doc/design/courier.md`:

- `pyre/http/EventStream.py`: an optional opening payload.
- `pyre/http/Server.py`: `stream` enqueues the opening payload after the preamble.

`qed`:

- `pkg/ux/Journal.py` *(new)*: the device: mirror, history, batching, publication,
  channel census.
- `pkg/nexus/Server.py`: install the device in `activate`; traits for the history
  length and the batching interval.
- `pkg/ux/Dispatcher.py`: the `journal` route.
- `pkg/gql/Journal.py`, `pkg/gql/JournalChannel.py`, `pkg/gql/journal/JournalChannelSet.py`
  and its input type *(new)*: the query and the mutation, mounted on `QED` and
  `Mutation`.
- `ux/client/activities/console/`, `ux/client/shapes/console/` *(new)*: the activity.
- `ux/client/views/viz/console/` *(new)*: the panel, `useJournal`, the trays.
- `ux/client/qed.js`: the route.
- `ux/client/automation/qed.js`: the `journal` namespace.
- `tests/qed.pkg/ux/journal_*.py`, `tests/qed.ux.playwright/behavior/console.spec.ts`,
  `lib/qed.d.ts`, `lib/routes.ts`.
- `doc/automation-surface.md`, `doc/diagnostics.md`: pointers.

## Sequencing

1. The `pyre` courier and nexus collection, installed.
2. The server device with mirror and history, and the `journal` route with replay on
   subscription. Verifiable with `curl` before any client work.
3. The activity, the panel with the list, expansion and filters, and the facade.
4. The channel query and mutation, and the toggles tray.
5. Virtualized rendering, once the buffer size makes it matter.
6. Worker channel control, when the `pyre` control phase exists.

## Open questions

1. **Who sees the console in a hosted deployment?** Every client shares server state,
   so every client would see every entry, including entries about products that belong
   to someone else. The first version accepts this; a notion of scope, if one is needed,
   is a decision that touches the store rather than the console.
2. **What is on by default?** Nothing changes: the severities that speak today are the
   ones the console shows. Debug channels stay off until toggled, and the toggle is the
   feature that makes turning one on for a minute cheap enough to be worth it.
3. **How much history?** A deque of a few thousand records is a few megabytes at most;
   the trait defaults to that and the client buffer matches it.
4. **A test entry on demand.** A facade command, backed by a mutation, that asks the
   server to log a given message on a given channel at a given severity would make the
   client tests deterministic and would double as a way to check that a channel is
   audible. It is a small addition and it is honest about being a test aid; the
   alternative is to rely on a real failure path that may change.
5. **Panel or full width?** The design places the console in the activity panel beside
   the viewports. If a log at that width is unreadable, it moves to a layout of its own.


<!-- end of file -->
