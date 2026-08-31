#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a render tells the two kinds of absence apart

A raster has two ways of saying it has nothing to record at a cell: the fill value its file
declares, and a nan. They are supposed to be the same thing, and on the NISAR geocoded
products they are not -- a GCOV declares the library's default fill of zero and then frames
its data in nans. That disagreement is a bug in whatever wrote the product, it cannot be seen
in the metadata, and until now it could not be seen in the picture either, because both cases
came out of the arithmetic as some indistinguishable dark colour. So the render paints them
differently: absence the file admits to is the faint brick red the masked channels already use
for their out-of-swath margin, and a nan the file never declared gets a discreet teal of its own
"""

# externals
from collections import Counter

# support
import journal
import pyre
import qed


# the colors a render uses to spell absence, as the picture stores them
def census(tile, shape):
    """
    Count the colors of a rendered tile, reported the way a person reads them
    """
    # the payload is the tail of the bitmap, three bytes per pixel
    raw = bytes(memoryview(tile))
    body = raw[len(raw) - shape[0] * shape[1] * 3 :]
    # gather them, remembering that a bitmap stores its channels in reverse
    tally = Counter(
        (body[at + 2], body[at + 1], body[at]) for at in range(0, len(body), 3)
    )
    # hand back the pile
    return tally


# the NISAR fixture this driver reads; part of the shared test data tree
product = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gcov.h5"
# if it has not been generated
if not product.exists():
    # there is nothing to check
    raise SystemExit(0)

# quiet the configuration chatter
journal.warning("qed.cli").deactivate()

# open the product
reader = qed.readers.nisar.gcov(name="absence", uri=f"file:{product}")
reader.open(measure=False)
# take a covariance term of the smaller frequency
covariance = [
    entry
    for entry in reader.datasets
    if dict(entry.selector) == {"band": "L", "frequency": "B", "cov": "HHHH"}
][0]
# and give it a display range, since a channel cannot render without one
covariance.measure()

# this is the product whose two answers disagree: it declares a fill of zero
assert covariance.data.dataset.fillValue == 0.0
assert covariance.fill == 0.0
# while writing nans, which is why the corner of the raster holds no valid cell at all
corner = {"origin": (0, 0), "shape": (64, 64)}
assert (
    covariance.kernels.sample(
        source=covariance.data.dataset,
        datatype=covariance.datatype.htype,
        stride=(1, 1),
        **corner,
    )[0]
    == 0
)

# the channels that build their own pipeline paint the difference
for tag in ("covariance", "covarianceMasked"):
    # render the corner, which is nothing but absence
    tile = covariance.render(
        channel=covariance.channel(name=tag), zoom=(0, 0), **corner
    )
    # take stock of what came out
    tally = census(tile=tile, shape=corner["shape"])
    # every cell of it is a nan the product never declared, so the whole tile is one color
    assert len(tally) == 1
    # and it is the teal that names undeclared absence
    assert next(iter(tally)) == (10, 28, 25)

# a product that declares a nan and writes one is consistent with itself, and the render
# says so with the brick red of an announced absence rather than the teal of a surprise
tile = qed.libqed.nisar.real.covariance(
    source=covariance.data.dataset,
    mask=covariance.mask.data.dataset,
    datatype=covariance.datatype.htype,
    stride=(1, 1),
    min=covariance.stats[0],
    max=covariance.stats[2],
    fill=float("nan"),
    **corner,
)
# so that corner comes back in the color the masked channels use for their own margin
tally = census(tile=tile, shape=corner["shape"])
assert len(tally) == 1
assert next(iter(tally)) == (25, 12, 12)

# a channel whose kernel delegates to the shared {native} pipelines cannot be told what the
# product declared, and must not be asked: it would be an argument the kernel cannot take
assert qed.readers.nisar.products.channels.covariance.absence is True
assert qed.readers.nisar.products.channels.amplitude.absence is False


# end of file
