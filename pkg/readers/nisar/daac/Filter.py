# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import re


# a filter generator
class Filter:
    """
    A generator of regular expressions that match granule ids given partial information
    """

    # interface
    def select(self, **tokens):
        """
        Build a regular expression that matches granule ids that have the specified token values
        """
        # generate a sequence of fragments, either fixed values from the given {tokens} or regular
        # expressions from the {lexer} of each unspecified token
        fragments = self.resolve(tokens=tokens)
        # assemble the scanner
        scanner = "".join(fragments)
        # compile  it
        regex = re.compile(scanner)
        # and attach it
        self.regex = regex
        # return the scanner, just in case the caller wants to inspect what was done
        return scanner

    def match(self, granule):
        """
        Check whether {granule} matches my filter
        """
        # do the simple thing for now
        return self.regex.match(granule)

    # metamethods
    def __init__(self, product: str, **kwds):
        # chain up
        super().__init__(**kwds)
        # resolve the product name into the matching descriptor class
        self.descriptor = getattr(qed.readers.nisar.daac, product.lower())
        # prime my regex
        self.regex = None
        # all done
        return

    # implementation details
    def resolve(self, tokens):
        """
        Go through the {descriptor} fields in {sequencer} order and use values from the {tokens}
        supplied by the caller when available, or the {lexer} from the token
        """
        # get the descriptor
        descriptor = self.descriptor
        # get the tokens in {sequencer} order
        for name in descriptor.sequencer():
            # get the matching token
            token = descriptor.pyre_trait(alias=name)
            # get the value from the caller table
            value = tokens.get(name)
            # if the value is trivial, hand off the token {lexer}
            # otherwise, format it and send it off
            yield token.lexer if value is None else token.str(value=value)
        # all done
        return


# end of file
