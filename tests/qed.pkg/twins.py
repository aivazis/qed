#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that every dataset flavor that supports hydration can materialize a metadata-only
twin without touching a file, and that its channels tune themselves from the seed

Each twin is pointed at a path that does not exist: construction that reached for the file
would fail outright, so passing is itself the proof that hydration is contact-free. The
seeds are shaped the way each flavor produces them, which is the point of letting the
flavor author its own finding -- the unwrapped interferogram keeps a record per interleaved
band, and its channels index them separately, so a uniform seed would mis-tune it
"""

# support
import qed

# a path that does not exist, so any attempt to open it fails loudly
absent = "file:/nonexistent/qed/twin.dat"

# a single-record seed: the minimum, mean, and maximum of a sample
record = (0.0, 1.0, 100.0)

# the flavors that support hydration, with the cell type and seed shape each one expects
flavors = [
    # the flat native raster
    ("qed.datasets.native.mmap", "c16", record),
    # the NISAR products
    ("qed.datasets.nisar.products.slc", "complex64", record),
    # the isce2 interferogram
    ("qed.datasets.isce2.int", "real32", record),
    # and the isce2 unwrapped interferogram, whose statistics are a record per band
    ("qed.datasets.isce2.unw", "real32", [record, record]),
]

# go through them
for index, (family, cell, seed) in enumerate(flavors):
    # resolve the factory the way hydration does
    factory = qed.protocols.dataset.pyre_resolveSpecification(spec=family)
    # materialize a twin
    twin = factory(
        # a name of its own, so the flavors do not collide
        name=f"twin{index}",
        # it holds no payload
        hydrated=True,
        # the seed stands in for the sample first contact would have taken
        seed=seed,
        # the layout
        uri=absent,
        cell=cell,
        shape=(512, 512),
        origin=(0, 0),
        tile=(512, 512),
        # and an identity
        selector={"probe": str(index)},
    )
    # it holds no data source, so nothing opened the absent file
    assert twin.data is None
    # it carries the seed it was given
    assert twin.stats == seed
    # and it registered the channels its cell type provides
    assert len(twin.channels) > 0

# the unwrapped flavor is the one that would break under a uniform seed, so check that its
# per-band records reached the right controllers; give the two bands distinct statistics
amplitudeBand = (0.0, 2.0, 10.0)
phaseBand = (-3.0, 0.0, 3.0)
# resolve the flavor
factory = qed.protocols.dataset.pyre_resolveSpecification(spec="qed.datasets.isce2.unw")
# and materialize a twin whose seed carries both
twin = factory(
    name="unwrapped",
    hydrated=True,
    seed=[amplitudeBand, phaseBand],
    uri=absent,
    cell="real32",
    shape=(512, 512),
    origin=(0, 0),
    tile=(512, 512),
    selector={},
)
# the amplitude channel tuned itself from the first band, which is where its mean lives
assert twin.channel(name="amplitude").mean == amplitudeBand[1]


# end of file
