# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import pyre

# my superclass
from .Team import Team


# the team that builds what a reader needs before it is worth looking at
class Builders(Team, family="qed.nexus.teams.build"):
    """
    A team of worker processes that makes first contact with a data source and builds the
    pyramids of its datasets

    The work streams: every page of the product is fetched once and every chunk is decoded
    once, so my members need a page buffer only as large as the pages of the task in hand, and
    no chunk cache beyond the library's own. The team is large while there is work, and is
    released when there is none, so it does not compete with the team that serves tiles
    """

    # user configurable state
    size = pyre.properties.int(default=16)
    size.doc = "the number of crew members to recruit"

    pages = pyre.properties.int(default=16 * 1024)
    pages.doc = (
        "the page buffer my members open a product with, in pages of 4 KiB; enough for the "
        "pages of the task in hand"
    )

    chunks = pyre.properties.int(default=None)
    chunks.doc = (
        "the chunk cache of each dataset my members open, in MiB; unset keeps the setting of "
        "the reader, since a stream decodes every chunk once"
    )

    # the kind of work i do
    kind = "build"


# end of file
