#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a reader that was never told where its file is refuses to make its contents, and
says so, rather than failing while it parses an empty uri
"""

# support
import qed


def test() -> None:
    """
    Make the contents of a reader of each kind with no uri
    """
    # a reader of each kind, some of them handed out by foundries
    kinds = (
        qed.readers.native.flat,
        qed.readers.native.gdal,
        qed.readers.nisar.gcov,
        qed.readers.isce2.unw,
        qed.readers.isce2.int,
    )
    # go through them
    for kind in kinds:
        # get the class
        cls = kind() if isinstance(kind, qed.foundry) else kind
        # make an instance that is told nothing
        reader = cls(name=f"tests.{cls.pyre_family()}.nouri")
        # ask it for its contents
        try:
            # by making its products
            reader.pyre_make()
            # which should be unreachable
            assert False, cls.pyre_family()
        # if it refuses, as expected
        except qed.flow.exceptions.ProductionError as error:
            # it names its contents as the product it cannot make
            assert error.product == "contents", (cls.pyre_family(), error.product)
            # and says why
            assert error.reason == "the uri of the file to read is not set", error.reason

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
