# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# framework
import qed


# base class for local products
class Product(
    qed.flow.product, implements=qed.protocols.products.specification, internal=True
):
    """
    The base class for {qed} products
    """


# end of file
