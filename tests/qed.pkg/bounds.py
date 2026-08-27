#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the dispatcher's tile bounds predicate accepts legal requests and rejects the ones
that overhang the raster, whose source footprint would crash the native render pipeline
"""

# support
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# initiate first contact with the sources, the way the server does when it is ready
ux.store.open()
# get the reader
reader, *_ = ux.store.sources
# and its dataset; the local fixture is 65x65
dataset, *_ = reader.datasets

# a tile that fits
assert ux._dataInBounds(dataset=dataset, zoom=(0, 0), origin=(0, 0), shape=(64, 64))
# the largest tile that fits exactly
assert ux._dataInBounds(dataset=dataset, zoom=(0, 0), origin=(0, 0), shape=(65, 65))
# an interior tile that reaches the far corner exactly
assert ux._dataInBounds(dataset=dataset, zoom=(0, 0), origin=(1, 1), shape=(64, 64))

# a tile that overhangs the trailing edge
assert not ux._dataInBounds(dataset=dataset, zoom=(0, 0), origin=(2, 2), shape=(64, 64))
# a tile that starts before the raster
assert not ux._dataInBounds(dataset=dataset, zoom=(0, 0), origin=(-1, 0), shape=(8, 8))
# a degenerate tile
assert not ux._dataInBounds(dataset=dataset, zoom=(0, 0), origin=(0, 0), shape=(0, 8))

# zoomed requests: at zoom 1, the stride is 2, so the source footprint doubles
# the whole raster at zoom 1
assert ux._dataInBounds(dataset=dataset, zoom=(1, 1), origin=(0, 0), shape=(32, 32))
# one past the zoomed extent overhangs the source
assert not ux._dataInBounds(dataset=dataset, zoom=(1, 1), origin=(0, 0), shape=(33, 33))
# an anisotropic zoom is checked per axis
assert ux._dataInBounds(dataset=dataset, zoom=(1, 0), origin=(0, 0), shape=(32, 65))
assert not ux._dataInBounds(dataset=dataset, zoom=(1, 0), origin=(0, 0), shape=(32, 66))

# profile points: (line, sample) pairs that must name real cells of the 65x65 raster
# a path within the raster
assert ux._profileInBounds(dataset=dataset, points=((0, 0), (32, 32), (64, 64)))
# an empty path is trivially in bounds
assert ux._profileInBounds(dataset=dataset, points=())
# a point at the extent reads one past the last cell
assert not ux._profileInBounds(dataset=dataset, points=((0, 0), (65, 64)))
assert not ux._profileInBounds(dataset=dataset, points=((64, 65),))
# a point before the raster
assert not ux._profileInBounds(dataset=dataset, points=((-1, 0),))
# a malformed point
assert not ux._profileInBounds(dataset=dataset, points=((1, 2, 3),))


# end of file
