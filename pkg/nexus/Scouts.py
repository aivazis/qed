# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import pyre

# superclass
from .Team import Team


# the archive listing team
class Scouts(Team, family="qed.nexus.teams.archive"):
    """
    A standing team of persistent worker processes that list the folders of a data archive

    One member is enough: a listing is sequential work, and the member that mounted the
    archive keeps it mounted, so the folders of a query backed archive are answered from the
    page it already holds
    """

    # user configurable state
    size = pyre.properties.int(default=1)
    size.doc = "the number of crew members to recruit"


# end of file
