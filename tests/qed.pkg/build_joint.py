#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a dataset that builds the first level of the rasters it is read with along with its
own produces the same pyramids as builds that each make their own, level for level and tile for
tile, with the pages fetched counted once, by the build that led
"""

# externals
import shutil

# support
import journal
import pyre
import qed

# the product this driver decimates
product = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gcov.h5"
# a checkout without the fixture has nothing to check
if not product.exists():
    # so bail quietly
    raise SystemExit(0)

# the reader complains about the missing web assets on open; this driver is not the app
journal.warning("qed.cli").deactivate()

# open the product without measuring it
gcov = qed.readers.nisar.gcov(name="joint.gcov", uri=f"file:{product}")
gcov.open(measure=False)
# find the covariance term
covariance = [
    entry
    for entry in gcov.datasets
    if dict(entry.selector) == {"band": "L", "frequency": "B", "cov": "HHHH"}
][0]
# and its mask
mask = covariance.mask


def build(label, joint):
    """
    Build the pyramids of the covariance and its mask in a scratch area named after {label},
    with the covariance leading when {joint}, and hand back the builds
    """
    # the scratch area
    scratch = pyre.primitives.path(__file__).parent / f"build_joint.{label}"
    # start clean
    if scratch.exists():
        shutil.rmtree(str(scratch))
    scratch.mkdir()
    # the workspace the crew builds into
    workspace = qed.workspaces.local(name=f"joint.{label}.workspace")
    workspace.path = str(scratch)
    # the fleet, with a dispatcher of its own
    fleet = qed.nexus.fleet(name=f"joint.{label}.fleet")
    fleet.dispatcher = pyre.ipc.newPSL()
    # the builds
    builds = []

    # a build is over
    def over(build, error=None):
        """
        Stop the loop once every build is over
        """
        # once they all are
        if all(build.done for build in builds):
            # stop
            fleet.dispatcher.stop()
        # all done
        return

    # go through the rasters
    for raster in (covariance, mask):
        # the pyramid the server lays out
        pyramid = qed.readers.nisar.pyramid(reader=gcov, dataset=raster, workspace=workspace)
        # and its build
        builds.append(
            qed.nexus.build(
                reader=gcov,
                dataset=raster,
                pyramid=pyramid,
                fleet=fleet,
                statistics=qed.ux.sample(),
                onDone=over,
                onFailed=over,
            )
        )
    # when asked to
    if joint:
        # the covariance leads its mask
        builds[0].lead(partners=builds[1:])
    # start the builds
    for build in builds:
        build.start()
    # run the loop until they are over
    fleet.dispatcher.watch()
    # let the crew go
    fleet.disband()
    # nothing failed
    assert all(build.error is None for build in builds), [build.error for build in builds]
    # hand back the builds, and where they built
    return builds, scratch


def level(pyramid, exponent):
    """
    Read the occupancy record and the tile file of the level at {exponent} of {pyramid}
    """
    # the record
    occupancy = open(str(pyramid.home / f"level-{exponent:02d}.occupancy"), "rb").read()
    # and the tiles
    tiles = open(str(pyramid.home / f"level-{exponent:02d}.tiles"), "rb").read()
    # hand them off
    return occupancy, tiles


# each raster on its own
alone, aloneArea = build(label="alone", joint=False)
# and the mask along with the covariance
joint, jointArea = build(label="joint", joint=True)

# the covariance led, and the mask followed
assert joint[0].partners == [joint[1]] and joint[1].leader is joint[0]
# the pages were counted once, by the build that led
assert joint[1].fetched == 0
# both ways built every raster all the way down
for mine, theirs in zip(alone, joint):
    # to the same depth
    assert mine.depth == theirs.depth == mine.pyramid.depth() > 1
    # with the same levels
    for exponent in range(1, mine.depth + 1):
        # the same tiles held something, and the tiles that did hold the same cells; the tiles
        # that held nothing were never written, so their bytes are not compared
        occupancy, tiles = level(pyramid=mine.pyramid, exponent=exponent)
        others, otherTiles = level(pyramid=theirs.pyramid, exponent=exponent)
        assert occupancy == others, (mine.dataset.pyre_name, exponent)
        # the size of a tile in the file
        size = len(tiles) // len(occupancy)
        # compare the ones that were written
        for index, held in enumerate(occupancy):
            # skipping the ones that were not
            if held:
                assert (
                    tiles[index * size : (index + 1) * size]
                    == otherTiles[index * size : (index + 1) * size]
                ), (mine.dataset.pyre_name, exponent, index)
    # and the same statistics
    assert mine.statistics.count == theirs.statistics.count
    assert mine.statistics.min == theirs.statistics.min
    assert mine.statistics.max == theirs.statistics.max

# clean up
shutil.rmtree(str(aloneArea))
shutil.rmtree(str(jointArea))


# end of file
