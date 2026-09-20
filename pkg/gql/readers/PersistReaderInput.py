# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for saving a data reader
class PersistReaderInput(graphene.InputObjectType):
    """
    The payload to save a data reader
    """

    # the name of the reader to save
    name = graphene.String(required=True)


# end of file
