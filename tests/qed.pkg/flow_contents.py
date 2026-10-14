#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
A flat reader describes its file as its contents when a picker bound to it asks: the contents
start stale, a request for suggestions makes them, which opens the file, and the picker writes
the one dataset of a flat file, which has no axes, and refuses a selection that names one
"""

# externals
import struct

# support
import qed


# the driver
def test() -> None:
    """
    Bind a picker to a flat reader, pull its contents, and pick its dataset
    """
    # the shape of the file
    lines, samples = 4, 6
    # write it, as interleaved pairs of single precision floats
    with open("flow_contents.c8", "wb") as stream:
        # one cell at a time
        for cell in range(lines * samples):
            # real and imaginary parts
            stream.write(struct.pack("<ff", float(cell), 0.0))

    # a flat reader of it
    reader = qed.readers.native.flat(
        name="flow_contents.reader",
        uri="flow_contents.c8",
        cell="complex64",
        shape=(lines, samples),
    )
    # its contents have not been made
    assert reader.contents.pyre_stale
    # and its file has not been opened
    assert reader.datasets == []

    # a picker, bound to them
    picker = qed.viz.pickers.match()(name="flow_contents.picker")
    picker.contents = reader.contents
    # binding opens nothing
    assert reader.datasets == []

    # asking for the selections it can make
    suggestions = list(picker.pyre_suggest(trait=picker.pyre_trait(alias="selection")))
    # pulls the contents, which opens the file
    assert len(reader.datasets) == 1
    # a flat file has no axes, and one dataset
    assert reader.contents.axes == {}, reader.contents.axes
    assert len(reader.contents.entries) == 1
    # so there is one selection, which names no axis
    assert suggestions == [{}], suggestions

    # picking it
    picker.selection = {}
    picker.pyre_run()
    # writes the dataset of the reader
    (dataset,) = reader.datasets
    assert picker.dataset.source is dataset
    assert picker.dataset.selector == {}

    # a selection that names an axis the file does not have
    other = qed.viz.pickers.match()(name="flow_contents.other")
    other.contents = reader.contents
    other.selection = {"band": "1"}
    # matches nothing, and is refused
    try:
        other.pyre_run()
        assert False, "a selection with an axis a flat file does not have was accepted"
    except qed.flow.exceptions.ProductionError as error:
        assert "no dataset matches" in error.reason, error.reason

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
