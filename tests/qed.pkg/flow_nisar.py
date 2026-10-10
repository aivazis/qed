#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Render tiles through the channels of nisar products that have recipes, once with their kernels
and once with the pipelines of their recipes, and check that they match byte for byte, reading
both a dataset of the product and a level of a pyramid built over it, at several zoom levels,
with and without the mask of the product
"""

# externals
import types
import uuid

# support
import journal
import pyre
import qed

# the fixtures this driver reads; part of the shared test data tree
gslc = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gslc.h5"
gcov = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gcov.h5"
# if they have not been generated
if not gslc.exists() or not gcov.exists():
    # there is nothing to check
    raise SystemExit(0)

# the directory that holds the pyramid level this driver builds
scratch = pyre.primitives.path(__file__).parent / "flow_nisar.scratch"


# compare the two engines of {channel} over {tiles} of {source}, each time after {configure}
def compare(channel, source, datatype, tiles, configurations):
    """
    Render each of the {tiles} of {source} through both engines of {channel}, under each of
    the {configurations}, and check that they agree byte for byte
    """
    # go through the configurations
    for configure in configurations:
        # apply it
        configure(channel)
        # go through the tiles
        for origin, shape, zoom in tiles:
            # render with the kernel
            channel.engine = "iterators"
            expected = bytes(
                memoryview(
                    channel.tile(
                        source=source, datatype=datatype, zoom=zoom, origin=origin, shape=shape
                    )
                )
            )
            # and with the pipeline
            channel.engine = "flow"
            rendered = channel.tile(
                source=source, datatype=datatype, zoom=zoom, origin=origin, shape=shape
            )
            # they must agree
            assert rendered == expected, (channel.pyre_name, origin, shape, zoom)
    # all done
    return


# make a channel of the given {kind}
def channel(kind):
    """
    Make a channel of nisar products of the given {kind}, under a name of its own
    """
    # pyre hands back the old instance for a name it has seen before
    return getattr(qed.readers.nisar.products.channels, kind)(
        name=f"flow_nisar.{kind}.{uuid.uuid1()}"
    )


# a stand-in for a dataset whose every zoom is served by {source}, owing {depth} fewer halvings
def served(source, depth=0, companions=None, fill=float("nan")):
    """
    Make a dataset stand-in whose renders read {source}, a dataset or a pyramid level that
    holds the cells already decimated {depth} times, along with its {companions}, and that
    declares {fill} as what it writes where it has no data
    """
    # the answer to a resolution: the source, its companions, and what is left of the zoom
    resolve = lambda zoom: (source, dict(companions or {}), tuple(level - depth for level in zoom))
    # wrap it
    return types.SimpleNamespace(resolve=resolve, fill=fill)


# build the first level of a pyramid over {dataset}, filled in only at {origins}
def level(dataset, origins, name="level1"):
    """
    Build the level of {dataset} decimated once, writing the tiles at {origins}, in files named
    after {name}, and return a reader of it
    """
    # the storage of the cells of the dataset
    storage = getattr(qed.libqed.pyramid, dataset.datatype.cell)
    # the shape of the level, and the shape of its tiles
    extent = tuple(axis // 2 for axis in dataset.shape)
    tile = tuple(dataset.tile)
    # the files of the level
    tiles = str(scratch / f"{name}.tiles")
    record = scratch / f"{name}.occupancy"
    # make the level
    storage.Draft.create(tiles=tiles, shape=extent, tile=tile)
    # the number of tiles along each axis
    rows = (extent[0] + tile[0] - 1) // tile[0]
    columns = (extent[1] + tile[1] - 1) // tile[1]
    # the occupancy record, naming the tiles about to be written
    occupancy = bytearray(rows * columns)
    # go through them
    for origin in origins:
        # mark each one
        occupancy[(origin[0] // tile[0]) * columns + origin[1] // tile[1]] = 1
    # write the record
    with open(str(record), "wb") as stream:
        # all at once
        stream.write(bytes(occupancy))
    # open the level for writing
    draft = storage.Draft(tiles=tiles, shape=extent, tile=tile)
    # go through the tiles
    for origin in origins:
        # and fill each one with the cells of the dataset at stride two
        dataset.kernels.decimate(
            source=dataset.data.dataset,
            destination=draft,
            datatype=dataset.datatype.htype,
            origin=origin,
            shape=tile,
            stride=(2, 2),
        )
    # let the draft go, so the cells reach the file
    del draft
    # the value of the cells no tile covers: the blank of the cell type, or zero for the masks,
    # whose cells have none
    blank = dataset.cell.blank if dataset.cell.blank is not None else 0
    # and read the level back
    return storage.Level(tiles=tiles, occupancy=str(record), shape=extent, tile=tile, fill=blank)


# the tiles of a level {depth} halvings deep that cover the windows of {tiles}
def cover(tiles, depth, tile):
    """
    The origins of the tiles of shape {tile} of the level {depth} halvings deep that hold the
    cells the windows of {tiles} read
    """
    # the pile
    origins = set()
    # go through the windows
    for origin, shape, zoom in tiles:
        # what is left of the zoom past the level
        stride = tuple(2 ** (level - depth) for level in zoom)
        # the first and last cells of the level the window reads, along each axis
        first = tuple(o * s for o, s in zip(origin, stride))
        last = tuple((o + n - 1) * s for o, n, s in zip(origin, shape, stride))
        # the tiles they span
        rows = range(first[0] // tile[0], last[0] // tile[0] + 1)
        columns = range(first[1] // tile[1], last[1] // tile[1] + 1)
        # add them to the pile
        origins.update((r * tile[0], c * tile[1]) for r in rows for c in columns)
    # hand them off, in order
    return sorted(origins)


# the driver
def test():
    """
    Compare the engines of the channels of nisar products over datasets and pyramid levels
    """
    # quiet the configuration chatter
    journal.warning("qed.cli").deactivate()
    # make room for the pyramid level
    scratch.mkdir(parents=True, exist_ok=True)

    # the range of a linear controller
    def ranged(low, high):
        """
        Set the range of the controller of a channel
        """

        # the configuration
        def configure(channel):
            # set the range
            channel.range.low = low
            channel.range.high = high
            # all done
            return

        # hand it off
        return configure

    # the decades of the amplitude
    def decades(low, high):
        """
        Set the range of the amplitude of a channel, in decades
        """

        # the configuration
        def configure(channel):
            # set the range
            channel.amplitude.low = low
            channel.amplitude.high = high
            # all done
            return

        # hand it off
        return configure

    # the range of the phase, and the constant parts of the color
    def wheel(low, high, saturation, brightness=None):
        """
        Set the range of the phase of a channel, and its saturation and brightness
        """

        # the configuration
        def configure(channel):
            # set the range of the phase
            channel.phase.low = low
            channel.phase.high = high
            # the saturation
            channel.saturation.value = saturation
            # and the brightness, if the channel has one
            if brightness is not None:
                # set it
                channel.brightness.value = brightness
            # all done
            return

        # hand it off
        return configure

    # the range of the phase, and the brightness
    def lit(low, high, brightness):
        """
        Set the range of the phase of a channel, and its brightness
        """

        # the configuration
        def configure(channel):
            # set the range of the phase
            channel.phase.low = low
            channel.phase.high = high
            # and the brightness
            channel.brightness.value = brightness
            # all done
            return

        # hand it off
        return configure

    # the whole complex value
    def complete(low, high, phaseLow, phaseHigh, saturation):
        """
        Set the amplitude, the phase, and the saturation of a complex channel
        """

        # the configuration
        def configure(channel):
            # the amplitude
            decades(low, high)(channel)
            # the phase and the saturation
            wheel(phaseLow, phaseHigh, saturation)(channel)
            # all done
            return

        # hand it off
        return configure

    # the configurations of the channels of complex cells
    complexes = {
        "amplitude": [decades(-4, -1), decades(-3, 0)],
        "real": [ranged(-0.1, 0.1), ranged(-1, 1)],
        "imaginary": [ranged(-0.1, 0.1), ranged(-1, 1)],
        "phase": [wheel(0, 1, 1, 1), wheel(0.25, 0.75, 0.5, 0.8)],
        "complex": [complete(-4, -1, 0, 1, 0.5), complete(-3, 0, 0.1, 0.9, 1)],
    }

    # open the slc product
    reader = qed.readers.nisar.gslc(name="flow_nisar.gslc", uri=f"file:{gslc}")
    reader.open(measure=False)
    # its first dataset
    base, *_ = reader.datasets
    # the tiles that land on the data, at full resolution and zoomed out, evenly and not
    tiles = [
        ((32768, 10240), (64, 64), (0, 0)),
        ((16384, 5120), (37, 53), (1, 1)),
        ((8192, 5120), (29, 31), (2, 1)),
    ]
    # go through the channels
    for kind, configurations in complexes.items():
        # read off the dataset
        compare(
            channel=channel(kind),
            source=served(source=base.data.dataset),
            datatype=base.datatype.htype,
            tiles=tiles,
            configurations=configurations,
        )

    # the first level of a pyramid over it, with four tiles where the data is
    first = level(
        dataset=base, origins=[(16384, 5120), (16384, 5632), (16896, 5120), (16896, 5632)]
    )
    # the tiles that land on what was written, at the depth of the level and below it
    tiles = [
        ((16384, 5120), (64, 64), (1, 1)),
        ((8192, 2560), (37, 53), (2, 2)),
        ((4096, 2560), (29, 31), (3, 2)),
    ]
    # go through the channels
    for kind, configurations in complexes.items():
        # read off the level
        compare(
            channel=channel(kind),
            source=served(source=first, depth=1),
            datatype=base.datatype.htype,
            tiles=tiles,
            configurations=configurations,
        )

    # open the covariance product, whose datasets hold reals
    reader = qed.readers.nisar.gcov(name="flow_nisar.gcov", uri=f"file:{gcov}")
    reader.open(measure=False)
    # its first dataset of reals
    (covariance,) = [d for d in reader.datasets if d.datatype.cell == "float32"][:1]
    # the tiles that land on the data, at full resolution and zoomed out, evenly and not
    tiles = [
        ((4410, 8944), (64, 64), (0, 0)),
        ((2205, 4472), (37, 53), (1, 1)),
        ((1102, 4472), (29, 31), (2, 1)),
    ]
    # the value channel
    compare(
        channel=channel("value"),
        source=served(source=covariance.data.dataset),
        datatype=covariance.datatype.htype,
        tiles=tiles,
        configurations=[ranged(0, 0.5), ranged(0.01, 0.2)],
    )

    # the channels that recolor the cells with no data, and the ones the mask flags; the masks of
    # GUNW products follow a different rule, which reads the codes of a GCOV mask just as well
    masked = {
        "covariance": [decades(-3, 0), decades(-2, -1)],
        "covarianceMasked": [decades(-3, 0), decades(-2, -1)],
        "coherence": [ranged(0, 0.5), ranged(0.01, 0.2)],
        "coherenceMasked": [ranged(0, 0.5), ranged(0.01, 0.2)],
        "unwrapped": [lit(0, 0.5, 0.5), lit(0.01, 0.2, 0.8)],
        "unwrappedMasked": [lit(0, 0.5, 0.5), lit(0.01, 0.2, 0.8)],
    }
    # the first dataset of the larger frequency, whose margins hold nans and masked cells
    (covariance,) = [d for d in reader.datasets if d.datatype.cell == "float32"][:1]
    # its mask
    mask = covariance.mask
    # the tiles that hold data, nans, and masked cells together, at full resolution and zoomed
    # out, evenly and not
    tiles = [
        ((12288, 3584), (64, 64), (0, 0)),
        ((7168, 5632), (37, 53), (1, 1)),
        ((1216, 1984), (64, 64), (3, 3)),
        ((1216, 3968), (29, 31), (3, 2)),
    ]
    # the fill the product declares, which none of its cells hold, and a nan, which tells the
    # nans in the margins apart as declared
    fills = [covariance.fill, float("nan")]
    # go through the channels
    for kind, configurations in masked.items():
        # and the fills
        for fill in fills:
            # read off the dataset and its mask
            compare(
                channel=channel(kind),
                source=served(
                    source=covariance.data.dataset,
                    companions={"mask": mask.data.dataset},
                    fill=fill,
                ),
                datatype=covariance.datatype.htype,
                tiles=tiles,
                configurations=configurations,
            )

    # the windows that read the first level of a pyramid over the dataset and its mask
    tiles = [
        ((7168, 5632), (37, 53), (1, 1)),
        ((1216, 1984), (64, 64), (3, 3)),
        ((1216, 3968), (29, 31), (3, 2)),
    ]
    # the tiles of the level they read
    origins = cover(tiles=tiles, depth=1, tile=tuple(covariance.tile))
    # build the level of the data
    data = level(dataset=covariance, origins=origins, name="covariance1")
    # and of the mask
    codes = level(dataset=mask, origins=origins, name="mask1")
    # go through the channels
    for kind, configurations in masked.items():
        # read off the levels
        compare(
            channel=channel(kind),
            source=served(source=data, depth=1, companions={"mask": codes}, fill=float("nan")),
            datatype=covariance.datatype.htype,
            tiles=tiles,
            configurations=configurations,
        )

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
