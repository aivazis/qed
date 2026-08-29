<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# how qed starts up

> Status: this document describes the startup sequence as it is intended to work once the
> staging redesign is complete. It is written ahead of the code and will be kept current as
> each phase lands. The reasoning behind the design, along with the record of the system it
> replaces, lives in `doc/staging.md`; this document records only the destination.

## The cast

Three actors cooperate to take a data product from its first mention to a rendered
picture on screen.

The **client** is the application that runs in the browser. It draws the panels the user
interacts with, records the user's choices, and asks the server for image tiles as the
user pans and zooms. The client never sees the data itself; it sees only descriptions of
the data and finished pictures.

The **server** is a single process that owns the catalog of data products, answers the
client's questions, and coordinates all the work. It obeys one strict rule: the server
never reads a data file. Everything it knows about the contents of a product it learned
from a report prepared by someone else.

The **crew** is a collection of worker processes that the server creates, organized into
teams, one team per data product. The workers are the only actors that open data files.
Each worker holds its own open copy of the product and renders image tiles from it on
demand.

## The life of a data product

Every product the server knows about is, at any moment, in exactly one of four states.
The state is recorded in the server's catalog of sources, published through the query
interface, and visible in the client, so that neither the user nor the code ever has to
guess what stage a product has reached.

A product is **connected** the moment the server learns of its existence, whether from
the configuration read at startup or from a user connecting to it through the explorer.
At this point the server holds only what it was told: a name, a location, and the choice
of reader that will interpret the file. Nothing has touched the data.

A product is **staging** while its crew carries out the survey described below. The
product is already listed in the client, marked with a busy indicator, so the user knows
it has been received and is being prepared.

A product is **ready** once the survey report has arrived and been absorbed. Its datasets,
their coordinates, and sensible initial display settings are all known; the selector
panel is fully populated; the product can be viewed.

A product is **failed** if the survey could not be completed. The reason is retained and
displayed, and the product remains listed with two affordances: the user may retry the
survey or disconnect the product. A failure is never silent, and it never disturbs the
rest of the application.

## The sequence, step by step

### First contact

A product enters the system in one of two ways: it is named in the configuration the
server reads at startup, or the user connects to it at runtime through the explorer. In
both cases the server constructs a passive description of the product from its settings
and registers it in the catalog with status `connected`. Startup does nothing further:
the server binds its port and begins serving requests immediately, no matter how many
products are configured, because none of them has been touched.

Staging begins when someone cares. The first time a client engages the part of the
interface that presents the catalog, it asks the server to stage the connected products;
a product connected at runtime through the explorer is staged immediately, since the
connection request itself is the expression of interest. Either way the request returns
at once, the products appear in the panel marked busy, and a client that is merely
browsing the data archives never sets any of this in motion.

### The survey

The fleet forms the product's team and assigns it a survey task. One worker builds its
own copy of the reader from the product's recorded settings, opens the file — the only
first contact that occurs anywhere in the system — and walks its structure. The worker
then composes a discovery record: for each dataset, the coordinates that identify it, its
dimensions, its cell type, and its channels; the map of which coordinate combinations
actually exist; and a first statistical sample of the data, gathered in exactly the form
that dataset's channels expect, because the record is authored by the same reader flavor
that will consume it. The record is compact, contains no pixel data, and travels back to
the server over the channel the team already uses for its reports.

Discovery is inherently sequential work — the structure of a file reveals itself one
step at a time — so the survey employs a single worker and seeks no speedup within a
product. What the arrangement buys is placement, not parallelism: the server remains
responsive throughout, products stage concurrently with one another, a defective file
harms only the worker examining it, and the worker that performed the examination
retains the open product, ready to render.

### Hydration

When the discovery record arrives, the server-side reader absorbs it. Datasets
materialize as lightweight objects that carry metadata only; display controls tune
themselves from the statistical sample. This is the one moment at which initial display
settings are chosen, and it is guaranteed to occur before any view can bind the dataset,
so the choice is never revised in front of the user. The product's status flips to
`ready`, the server notifies the client, and the selector panel lights up with the
product's coordinates and availability. If the survey fails instead, the status flips to
`failed`, the error travels with it, and the panel offers retry and disconnect.

### Selection

The user composes a view by picking a value along each of the product's coordinate axes.
Every choice is a small exchange with the server, which updates the view's state and
narrows what remains available. Because all the metadata is already resident on the
server, each exchange is quick, and no choice can trigger contact with the data file.
When the final axis is pinned, the server binds the matching dataset to the view, selects
its channel when only one exists, and marks the view ready. The client reads that
readiness directly; it does not infer it.

### The first tile

With the view ready, the client partitions the visible region into tiles and requests
them. The product's team already exists and is already warm: the survey opened the
product in the worker registry, so no processes need to be created and no files need to
be opened on the request path. A worker renders each tile with the display settings the
survey established, so the first picture the user sees is correctly tuned; there is no
visible moment of retuning. Finished tiles are cached, and later requests for the same
tile are served from the cache without involving the crew.

## When something goes wrong

Failure is a first-class state, not an anomaly. A product whose survey fails is retained
in the catalog with its error message, visibly marked in the client, and equipped with
retry and disconnect actions. A worker lost during rendering is reported and its work
reassigned. In every case the damage is confined to the product involved: the server
keeps serving, the other products remain usable, and the client interface never goes
dark because one file was unreadable.


<!-- end of file -->
