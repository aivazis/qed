#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a build reports every level of its pyramid as it comes into existence, in order,
that its description tells the level under construction and how deep the pyramid is available,
and that the record of the preparation behind it describes the dataset by its shallowest raster
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

# the scratch area
scratch = pyre.primitives.path(__file__).parent / "build_levels.scratch"
# start clean, by removing whatever a previous run left behind
if scratch.exists():
    shutil.rmtree(str(scratch))
# and making the area
scratch.mkdir()

# open the product without measuring it
gcov = qed.readers.nisar.gcov(name="levels.gcov", uri=f"file:{product}")
gcov.open(measure=False)
# find the covariance term
covariance = [
    entry
    for entry in gcov.datasets
    if dict(entry.selector) == {"band": "L", "frequency": "B", "cov": "HHHH"}
][0]
# and its mask
mask = covariance.mask

# the workspace the crew builds into
workspace = qed.workspaces.local(name="levels.workspace")
workspace.path = str(scratch)
# the fleet, with a dispatcher of its own
fleet = qed.nexus.fleet(name="levels.fleet")
fleet.dispatcher = pyre.ipc.newPSL()

# the record of the preparation, the way the store keeps it
record = qed.ux.preparation(name=covariance.pyre_name)
# what each build said about itself whenever a level came into existence
snapshots = []


# a level exists
def leveled(build, exponent):
    """
    Record the level that came into existence and what the build says about itself
    """
    # save both
    snapshots.append((build.dataset.pyre_name, exponent, build.describe()))
    # all done
    return


# a build is over
def over(build, error=None):
    """
    Stop the loop once every build is over
    """
    # a failure is noted in the record
    if error is not None:
        record.fail(error=error)
    # once they all are
    if all(build.done for build in record.builds):
        # stop
        fleet.dispatcher.stop()
    # all done
    return


# build the pyramids of the covariance and its mask
for raster in (covariance, mask):
    # the pyramid the server lays out
    pyramid = qed.readers.nisar.pyramid(reader=gcov, dataset=raster, workspace=workspace)
    # and its build
    record.builds.append(
        qed.nexus.build(
            reader=gcov,
            dataset=raster,
            pyramid=pyramid,
            fleet=fleet,
            statistics=qed.ux.sample(),
            onLevel=leveled,
            onDone=over,
            onFailed=over,
        )
    )

# before the builds start, nothing is available
before = record.describe()
assert before["status"] == "working"
assert before["reach"] == 0
assert before["started"] is not None and before["finished"] is None

# start the builds
for build in record.builds:
    build.start()
# and run the loop until they are over
fleet.dispatcher.watch()
# let the crew go
fleet.disband()
# the work succeeded
record.succeed()

# every raster reported every one of its levels, in order
for build in record.builds:
    # the levels this raster reported
    levels = [exponent for name, exponent, _ in snapshots if name == build.dataset.pyre_name]
    # are all of them, in order
    assert levels == list(range(1, build.depth + 1)), levels
# and at the moment a level came into existence
for name, exponent, snapshot in snapshots:
    # it was the level under construction
    assert snapshot["level"] == exponent, snapshot
    # with every one of its runs back
    assert snapshot["runs"] > 0 and snapshot["outstanding"] == 0, snapshot
    # and the pyramid available down to it
    assert snapshot["reach"] == exponent, snapshot

# once the builds are over
after = record.describe()
# the work is done
assert after["status"] == "ready"
assert after["finished"] is not None and after["finished"] >= after["started"]
# every raster is available to the bottom of its pyramid, with nothing under construction
for raster in after["rasters"]:
    assert raster["reach"] == raster["depth"] > 1, raster
    assert raster["level"] is None and raster["runs"] == 0 and raster["outstanding"] == 0
# and the dataset is as deep as its shallowest raster
assert after["depth"] == min(raster["depth"] for raster in after["rasters"])
assert after["reach"] == after["depth"]

# clean up
shutil.rmtree(str(scratch))


# end of file
