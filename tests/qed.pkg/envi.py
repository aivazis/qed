#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Read flat products through their ENVI headers, in either byte order, and confirm that they
render, sample, and profile exactly like the same data read natively
"""

# externals
import struct
import sys

# support
import journal
import pyre
import qed

# the layout of the synthetic product
LINES, SAMPLES = 40, 64
# every cell holds its own offset, which single precision represents exactly at this size
VALUES = [float(i * SAMPLES + j) for i in range(LINES) for j in range(SAMPLES)]


def synthesize():
    """
    Write the product in each byte order, with its ENVI header placed the two ways writers do
    """
    # the number of cells
    cells = LINES * SAMPLES
    # the little endian product, with its header next to it under the same stem
    with open("envi_le.dat", "wb") as product:
        product.write(struct.pack(f"<{cells}f", *VALUES))
    pyre.envi.writer().write(header=describe(order=0), uri="envi_le.hdr")
    # the big endian product, with its header named after the full product name
    with open("envi_be.dat", "wb") as product:
        product.write(struct.pack(f">{cells}f", *VALUES))
    pyre.envi.writer().write(header=describe(order=1), uri="envi_be.dat.hdr")
    # all done
    return


def describe(order, **extras):
    """
    Build the header of the synthetic product in the given byte {order}, with {extras} overriding
    its fields
    """
    # the fields
    fields = dict(
        samples=SAMPLES, lines=LINES, bands=1, dataType=4, interleave="bsq", byteOrder=order
    )
    # apply the overrides
    fields.update(extras)
    # and build the header
    return pyre.envi.header(**fields)


def contact(name, uri, **kwds):
    """
    Build an ENVI reader over {uri} and make first contact
    """
    # build the reader
    reader = qed.readers.native.envi(name=name, uri=uri, **kwds)
    # open it
    reader.open()
    # and hand it off
    return reader


def test():
    """
    The ENVI reader recovers the layout of a product from its header and reads the product in
    place whatever its byte order
    """
    # make the products
    synthesize()

    # the host's order
    host = sys.byteorder
    # readers over the two products
    le = contact(name="envi.le", uri="envi_le.dat")
    be = contact(name="envi.be", uri="envi_be.dat")
    # and the reference: the flat reader over the product that is in the host's order
    reference = qed.readers.native.flat(
        name="envi.reference",
        uri="envi_le.dat" if host == "little" else "envi_be.dat",
        shape=(LINES, SAMPLES),
        cell="float32",
    )
    reference.open()
    # its dataset
    (expected,) = reference.datasets

    # both readers recovered the layout from their headers
    for reader in (le, be):
        # exactly one dataset
        (dataset,) = reader.datasets
        # of the declared shape and type
        assert dataset.shape == (LINES, SAMPLES)
        assert dataset.cell.cell == "float32"
    # the datasets
    (little,) = le.datasets
    (big,) = be.datasets
    # the swap flag follows the product, not the host
    assert little.cell.byteswap == (host != "little")
    assert big.cell.byteswap == (host != "big")
    # and the buffer description carries the order of the product
    assert memoryview(little.data).format == ("f" if host == "little" else "<f")
    assert memoryview(big.data).format == ("f" if host == "big" else ">f")

    # cells read as native values through the grid, whatever the order on disk
    for dataset in (little, big):
        assert dataset.data[3, 5] == VALUES[3 * SAMPLES + 5]
        assert dataset.data[LINES - 1, SAMPLES - 1] == VALUES[-1]

    # tiles rendered from either product are identical to the reference, at a few zoom levels
    # and origins, including footprints that stride through the product
    geometries = [
        ((0, 0), (0, 0), (32, 32)),
        ((1, 1), (2, 3), (8, 8)),
        ((0, 1), (5, 0), (16, 16)),
    ]
    # go through them
    for zoom, origin, shape in geometries:
        # render the reference
        pipeline = expected.channel(name="value")
        tile = bytes(
            memoryview(expected.render(channel=pipeline, zoom=zoom, origin=origin, shape=shape))
        )
        # and each product
        for dataset in (little, big):
            # the same way
            pipeline = dataset.channel(name="value")
            actual = bytes(
                memoryview(dataset.render(channel=pipeline, zoom=zoom, origin=origin, shape=shape))
            )
            # the bytes must agree
            assert actual == tile

    # the statistics gathered at first contact agree
    for dataset in (little, big):
        assert dataset.stats == expected.stats
    # so do samples of a strided footprint
    for dataset in (little, big):
        assert dataset.sample(zoom=(1, 0), origin=(3, 4), shape=(10, 10)) == expected.sample(
            zoom=(1, 0), origin=(3, 4), shape=(10, 10)
        )
    # and profiles along a path
    points = [(1, 2), (10, 20), (30, 60)]
    for dataset in (little, big):
        assert dataset.profile(points=points) == expected.profile(points=points)

    # the refusals: send the complaints to the trash, since they are expected
    journal.error("qed.readers.native.envi").device = journal.trash()
    # a product without a header
    try:
        # pointing the reader at a header that is not there
        contact(name="envi.missing", uri="envi_le.dat", header="envi_missing.hdr")
    # is a fatal error
    except journal.ApplicationError:
        # as expected
        pass
    # anything else
    else:
        # is a failure
        assert False, "a product without a header was accepted"
    # products with an embedded header read exactly like the ones without
    offsets(expected=expected)
    # multi-band products come apart into one dataset per band
    bands()
    # even past an embedded header that leaves their cells misaligned
    bands(offset=5)

    # all done
    return


def offsets(expected):
    """
    A product whose cells sit past an embedded header reads exactly like the {expected} one
    without it, in either byte order, whether the header leaves the cells aligned or not
    """
    # the number of cells
    cells = LINES * SAMPLES
    # the datasets to check
    datasets = []
    # a header that leaves the cells aligned, and two that do not
    for offset in (128, 3, 6):
        # in either byte order
        for order, code in ((0, "<"), (1, ">")):
            # the stem of the product
            stem = f"envi_offset_{offset}_{order}"
            # write the embedded header, which is junk as far as the cells are concerned, and
            # the cells after it
            with open(f"{stem}.dat", "wb") as product:
                product.write(b"\xab" * offset)
                product.write(struct.pack(f"{code}{cells}f", *VALUES))
            # and the ENVI header that says how long the embedded one is
            pyre.envi.writer().write(
                header=describe(order=order, headerOffset=offset), uri=f"{stem}.hdr"
            )
            # open it
            reader = contact(name=f"envi.offset.{offset}.{order}", uri=f"{stem}.dat")
            # the reader adopted the offset from the header
            assert reader.offset == offset
            # exactly one dataset
            (dataset,) = reader.datasets
            # that starts past the embedded header
            assert dataset.offset == offset
            # of the declared shape
            assert dataset.shape == (LINES, SAMPLES)
            # add it to the pile
            datasets.append(dataset)
    # the flat reader, told where the cells start, over a product that leaves them misaligned
    flat = qed.readers.native.flat(
        name="envi.offset.flat",
        uri=f"envi_offset_3_{0 if sys.byteorder == 'little' else 1}.dat",
        shape=(LINES, SAMPLES),
        cell="float32",
        offset=3,
    )
    flat.open()
    # add its dataset to the pile
    datasets.extend(flat.datasets)

    # go through them
    for dataset in datasets:
        # cells read as their values
        assert dataset.data[3, 5] == VALUES[3 * SAMPLES + 5]
        assert dataset.data[LINES - 1, SAMPLES - 1] == VALUES[-1]
        # tiles render exactly like the reference, including footprints that stride
        for zoom, origin, shape in [((0, 0), (0, 0), (32, 32)), ((1, 1), (2, 3), (8, 8))]:
            # the reference tile
            tile = bytes(
                memoryview(
                    expected.render(
                        channel=expected.channel(name="value"),
                        zoom=zoom,
                        origin=origin,
                        shape=shape,
                    )
                )
            )
            # and this one
            actual = bytes(
                memoryview(
                    dataset.render(
                        channel=dataset.channel(name="value"),
                        zoom=zoom,
                        origin=origin,
                        shape=shape,
                    )
                )
            )
            # must agree
            assert actual == tile
        # so do the statistics, samples, and profiles
        assert dataset.stats == expected.stats
        assert dataset.sample(zoom=(1, 0), origin=(3, 4), shape=(10, 10)) == expected.sample(
            zoom=(1, 0), origin=(3, 4), shape=(10, 10)
        )
        points = [(1, 2), (10, 20), (30, 60)]
        assert dataset.profile(points=points) == expected.profile(points=points)

    # an offset that leaves the file too short for the declared shape is refused
    pyre.envi.writer().write(header=describe(order=0, headerOffset=64), uri="envi_offset_short.hdr")
    # by writing the cells without the embedded header in front of them
    with open("envi_offset_short.dat", "wb") as product:
        product.write(struct.pack(f"<{cells}f", *VALUES))
    # the complaint is expected, so send it to the trash
    journal.warning("qed.readers.native.flat").device = journal.trash()
    # the reader
    short = contact(name="envi.offset.short", uri="envi_offset_short.dat")
    # builds no datasets
    assert not short.datasets

    # all done
    return


def bands(offset=0):
    """
    A multi-band product yields one dataset per band, selectable by name, in every interleave and
    in either byte order, each reading exactly like the band written out on its own; the cells
    sit past an embedded header of {offset} bytes
    """
    # the host's order
    host = sys.byteorder
    # the bands
    names = ["red", "green", "blue"]
    # every cell holds a value that names its band and its position
    cube = [
        [float(1000 * b + i * SAMPLES + j) for i in range(LINES) for j in range(SAMPLES)]
        for b in range(len(names))
    ]
    # the reference: each band on its own, in the host's order, through the flat reader
    references = []
    for b, plane in enumerate(cube):
        with open(f"envi_band{b}_{offset}.dat", "wb") as product:
            product.write(struct.pack(f"={LINES * SAMPLES}f", *plane))
        reader = qed.readers.native.flat(
            name=f"envi.band{b}.{offset}",
            uri=f"envi_band{b}_{offset}.dat",
            shape=(LINES, SAMPLES),
            cell="float32",
        )
        reader.open()
        (dataset,) = reader.datasets
        references.append(dataset)

    # the interleaves, each with a byte order; the pixel interleaved product is in the order
    # the host lacks, so the swap is exercised on a strided plane as well
    layouts = [("bsq", 0 if host == "little" else 1), ("bil", 0 if host == "little" else 1)]
    layouts.append(("bip", 1 if host == "little" else 0))
    # go through them
    for interleave, order in layouts:
        # the struct code of the order
        code = "<" if order == 0 else ">"
        # arrange the cells the way the interleave does
        cells = []
        if interleave == "bsq":
            for b in range(3):
                cells.extend(cube[b])
        elif interleave == "bil":
            for i in range(LINES):
                for b in range(3):
                    cells.extend(cube[b][i * SAMPLES : (i + 1) * SAMPLES])
        else:
            for i in range(LINES):
                for j in range(SAMPLES):
                    for b in range(3):
                        cells.append(cube[b][i * SAMPLES + j])
        # the stem of the product
        stem = f"envi_{interleave}_{offset}"
        # write the product, past its embedded header
        with open(f"{stem}.dat", "wb") as product:
            product.write(b"\xab" * offset)
            product.write(struct.pack(f"{code}{len(cells)}f", *cells))
        # and its header
        pyre.envi.writer().write(
            header=describe(
                order=order,
                bands=3,
                interleave=interleave,
                bandNames=names,
                headerOffset=offset,
            ),
            uri=f"{stem}.hdr",
        )
        # open it
        reader = contact(name=f"envi.{interleave}.{offset}", uri=f"{stem}.dat")
        # one dataset per band, named by ordinal
        assert [dataset.pyre_name for dataset in reader.datasets] == [
            f"envi.{interleave}.{offset}.{b + 1}" for b in range(3)
        ]
        # the selector names the bands
        assert reader.selectors == {"band": tuple(names)}
        assert reader.available == {"band": set(names)}
        # each dataset knows its band and its plane
        for b, dataset in enumerate(reader.datasets):
            assert dataset.selector == {"band": names[b]}
            assert dataset.shape == (LINES, SAMPLES)
            assert dataset.cell.cell == "float32"
            # its cells read as the band's values
            assert dataset.data[3, 5] == cube[b][3 * SAMPLES + 5]
            assert dataset.data[LINES - 1, SAMPLES - 1] == cube[b][-1]
            # and it renders, samples, and profiles exactly like the band on its own
            expected = references[b]
            for zoom, origin, shape in [((0, 0), (0, 0), (32, 32)), ((1, 1), (2, 3), (8, 8))]:
                tile = bytes(
                    memoryview(
                        expected.render(
                            channel=expected.channel(name="value"),
                            zoom=zoom,
                            origin=origin,
                            shape=shape,
                        )
                    )
                )
                actual = bytes(
                    memoryview(
                        dataset.render(
                            channel=dataset.channel(name="value"),
                            zoom=zoom,
                            origin=origin,
                            shape=shape,
                        )
                    )
                )
                assert actual == tile
            assert dataset.stats == expected.stats
            assert dataset.sample(zoom=(1, 0), origin=(3, 4), shape=(10, 10)) == expected.sample(
                zoom=(1, 0), origin=(3, 4), shape=(10, 10)
            )
            points = [(1, 2), (10, 20), (30, 60)]
            assert dataset.profile(points=points) == expected.profile(points=points)

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
