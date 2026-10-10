#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that hydrating a reader merges the selections a survey reports into the ones the reader
holds: the survey fills the axes the reader has no opinion on, and the reader's own win
"""

# externals
import types

# support
import qed


# the driver
def test():
    """
    Hydrate a passive reader stand-in from a survey record and check its selections
    """
    # a passive reader stand-in that has never touched its product, with the selections its
    # configuration gave it
    reader = types.SimpleNamespace(
        pyre_name="hydrate_selections",
        uri="file:hydrate_selections.h5",
        datasets=[],
        selections={"frequency": "A", "polarization": "HH"},
        _opened=False,
    )
    # a survey that auto-picked the single-valued band and disagrees about the polarization
    record = qed.nexus.discovery(
        selections={"band": "L", "polarization": "HV"},
        available={"band": ("L",), "frequency": ("A", "B"), "polarization": ("HH", "HV")},
        shape=None,
        findings=[],
    )
    # hydrate
    record.hydrate(reader=reader)
    # the band comes from the survey, and the rest is what the reader held
    assert reader.selections == {"band": "L", "frequency": "A", "polarization": "HH"}
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
