# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import re

# support
import qed


# the generic proposal for the name of a reader
def nickname(uri: str, **kwds) -> str:
    """
    Propose a name for the reader of the product at {uri}, made from its file name
    """
    # find the file the {uri} points to
    address = qed.primitives.uri.parse(uri).address
    # its name without the extension is what the user would type
    stem = qed.primitives.path(address).stem
    # make it a single level of a pyre name
    name = sanitize(name=stem)
    # a file with nothing but an extension still needs a name
    return name or "reader"


# turn arbitrary text into a single level of a pyre name
def sanitize(name: str) -> str:
    """
    Replace the characters of {name} that do not belong in a pyre name with underscores
    """
    # dots separate the levels of a pyre name, and the rest of the punctuation is not welcome
    # either, so anything other than a word character or a dash becomes an underscore
    return re.sub(r"[^\w-]", "_", name)


# end of file
