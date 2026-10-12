# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a method of a factory that the diagram can invoke
class FlowMethod(graphene.ObjectType):
    """
    A method of a factory that can be invoked with no arguments
    """

    # the fields
    # the name of the method
    name = graphene.String(required=True)
    # the first line of its documentation
    doc = graphene.String()
    # whether it can be invoked now: only an instance has methods to invoke
    invocable = graphene.Boolean(required=True)


# end of file
