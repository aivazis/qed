# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# framework
import qed


# protocol for the places qed keeps what it derives
class Workspace(qed.protocol, family="qed.workspaces"):
    """
    The protocol for the place {qed} works out of

    Data products are read-only, and often not even local, so anything qed computes and
    means to keep has to live somewhere else. A workspace is that somewhere: it answers
    where a given kind of derived data belongs, and it is the one place to look when the
    question is where all of this is being written
    """

    # user configurable state
    path = qed.properties.path()
    path.default = "."
    path.doc = "the directory that holds whatever qed derives from its data products"

    # interface
    @qed.provides
    def cache(self, name):
        """
        Retrieve the directory that holds derived data of the given {name}, making it if
        this is the first time anyone has asked
        """

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # work out of a local directory
        return qed.workspaces.local


# end of file
