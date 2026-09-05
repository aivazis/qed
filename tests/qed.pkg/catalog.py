#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the catalog stays in the order the user registered their products in

Sources are listed in the order they were added, which is the order they appear in the
configuration file. A source is re-registered when its survey completes, so that the dataset
index reflects what the survey discovered -- and surveys complete in whatever order the crews
happen to get to them. If re-registering moved a source to the end of the pile, the catalog
would quietly sort itself by whichever product finished first, and the client would show a
different order on every run
"""

# support
# the registry is internal to the ux package, so reach in
from qed.ux.Sources import Sources


# a stand-in for a data source: the registry only asks for a name and a list of datasets
class Source:
    """
    Something the registry will accept as a source
    """

    # metamethods
    def __init__(self, name, datasets=(), **kwds):
        # chain up
        super().__init__(**kwds)
        # take my name, which is what the registry keys me by
        self.pyre_name = name
        # and whatever i claim to hold
        self.datasets = list(datasets)
        # all done
        return


# a stand-in for one of its datasets
class Dataset:
    """
    Something the registry will accept as a dataset
    """

    # metamethods
    def __init__(self, name, **kwds):
        # chain up
        super().__init__(**kwds)
        # my name is my identity in the index
        self.pyre_name = name
        # all done
        return


# make a registry
registry = Sources()
# and register three products, in the order a configuration file would list them
for tag in ("first", "second", "third"):
    registry.addSource(source=Source(name=tag, datasets=[Dataset(name=f"{tag}.data")]))
# which is the order it reports them in
assert [source.pyre_name for source in registry.sources()] == [
    "first",
    "second",
    "third",
]

# now let the middle one finish its survey and re-register, carrying the datasets the survey
# found; this is what the store does when a crew reports back
registry.addSource(source=Source(name="second", datasets=[Dataset(name="second.discovered")]))
# the catalog must not have moved
assert [source.pyre_name for source in registry.sources()] == [
    "first",
    "second",
    "third",
]
# and the index must carry what the survey found rather than what stood there before
names = {dataset.pyre_name for dataset in registry.datasets()}
assert "second.discovered" in names
assert "second.data" not in names

# let them all report back, in an order no configuration file would produce
for tag in ("third", "first", "second"):
    registry.addSource(source=Source(name=tag, datasets=[Dataset(name=f"{tag}.data")]))
# the catalog still reflects the configuration rather than the finishing order
assert [source.pyre_name for source in registry.sources()] == [
    "first",
    "second",
    "third",
]

# a source that genuinely departs does leave
registry.removeSource(name="second")
assert [source.pyre_name for source in registry.sources()] == ["first", "third"]
# and taking its place at the end is then correct, since it is a new arrival
registry.addSource(source=Source(name="second", datasets=[]))
assert [source.pyre_name for source in registry.sources()] == [
    "first",
    "third",
    "second",
]


# end of file
