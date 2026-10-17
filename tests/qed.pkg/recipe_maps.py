#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the {dict} traits of a reader travel to a worker as tables

The value of a {kv} is a map that behaves like a dictionary without being one. The recipe must
carry it as a plain dictionary, empty or not: a worker treats anything else as text to be
evaluated, and the text of an empty table, {}, is not a legal expression. The selector table
is derived from the file, so it stays behind for the worker to rebuild
"""

# externals
import pickle

# support
import qed

# a product that only a worker will ever open
uri = "s3://bucket/products/gslc.h5"

# a reader whose maps are all empty, the way a reader starts out before its survey
bare = qed.readers.nisar.gslc(name="maps_bare", uri=uri)
# describe its first contact, the way the server does
recipe = dict(qed.nexus.survey(reader=bare).config)
# its credentials travel as an empty table
assert type(recipe["credentials"]) is dict and recipe["credentials"] == {}
# and so do its selections
assert type(recipe["selections"]) is dict and recipe["selections"] == {}
# while the selector table is left for the worker to derive from the file
assert "selectors" not in recipe
# push the recipe through the wire, and rebuild the reader from it, the way a worker does
worker = qed.readers.nisar.gslc(name="maps_bare_worker", **pickle.loads(pickle.dumps(recipe)))
# its credentials arrive as empty as they left
assert dict(worker.credentials) == {}
# and so do its selections
assert dict(worker.selections) == {}

# a reader whose maps have entries
full = qed.readers.nisar.gslc(
    name="maps_full", uri=uri, credentials={"profile": "st"}, selections={"frequency": "A"}
)
# adopt a selection after construction, the way the team side adopts what a survey reports
full.selections["polarization"] = "HH"
# describe its first contact
recipe = dict(qed.nexus.survey(reader=full).config)
# its credentials travel as a table with the entries the user wrote
assert type(recipe["credentials"]) is dict and recipe["credentials"] == {"profile": "st"}
# its selections travel as a table with whatever the team side holds now
assert type(recipe["selections"]) is dict
assert recipe["selections"] == {"frequency": "A", "polarization": "HH"}
# the reader rebuilt from the recipe on the other side of the wire
worker = qed.readers.nisar.gslc(name="maps_full_worker", **pickle.loads(pickle.dumps(recipe)))
# presents the same credentials
assert dict(worker.credentials) == {"profile": "st"}
# and picks the same datasets
assert dict(worker.selections) == {"frequency": "A", "polarization": "HH"}


# end of file
