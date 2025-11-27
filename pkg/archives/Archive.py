# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal


# a local data archive
class Archive(
    qed.component, family="qed.archives.base", implements=qed.protocols.archive
):
    """
    The base data archive
    """

    # user configurable state
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="file", address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"

    # constants
    readers = ()

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve my contents at {uri}, a location expected to belong within the archive document
        space
        """
        # i got nothing
        return []

    def credentials(self):
        """
        Generate the credentials necessary to access my contents
        """
        # nothing, by default
        return {}

    # implementation details
    # visitor support
    def identify(self, visitor, **kwds):
        """
        Let {visitor} know i'm a base archive
        """
        # attempt to
        try:
            # ask {visitor} for it's base handler
            handler = visitor.onArchive
        # if it doesn't understand
        except AttributeError:
            # get my class
            me = type(self)
            # and my poorly formed visitor's
            them = type(visitor)
            # complain that it is not a real visitor
            raise NotImplementedError(
                f"class '{them.__module__}.{them.__name__}' "
                f"is not a well formed visitor of '{me.__module__}.{me.__name__}"
            )
        # if all went well, invoke the hook
        return handler(archive=self, **kwds)

    # constants
    tag = "<base>"
    label = "<base>"


# end of file
