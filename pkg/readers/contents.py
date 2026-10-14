# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# describe what a reader found in its file
def contents(*, reader) -> dict:
    """
    Describe what {reader} found in its file, the way its contents hold it: the axes its selectors
    span, with the values each may take, and its datasets, each known by its selector
    """
    # the axes, with the values each may take
    axes = dict(reader.selectors)
    # the datasets, each known by its value along every axis, along with the dataset itself
    entries = [
        {"selector": dict(dataset.selector), "source": dataset} for dataset in reader.datasets
    ]
    # hand them off
    return {"axes": axes, "entries": entries}


# end of file
