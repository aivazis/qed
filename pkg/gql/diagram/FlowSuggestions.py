# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# support
import qed

# the rendering of values
from .FlowFactory import FlowFactory

# field types
from .FlowSuggestion import FlowSuggestion


# the values suggested for a setting of a factory
class FlowSuggestions(graphene.ObjectType):
    """
    The values suggested for a setting of a factory, and whether they are all it can take
    """

    # whether the suggestions are all the values the setting can take
    closed = graphene.Boolean(required=True)
    # the suggestions
    choices = graphene.List(graphene.NonNull(FlowSuggestion), required=True)

    # resolvers
    @staticmethod
    def resolve_closed(suggestions, info, **kwds):
        """
        Get whether the suggestions are all the values the setting can take
        """
        # unpack
        closed, _ = suggestions
        # and hand off
        return closed

    @staticmethod
    def resolve_choices(suggestions, info, **kwds):
        """
        Describe each suggestion by the text that sets it and how it reads
        """
        # unpack
        _, values = suggestions
        # describe each one
        return [FlowSuggestions.describe(value=value) for value in values]

    @staticmethod
    def describe(value):
        """
        Render a suggested {value}: a class by its family, which reads as its last part; a tuple
        by its parts, the way a configuration file lists them; a map by its entries, the way the
        diagram shows one; the rest the way a setting reads
        """
        # a class of components
        if isinstance(value, type) and issubclass(value, qed.component):
            # is set by its family and reads as the last part of it
            family = value.pyre_family()
            return FlowSuggestion(value=family, label=family.split(".")[-1])
        # a tuple
        if isinstance(value, tuple):
            # is set by its parts, and reads as them
            text = ", ".join(str(part) for part in value)
            return FlowSuggestion(value=text, label=text)
        # a map
        if isinstance(value, dict):
            # is set by its entries, and reads the way the diagram shows a map
            text = "{" + ", ".join(f"{key}: {item}" for key, item in value.items()) + "}"
            return FlowSuggestion(value=text, label=text)
        # the rest read the way a setting does
        text = FlowFactory.render(value=value)
        # and are set by the same text
        return FlowSuggestion(value=text, label=text)


# end of file
