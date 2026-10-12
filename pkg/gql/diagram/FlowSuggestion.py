# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a value suggested for a setting of a factory
class FlowSuggestion(graphene.ObjectType):
    """
    A value suggested for a setting: the text that sets it, and how it reads
    """

    # the text that sets the value, the way a configuration file would
    value = graphene.String(required=True)
    # how it reads
    label = graphene.String(required=True)


# end of file
