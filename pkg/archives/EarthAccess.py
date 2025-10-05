# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal

# superclass
from .Archive import Archive


# an earth access data archive
class EarthAccess(Archive, family="qed.archives.earth"):
    """
    A data archive that consists of datasets available through earth access
    """

    # user configurable state
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="earth", address=())
    uri.doc = "the archive identifier"

    filters = qed.properties.list(schema=qed.protocols.archiveFilter())
    filters.doc = "the collection of search filters to apply when looking for datasets"

    # constants
    readers = ("nisar",)

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve the archive contents at {uri}, a location expected to belong within the archive
        document space
        """
        # collect the my filters
        config = dict(
            (name, value)
            for filter in self.filters
            for name, value in self.identify(visitor=filter)
        )

        # show me
        channel = journal.info("qed.archives.earth.contents")
        channel.line(f"{self}")
        channel.indent()
        channel.line(f"config: {config}")
        channel.outdent()
        channel.log()

        # no contents, until we can get real data from vertex
        return []

    # visitor support
    def identify(self, visitor, **kwds):
        """
        Let {visitor} know i'm an earth access archive
        """
        # attempt to
        try:
            # ask {visitor} for it's base handler
            handler = visitor.onEarthAccess
        # if it doesn't understand
        except AttributeError:
            # chain up
            return super().identify(visitor=visitor, **kwds)
        # if all went well, invoke the hook
        return handler(archive=self, **kwds)

    # hooks
    @classmethod
    def isSupported(cls):
        """
        Check whether there is runtime support for this archive type
        """
        # attempt to
        try:
            # access the external packages we need
            import earthaccess
        # if anything goes wrong
        except ImportError as error:
            # no dice
            return False
        # otherwise, chances are good there is runtime support
        return True

    # constants
    tag = "earth"
    label = "earth-access"


# end of file
