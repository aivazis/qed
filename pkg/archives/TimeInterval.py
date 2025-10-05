# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal


# a point on the surface of a sphere
class TimeInterval(
    qed.component,
    family="qed.archives.filters.when",
    implements=qed.protocols.archiveFilter,
):
    """
    A filter for earthdata searches that identifies datasets from a given time interval
    """

    # user-configurable state
    begin = qed.properties.str()
    begin.doc = "the longitude of the point"

    end = qed.properties.str()
    end.doc = "the latitude of the point"

    # interface
    @qed.export
    def filter(self):
        """
        Apply the filter to a search
        """
        # all done
        return

    # framework hooks
    def pyre_configured(self, **kwds):
        # chain up
        yield from super().pyre_configured(**kwds)
        # show me
        channel = journal.info("qed.archives.time")
        channel.line(f"{self}")
        channel.indent()
        channel.line(f"begin: {self.begin}")
        channel.line(f"  end: {self.end}")
        channel.outdent()
        # all done
        return


# end of file
