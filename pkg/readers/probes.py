# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import journal


# estimate the statistics of a dataset by probing it in several places
def probe(dataset, windows: int = 4, extent: int = 256) -> tuple:
    """
    Estimate the display range of {dataset} from a grid of {windows}x{windows} sample
    windows of up to {extent} cells on a side, spread across its full extent

    A single window in the middle of the raster is a poor estimator: a geocoded product
    frames its data inside a much larger grid of fill, so the middle is often empty, and a
    swath that runs along one edge is invisible from the center no matter how large the
    window is. Spreading a few small windows over the whole extent costs about as much and
    finds data wherever it happens to sit.

    Windows are used rather than a strided pass over everything because stride touches
    every chunk of the file: on a compressed product that means decompressing all of it,
    which is minutes of work for a seed. Each window, by contrast, touches only the chunks
    it lands in
    """
    # unpack the extent of the raster
    shape = tuple(dataset.shape)
    # size a window, keeping it inside the raster on both axes
    span = tuple(min(extent, axis) for axis in shape)
    # the last origin that still fits a whole window on each axis
    last = tuple(axis - width for axis, width in zip(shape, span))
    # the number of stops per axis, never more than the axis can hold distinctly
    stops = tuple(min(windows, axis // width + 1) for axis, width in zip(last, span))
    # plan the origins: evenly spaced from the first row to the last that fits
    origins = [
        (
            last[0] * i // max(stops[0] - 1, 1),
            last[1] * j // max(stops[1] - 1, 1),
        )
        for i in range(stops[0])
        for j in range(stops[1])
    ]

    # the running merge of everything the windows found
    cells, low, high, total = 0, None, None, 0.0
    # go through the planned windows
    for origin in origins:
        # sample this one at full resolution; the record is mergeable
        count, minimum, mean, _, maximum = dataset.sample(
            zoom=(0, 0), origin=origin, shape=span
        )
        # a window of nothing but fill contributes nothing
        if count == 0:
            # so skip it
            continue
        # fold in what it found
        cells += count
        total += mean * count
        # and stretch the extrema
        low = minimum if low is None else min(low, minimum)
        high = maximum if high is None else max(high, maximum)

    # if every window came back empty
    if cells == 0:
        # make a channel
        channel = journal.warning("qed.readers.statistics")
        # say so plainly: the numbers below are a guess, not a measurement, and a display
        # built on them will be wrong as soon as real data appears
        channel.line(f"found no data in '{dataset.pyre_name}'")
        channel.line(
            f"sampled {len(origins)} windows of {span} across an extent of {shape}"
        )
        channel.line(f"and every one of them held nothing but fill")
        channel.line(f"the display range is a guess until a tile finds something")
        # flush
        channel.log()
        # hand back nominal values; a range has to exist, since the range controllers of a
        # linear channel cannot render without one
        return 0.0, 0.5, 1.0

    # otherwise, report what the windows found
    return low, total / cells, high


# end of file
