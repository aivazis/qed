#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a pyramid built by the crew is the pyramid a single process would have built

The server lays the levels out and hands runs of tiles to the crew; the workers decimate
them and report what each tile held; the server keeps the occupancy, merges the records
into the statistics, and commits each level when its last run reports. This driver runs
that through a real fleet on the covariance fixture and its mask, watches the milestones
arrive in order, and compares what lands on disk with a build that did all the work itself
"""

# externals
import os
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

# the scratch areas: one for the crew, one for the single process
scratch = pyre.primitives.path(__file__).parent / "build.scratch"
alone = pyre.primitives.path(__file__).parent / "build.alone"
# start clean
for area in (scratch, alone):
    # by removing whatever a previous run left behind
    if area.exists():
        shutil.rmtree(str(area))
    # and making the area
    area.mkdir()

# open the product without measuring it; the numbers come out of the build
gcov = qed.readers.nisar.gcov(name="build.gcov", uri=f"file:{product}")
gcov.open(measure=False)
# find the covariance term and its mask
covariance = [
    entry
    for entry in gcov.datasets
    if dict(entry.selector) == {"band": "L", "frequency": "B", "cov": "HHHH"}
][0]
mask = covariance.mask
# the mask is the one companion
assert covariance.companions() == {"mask": mask}

# the workspace the crew builds into
workspace = qed.workspaces.local(name="build.workspace")
workspace.path = str(scratch)
# the fleet, with a dispatcher of its own
fleet = qed.nexus.fleet(name="build.fleet")
fleet.dispatcher = pyre.ipc.newPSL()

# the milestones, in the order they arrive
events = []
# the builds, one per raster
builds = {}


def watch(name):
    """
    Build the hooks that record the milestones of the build of {name}
    """

    def seeded(build):
        """
        The probe's tiles have reported
        """
        events.append((name, "seeded"))
        return

    def progressed(build):
        """
        More of the first level has reported
        """
        events.append((name, "progress"))
        return

    def done(build):
        """
        The pyramid is complete
        """
        events.append((name, "done"))
        # stop the loop when every build is over
        if all(build.done for build in builds.values()):
            fleet.dispatcher.stop()
        return

    def failed(build, error):
        """
        The build failed
        """
        events.append((name, "failed", str(error)))
        # stop the loop when every build is over
        if all(build.done for build in builds.values()):
            fleet.dispatcher.stop()
        return

    # hand back the hooks
    return {
        "onSeeded": seeded,
        "onProgress": progressed,
        "onDone": done,
        "onFailed": failed,
    }


# go through the rasters
for name, raster in (("covariance", covariance), ("mask", mask)):
    # the pyramid the server lays out
    pyramid = qed.readers.nisar.pyramid(reader=gcov, dataset=raster, workspace=workspace)
    # and the build
    builds[name] = qed.nexus.build(
        reader=gcov,
        dataset=raster,
        pyramid=pyramid,
        fleet=fleet,
        statistics=qed.ux.sample(),
        **watch(name=name),
    )
# start them
for build in builds.values():
    build.start()
# and run the loop until they are over
fleet.dispatcher.watch()
# let the crew go
fleet.disband()

# nothing failed
assert not [event for event in events if event[1] == "failed"], events
# both builds finished
assert (("covariance", "done") in events) and (("mask", "done") in events)
# the covariance was seeded, and before it was done
assert events.index(("covariance", "seeded")) < events.index(("covariance", "done"))
# every build seeds; whether anyone listens is the store's business
assert events.index(("mask", "seeded")) < events.index(("mask", "done"))
# the numbers moved along the way
assert ("covariance", "progress") in events

# every level of both rasters is on disk
for name, build in builds.items():
    # the pyramid
    pyramid = build.pyramid
    # the build went all the way
    assert build.depth == pyramid.depth() > 1
    # go through the levels
    for exponent in range(1, build.depth + 1):
        # each one exists
        assert pyramid.holds(exponent=exponent), (name, exponent)
        # its record names as many tiles as the level has
        _, _, grid = pyramid.layout(exponent=exponent)
        record = open(str(pyramid.home / f"level-{exponent:02d}.occupancy"), "rb").read()
        assert len(record) == grid[0] * grid[1], (name, exponent)
    # and the sidecar is beside them
    assert pyramid.sidecar.exists(), name

# a single process builds the same covariance pyramid on its own
solo = qed.workspaces.local(name="build.solo")
solo.path = str(alone)
reference = qed.readers.nisar.pyramid(reader=gcov, dataset=covariance, workspace=solo)
reference.build()
# it reaches the same depth
assert reference.reach() == builds["covariance"].depth
# the records of every level are identical: the same tiles held something
for exponent in range(1, reference.reach() + 1):
    # the crew's record
    crew = open(
        str(builds["covariance"].pyramid.home / f"level-{exponent:02d}.occupancy"), "rb"
    ).read()
    # and the single process's
    mine = open(str(reference.home / f"level-{exponent:02d}.occupancy"), "rb").read()
    # match
    assert crew == mine, exponent
# and so are the statistics, up to the order the records were merged in
theirs = builds["covariance"].statistics
assert theirs.count == reference.statistics.count
assert theirs.min == reference.statistics.min
assert theirs.max == reference.statistics.max
assert abs(theirs.mean - reference.statistics.mean) < 1e-9 * abs(reference.statistics.mean)
assert abs(theirs.m2 - reference.statistics.m2) < 1e-9 * abs(reference.statistics.m2)

# a reader attaching to the crew's levels serves the same cells as one attaching to the
# other build, over a window that holds data
kernels = covariance.kernels
datatype = covariance.datatype.htype
theirs = qed.readers.nisar.pyramid(reader=gcov, dataset=covariance, workspace=workspace)
theirs.attach()
reference.attach()
# the window
window = {"origin": (512, 512), "shape": (64, 64), "stride": (1, 1)}
# go through the levels
for exponent in range(1, reference.reach() + 1):
    # the samples agree
    assert kernels.sample(
        source=theirs.at(exponent=exponent), datatype=datatype, **window
    ) == kernels.sample(source=reference.at(exponent=exponent), datatype=datatype, **window)
# and the first level holds data there
assert kernels.sample(source=theirs.at(exponent=1), datatype=datatype, **window)[0] > 0

# let go
theirs.close()
reference.close()
# and clean up
for area in (scratch, alone):
    shutil.rmtree(str(area))

# end of file
