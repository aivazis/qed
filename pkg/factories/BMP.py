# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal

# superclass
from .Factory import Factory


# an image that can be shipped to the client
class BMP(
    Factory,
    family="qed.factories.renderers.bmp",
    implements=qed.protocols.factories.codec,
):
    """
    A microsoft v2 bitmap
    """

    # required: output
    bmp = qed.protocols.products.image.output()
    bmp.default = qed.products.bmp
    bmp.doc = "the image that will be sent to the client"

    # intrinsic: inputs
    red = qed.protocols.products.tile.input()
    red.doc = "the red channel input"

    green = qed.protocols.products.tile.input()
    green.doc = "the green channel input"

    blue = qed.protocols.products.tile.input()
    blue.doc = "the blue channel input"


# end of file
