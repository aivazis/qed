#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Read the image files of CEOS products in the layouts real producers use, and confirm that they
render, sample, and profile exactly like the same raster read from a flat file
"""

# externals
import struct

# support
import journal
import qed

# the layout of the synthetic raster
LINES, SAMPLES = 40, 64
# the formats of the cells: the struct code of a cell in big endian order, and the value of the
# cell at line {i} and sample {j}; every value is exact in its type
FORMATS = {
    "IU1": ("B", lambda i, j: (7 * i + j) % 256),
    "IU2": ("H", lambda i, j: 1000 + i * SAMPLES + j),
    "R*4": ("f", lambda i, j: float(i * SAMPLES + j) - 100.5),
    "C*8": ("ff", lambda i, j: (float(i), float(j) - 32)),
}
# the qed names of the cell types
CELLS = {"IU1": "uint8", "IU2": "uint16", "R*4": "float32", "C*8": "complex64"}


def image(
    uri,
    code,
    descriptor=720,
    prefix=180,
    counted=False,
    suffix=0,
    pixels=True,
    channels=1,
    interleave="BSQ",
    vary=False,
):
    """
    Write the image file of a CEOS product at {uri} with cells in the format {code}, after a file
    descriptor record of {descriptor} bytes; each record holds a {prefix} that {counted} says
    whether includes the record header, the samples, and a {suffix}; {pixels} says whether the
    descriptor reports the pixels of a line; {vary} makes the last record longer than the rest
    """
    # the struct code and the values of the cells
    fmt, value = FORMATS[code]
    # the bytes of a pixel
    group = struct.calcsize(">" + fmt)
    # the bytes of samples of a record
    data = SAMPLES * group
    # the length of a data record
    length = (0 if counted else 12) + prefix + data + suffix
    # the number of data records
    records = LINES * channels
    # the descriptor: its header, and the rest blank
    record = bytearray(struct.pack(">I4sI", 1, b"\x3f\xc0\x12\x12", descriptor))
    record += b" " * (descriptor - 12)

    # place a field right justified in the 1-based byte range {first} through {last}
    def put(first, last, text):
        # justify it
        field = str(text).rjust(last - first + 1).encode("ascii")
        # and place it
        record[first - 1 : last] = field

    # the layout fields
    put(181, 186, records)
    put(187, 192, length)
    put(225, 228, group)
    put(233, 236, channels)
    put(237, 244, LINES)
    put(245, 248, 0)
    put(257, 260, 0)
    put(269, 272, interleave)
    put(273, 274, 1)
    put(277, 280, prefix)
    put(281, 288, data)
    put(289, 292, suffix)
    put(429, 432, code)
    # the pixels of a line, unless the descriptor leaves them blank
    if pixels:
        put(249, 256, SAMPLES)
    # write the file
    with open(uri, "wb") as stream:
        # the descriptor
        stream.write(record)
        # the data records
        for sequence in range(records):
            # the channel and the line of this record
            if interleave == "BSQ":
                channel, line = divmod(sequence, LINES)
            else:
                line, channel = divmod(sequence, channels)
            # the samples, with each channel offset so the channels differ
            cells = b"".join(
                struct.pack(">" + fmt, *_parts(value(line + 3 * channel, j)))
                for j in range(SAMPLES)
            )
            # the last record of a file whose records vary is longer than the rest
            extra = 4 if vary and sequence == records - 1 else 0
            # the header
            stream.write(struct.pack(">I4sI", sequence + 2, b"\x32\x0a\x12\x14", length + extra))
            # the prefix past the header, the samples, and the suffix
            stream.write(b"\xab" * (prefix - (12 if counted else 0)))
            stream.write(cells)
            stream.write(b"\xcd" * (suffix + extra))
    # all done
    return


def flat(uri, code, channel=0):
    """
    Write the raster of {channel} as a flat file in the host's byte order, for reference
    """
    # the struct code and the values of the cells
    fmt, value = FORMATS[code]
    # write the cells
    with open(uri, "wb") as stream:
        for i in range(LINES):
            for j in range(SAMPLES):
                stream.write(struct.pack("=" + fmt, *_parts(value(i + 3 * channel, j))))
    # all done
    return


def _parts(value):
    """
    The parts of a cell {value} the struct module packs
    """
    # a pair is already in parts
    return value if isinstance(value, tuple) else (value,)


def compare(dataset, expected):
    """
    Confirm that {dataset} renders, samples, and profiles exactly like {expected}
    """
    # the layout agrees
    assert dataset.shape == expected.shape
    assert dataset.cell.cell == expected.cell.cell
    # tiles agree at a few zoom levels and origins, including footprints that stride, and in
    # every channel
    for zoom, origin, shape in [
        ((0, 0), (0, 0), (32, 32)),
        ((1, 1), (2, 3), (8, 8)),
        ((0, 1), (5, 0), (16, 16)),
        ((2, 0), (1, 7), (8, 8)),
    ]:
        for name in expected.channels:
            tile = bytes(
                memoryview(
                    expected.render(
                        channel=expected.channel(name=name), zoom=zoom, origin=origin, shape=shape
                    )
                )
            )
            actual = bytes(
                memoryview(
                    dataset.render(
                        channel=dataset.channel(name=name), zoom=zoom, origin=origin, shape=shape
                    )
                )
            )
            assert actual == tile, (name, zoom, origin, shape)
        # and so do the samples of the footprint
        assert dataset.sample(zoom=zoom, origin=origin, shape=shape) == expected.sample(
            zoom=zoom, origin=origin, shape=shape
        )
    # the statistics gathered at first contact agree
    assert dataset.stats == expected.stats
    # profiles agree along paths in every direction, open and closed
    for points in [[(1, 2), (10, 20), (30, 60)], [(30, 60), (10, 20), (1, 2)], [(5, 5)]]:
        for closed in (False, True):
            assert list(dataset.profile(points=points, closed=closed)) == list(
                expected.profile(points=points, closed=closed)
            )
    # all done
    return


def reference(name, code, channel=0):
    """
    Open the flat reference for {code} and {channel}
    """
    # write it
    uri = f"ceos_{name}_reference.dat"
    flat(uri=uri, code=code, channel=channel)
    # read it
    reader = qed.readers.native.flat(
        name=f"ceos.{name}.reference", uri=uri, shape=(LINES, SAMPLES), cell=CELLS[code]
    )
    reader.open()
    # hand off its dataset
    (dataset,) = reader.datasets
    return dataset


def contact(name, uri):
    """
    Build a CEOS reader over {uri} and make first contact
    """
    # build the reader
    reader = qed.readers.native.ceos(name=name, uri=uri)
    # open it
    reader.open()
    # and hand it off
    return reader


def test():
    """
    The CEOS reader finds the raster of an image file in every layout the producers use
    """
    # the layouts: the prefix counted with the record header and without it, descriptors of
    # different lengths, a descriptor that leaves the pixels of a line blank, and a suffix
    layouts = [
        # like ALOS: a prefix of 412 bytes that counts the header, complex floats
        ("alos", "C*8", dict(prefix=412, counted=True)),
        # like RADARSAT-1 SGF: a descriptor of 16252 bytes, a prefix of 180 that does not count the
        # header, unsigned shorts
        ("sgf", "IU2", dict(descriptor=16252, prefix=180, counted=False)),
        # like the RADARSAT-1 products from ASF: a prefix of 192 that counts the header, bytes, and
        # the pixels of a line left blank
        ("asf", "IU1", dict(prefix=192, counted=True, pixels=False)),
        # real floats with a suffix after the samples
        ("real", "R*4", dict(prefix=100, counted=False, suffix=28)),
    ]
    # go through them
    for name, code, options in layouts:
        # write the image file
        uri = f"ceos_{name}.dat"
        image(uri=uri, code=code, **options)
        # read it
        reader = contact(name=f"ceos.{name}", uri=uri)
        # one dataset
        (dataset,) = reader.datasets
        # that reads exactly like the flat reference
        compare(dataset=dataset, expected=reference(name=name, code=code))

    # files with two channels, in either interleave
    for interleave in ("BSQ", "BIL"):
        # write the image file
        uri = f"ceos_{interleave.lower()}.dat"
        image(uri=uri, code="IU2", prefix=192, counted=True, channels=2, interleave=interleave)
        # read it
        reader = contact(name=f"ceos.{interleave.lower()}", uri=uri)
        # one dataset per channel
        assert len(reader.datasets) == 2
        # selectable by ordinal
        assert reader.selectors == {"band": ("1", "2")}
        # each reading exactly like its channel written out on its own
        for channel, dataset in enumerate(reader.datasets):
            # it knows its channel
            assert dataset.selector == {"band": str(channel + 1)}
            # and reads like the reference
            compare(
                dataset=dataset,
                expected=reference(
                    name=f"{interleave.lower()}{channel}", code="IU2", channel=channel
                ),
            )

    # the refusals: send the complaints to the trash, since they are expected
    journal.error("qed.readers.native.ceos").device = journal.trash()
    # a file whose records vary in length
    image(uri="ceos_vary.dat", code="IU2", vary=True)
    # a file with a format that is not supported
    image(uri="ceos_cint.dat", code="IU2")
    with open("ceos_cint.dat", "r+b") as stream:
        stream.seek(428)
        stream.write(b"CI*4")
    # a file that is not a CEOS image file
    flat(uri="ceos_flat.dat", code="IU2")
    # go through them
    for name in ("vary", "cint", "flat"):
        # carefully
        try:
            # open it
            contact(name=f"ceos.{name}", uri=f"ceos_{name}.dat")
        # the refusal
        except journal.ApplicationError:
            # is the expected outcome
            pass
        # anything else
        else:
            # is a failure
            assert False, f"'ceos_{name}.dat' was accepted"

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
