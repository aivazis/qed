#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a render which depends on a measured scalar survives the trip to a worker

A crew member rebuilds its reader without sampling, on the grounds that the client's
controller state is about to be installed over anything a sample would produce; so the
measurement the team side made has to travel with the task, or every number a channel
derives from it and keeps outside its traits -- the reference amplitude of the unwrapped
power law, for one -- arrives at its default and the tile comes back wrong
"""

# externals
import pickle
import struct
import types

# support
import qed

# the layout of the synthetic product
LINES, SAMPLES = 48, 64
# the amplitudes: well away from unity, so a channel that missed the measurement renders
# something visibly different
AMPLITUDES = [
    100.0 + (line * SAMPLES + sample) % 57 for line in range(LINES) for sample in range(SAMPLES)
]
# and the phases, spanning a few radians on either side of zero
PHASES = [0.3 * (line - LINES // 2) for line in range(LINES) for _ in range(SAMPLES)]
# the geometry of the tiles this test renders
ZOOM, ORIGIN, SHAPE = (0, 0), (0, 0), (32, 32)
# the name of the product
URI = "measured.unw"
# the channels whose render depends on the measurement
TAGS = ("complex", "amplitude")


def synthesize():
    """
    Write an unwrapped interferogram: a line of amplitudes followed by a line of phases
    """
    # open the product
    with open(URI, "wb") as product:
        # go through the lines
        for line in range(LINES):
            # the span of this line
            span = slice(line * SAMPLES, (line + 1) * SAMPLES)
            # write its amplitudes
            product.write(struct.pack(f"{SAMPLES}f", *AMPLITUDES[span]))
            # followed by its phases
            product.write(struct.pack(f"{SAMPLES}f", *PHASES[span]))
    # all done
    return


def render(dataset, tag):
    """
    Render a tile of {tag} off {dataset} using its own pipeline
    """
    # get the pipeline
    pipeline = dataset.channel(name=tag)
    # render and reduce to bytes so tiles can be compared
    return bytes(
        memoryview(dataset.render(channel=pipeline, zoom=ZOOM, origin=ORIGIN, shape=SHAPE))
    )


def dispatch(reader, dataset, tag, readers):
    """
    Push a tile request for {tag} through the wire and execute it the way a worker does
    """
    # assemble a stand-in for the view state behind a tile request
    view = types.SimpleNamespace(
        reader=reader, dataset=dataset, pipeline=lambda channel: dataset.channel(name=tag)
    )
    # describe the tile as a task
    task = qed.nexus.tile(
        view=view, channel=f"measured.data.{tag}", zoom=ZOOM, origin=ORIGIN, shape=SHAPE
    )
    # marshal it the way the team hands work to a crew member
    task = pickle.loads(pickle.dumps(task))
    # execute it on a reader rebuilt from the recipe it carries
    spool = task.execute(readers=readers)
    # read the payload back
    spool.file.seek(0)
    tile = spool.file.read()
    # release the spool
    spool.close()
    # hand back the tile and the task that produced it
    return tile, task


def test():
    """
    The tiles a worker renders are the ones the team side would have produced
    """
    # make the product
    synthesize()

    # build a reader over it
    reader = qed.readers.isce2.unw(name="measured", uri=URI, shape=(LINES, SAMPLES))
    # and make first contact, which samples the data the way the server does
    reader.open()
    # get the dataset it discovered
    (dataset,) = reader.datasets
    # the mean amplitude the sample found is nowhere near the value a channel that was
    # never tuned would carry
    assert dataset.stats[0][1] > 100

    # the registry a worker keeps, shared across tasks the way a crew member shares it
    readers = {}
    # go through the channels
    for tag in TAGS:
        # the pipeline picked up the measurement at first contact
        assert dataset.channel(name=tag).mean == dataset.stats[0][1]
        # the tile a worker renders matches the one produced here
        tile, task = dispatch(reader=reader, dataset=dataset, tag=tag, readers=readers)
        assert tile == render(dataset=dataset, tag=tag)
        # and the measurement is part of what makes this request what it is
        assert task.stats is not None

    # now the part that has teeth: hand the team side dataset numbers no sample of this
    # product would ever produce, so a worker that measured for itself, or never tuned at
    # all, cannot arrive at the same pixels by luck
    amplitude, phase = dataset.stats
    # a mean an order of magnitude off, with the bounds left alone
    low, mean, high = amplitude
    dataset.measure(seed=[(low, 10 * mean, high), phase])
    # every channel followed the new numbers
    for tag in TAGS:
        assert dataset.channel(name=tag).mean == 10 * mean

    # the worker must follow them too, on the reader it already holds from the round above
    for tag in TAGS:
        # render the tile through the wire
        tile, _ = dispatch(reader=reader, dataset=dataset, tag=tag, readers=readers)
        # and compare against the team side
        assert tile == render(dataset=dataset, tag=tag)
        # the worker's own copy of the dataset adopted the seed rather than sampling
        (twin,) = readers["measured"].datasets
        assert twin.stats[0][1] == 10 * mean
        assert twin.channel(name=tag).mean == 10 * mean

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
