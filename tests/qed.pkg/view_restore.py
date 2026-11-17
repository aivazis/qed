#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a view keeps the selections it was configured with while its reader has not made
first contact, the way a saved session restores them at boot, and judges them only once the
reader knows what is available
"""

# externals
import struct

# support
import pyre
import qed

# the layout of the synthetic product
LINES, SAMPLES, BANDS = 8, 16, 2


def synthesize():
    """
    Write a product with two bands, and its ENVI header
    """
    # the number of cells
    cells = LINES * SAMPLES * BANDS
    # the product
    with open("view_restore.dat", "wb") as product:
        # every cell holds its own offset
        product.write(struct.pack(f"<{cells}f", *map(float, range(cells))))
    # its header, with the bands known by their ordinals
    header = pyre.envi.header(
        samples=SAMPLES, lines=LINES, bands=BANDS, dataType=4, interleave="bsq", byteOrder=0
    )
    # written next to it
    pyre.envi.writer().write(header=header, uri="view_restore.hdr")
    # all done
    return


def test():
    """
    Restore views over a reader that has not made first contact, then make contact
    """
    # make the product
    synthesize()
    # a reader over it, which touches nothing until it is opened
    reader = qed.readers.native.envi(name="view_restore", uri="view_restore.dat")
    # a view restored with a band the product has
    kept = qed.ux.view(name="view_restore.kept", reader=reader, selections={"band": "2"})
    # and one restored with a band it does not
    stale = qed.ux.view(name="view_restore.stale", reader=reader, selections={"band": "7"})
    # before first contact, both keep what they were given
    assert dict(kept.selections) == {"band": "2"}, dict(kept.selections)
    assert dict(stale.selections) == {"band": "7"}, dict(stale.selections)
    # and neither has a dataset yet
    assert kept.dataset is None
    assert stale.dataset is None

    # make first contact
    reader.open()
    # and let the views catch up
    kept.refresh()
    stale.refresh()
    # the band the product has survives
    assert dict(kept.selections) == {"band": "2"}, dict(kept.selections)
    # and picks its dataset
    assert kept.dataset is not None and dict(kept.dataset.selector) == {"band": "2"}
    # the band it does not have is dropped, so the user can pick again
    assert dict(stale.selections) == {}, dict(stale.selections)
    # and there is no dataset to show
    assert stale.dataset is None
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
