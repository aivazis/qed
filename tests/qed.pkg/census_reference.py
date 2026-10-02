#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check how the store reads the census digests the quality panel compares a raster against: it
keeps the latest cycle of each product, and of two digests of the same cycle the newer one, and a
folder that is missing or a digest that cannot be read only means there is less to compare with
"""

# externals
import json
import os
import tempfile
import types

# support
import journal
import pyre
import qed


def load(folder):
    """
    Read the census digests in {folder} the way the store does
    """
    # a stand in for the store, which only needs the plexus that names the folder
    store = types.SimpleNamespace(_plexus=types.SimpleNamespace(census=folder))
    # read them
    return qed.ux.store._loadCensus(store)


def write(folder, name, product, cycle, stamp):
    """
    Write a digest of {product} for {cycle} as {name} in {folder}, dated {stamp}
    """
    # the path
    path = os.path.join(folder, name)
    # the digest, with just enough in it to tell them apart
    with open(path, "w") as stream:
        # as json
        json.dump({"census": name, "product": product, "cycle": cycle, "measures": {}}, stream)
    # date it
    os.utime(path, (stamp, stamp))
    # all done
    return


# the warnings of a missing folder or an unreadable digest are expected, so they go to the trash
journal.warning("qed.census").device = journal.trash()

# without a folder there is nothing to compare against
assert load(None) == {}
# and a folder that is not there is no different
assert load(pyre.primitives.path("/no/such/census/folder")) == {}

# in a scratch folder
with tempfile.TemporaryDirectory() as folder:
    # two digests of the gcov of cycle 31, the one whose name sorts last written first
    write(folder, "digest-census-gcov-31.json", "gcov", 31, stamp=1_000)
    write(folder, "digest-census-31-gcov.json", "gcov", 31, stamp=2_000)
    # an older cycle of the gslc, written last
    write(folder, "digest-census-31-gslc.json", "gslc", 31, stamp=1_000)
    write(folder, "digest-census-29-gslc.json", "gslc", 29, stamp=3_000)
    # and a digest that cannot be read
    with open(os.path.join(folder, "digest-census-broken.json"), "w") as stream:
        # because it is not json
        stream.write("not json")
    # read them
    references = load(pyre.primitives.path(folder))
    # the newer digest of the same cycle wins, whatever the order of the names
    assert references["gcov"]["census"] == "digest-census-31-gcov.json"
    # the latest cycle wins, whenever it was written
    assert references["gslc"]["cycle"] == 31
    # and the broken digest is left out
    assert set(references) == {"gcov", "gslc"}


# end of file
