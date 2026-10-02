#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a view is shown no further out than the levels of its dataset that can be shown: a
dataset supports as many levels as it takes to halve it into a single tile, while its pyramid is
being built it shows only the levels that exist, and a view kept at a deeper level is shown at the
deepest one that exists, without losing the level it keeps
"""

# externals
import types

# support
import qed

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
# get the store
store = ux.store


# a build that describes itself without building anything
class Built:
    """
    A stand-in for the build of a raster, with a fixed reach
    """

    # metamethods
    def __init__(self, reach, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the reach
        self.reach = reach
        # all done
        return

    # interface
    def describe(self):
        """
        Describe the build
        """
        # enough for the store to find the reach
        return {"raster": "reach.raster", "depth": 5, "reach": self.reach}


# a zoom state, the way a view keeps it
class Zoom:
    """
    A stand-in for the zoom of a view
    """

    # metamethods
    def __init__(self, level, **kwds):
        # chain up
        super().__init__(**kwds)
        # both axes at the same level
        self.horizontal = level
        self.vertical = level
        # coupled, and different from the defaults
        self.coupled = True
        self.dirty = True
        # named
        self.pyre_name = "reach.zoom"
        # all done
        return

    # interface
    def pyre_family(self):
        """
        The family of the zoom
        """
        # easy enough
        return "qed.ux.zoom.zoom"


# a raster of 10000 by 10000 in tiles of 512 by 512, which halves five times into one tile
large = types.SimpleNamespace(pyre_name="reach.large", shape=(10000, 10000), tile=(512, 512))
# and one that fits in a tile to begin with
small = types.SimpleNamespace(pyre_name="reach.small", shape=(65, 65), tile=(512, 512))

# the depth follows the extent
assert store.depth(dataset=large) == 5
assert store.depth(dataset=small) == 0
assert store.depth(dataset=None) == 0
# a dataset without a pyramid shows every level it supports
assert store.reach(dataset=large) == 5

# a dataset whose pyramid is being built
record = qed.ux.preparation(name=large.pyre_name)
# whose rasters reach two and three levels
record.builds = [Built(reach=2), Built(reach=3)]
# file it where the store keeps such records
store._preparations[record.name] = record
# shows the levels its shallowest raster has
assert store.reach(dataset=large) == 2
# and still does once it is far enough along to render by
record.seed()
assert store.reach(dataset=large) == 2

# a view of it, kept five levels out
view = types.SimpleNamespace(dataset=large, zoom=Zoom(level=-5))
# is shown two levels out
shown = store.shown(view=view)
assert (shown.horizontal, shown.vertical) == (-2, -2)
# without losing the level it keeps
assert (view.zoom.horizontal, view.zoom.vertical) == (-5, -5)
# and with everything else the view's own
assert shown.pyre_name == "reach.zoom" and shown.pyre_family() == "qed.ux.zoom.zoom"
assert shown.coupled and shown.dirty
# a view zoomed in is shown as it is
assert store.shown(view=types.SimpleNamespace(dataset=large, zoom=Zoom(level=1))).horizontal == 1

# once the build is done
record.succeed()
# every level can be shown
assert store.reach(dataset=large) == 5
# and the view is shown where it is kept
assert store.shown(view=view).horizontal == -5

# a raster whose build failed after one level
other = types.SimpleNamespace(pyre_name="reach.other", shape=(10000, 10000), tile=(512, 512))
failed = qed.ux.preparation(name=other.pyre_name)
failed.builds = [Built(reach=1)]
failed.fail(error="no pages")
store._preparations[failed.name] = failed
# shows every level as well, the ones it did not build read from the product, as before
assert store.reach(dataset=other) == 5


# end of file
