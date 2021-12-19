# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# support
import qed


# custom properties
def selectors(default={}, **kwds):
    """
    A map from selector names to their legal values
    """
    # build the trait descriptor and return it
    return qed.properties.dict(
        schema=qed.properties.tuple(schema=qed.properties.str(), default=()),
        default=default, **kwds)


# end of file
