#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Stage the recipe the playground draws against the catalog of the pyre extension, realize it for a
tile shape, and pull an image out of it
"""

# externals
import cmath
import types

# support
import qed


# the driver
def test():
    """
    Stage the amplitude recipe of the playground, starting from complex samples, and render a tile
    """
    # the recipe, as the store makes it for its playground
    recipe = qed.ux.store.amplitude(types.SimpleNamespace())
    # the catalog
    catalog = qed.libpyre.flow.catalog()
    # the tiles of complex samples
    complex64 = qed.flow.recipes.plan.tile(catalog=catalog, cell="complex64")
    # stage the recipe, starting from them
    plan = recipe.stage(catalog=catalog, products={"signal": complex64})
    # the shape of the tile
    lines, samples = 4, 6
    # realize the plan for it
    with plan.realize(shape=(lines, samples)) as graph:
        # get the cells of the signal
        cells = graph["signal"].write()
        # fill them
        for i in range(lines):
            # one sample at a time
            for j in range(samples):
                # with magnitudes in the interval of the normalizer
                cells[i, j] = cmath.rect((i * samples + j) / (lines * samples), 0.5 * j)
        # pull the image
        image = graph["image"].read()
    # it is a bitmap
    assert image[:2] == b"BM"
    # that records its own size
    assert int.from_bytes(image[2:6], "little") == len(image)
    # and has the shape of the tile
    assert int.from_bytes(image[18:22], "little", signed=True) == samples
    assert abs(int.from_bytes(image[22:26], "little", signed=True)) == lines
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
