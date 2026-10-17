#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the selections a survey hands a passive reader are not saved: hydration puts them
in the reader, and a recipe of the reader leaves them out
"""

# externals
import os

# support
import pyre
import qed

# the raster in this directory
raster = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c16.dat")


def test():
    """
    Hydrate a passive reader from a survey record, and describe it the way the session does
    when it saves the workspace
    """
    # a passive reader that has never touched its product
    reader = qed.readers.native.flat(name="survey_picks", uri=raster, shape=(65, 65), cell="c16")
    # a survey that auto-picked a band
    record = qed.nexus.discovery(
        selections={"band": "L"}, available={"band": ("L",)}, shape=None, findings=[]
    )
    # hydrate
    record.hydrate(reader=reader)
    # the reader holds the pick
    assert dict(reader.selections) == {"band": "L"}, dict(reader.selections)
    # describe it
    recipe = pyre.config.newRecipe().add(reader)
    # get its section
    section = recipe.section("survey_picks")
    # it says where the product is
    assert "uri" in section, section
    # but nothing about the pick
    assert "selections" not in section, section
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
