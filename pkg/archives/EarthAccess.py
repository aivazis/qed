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
        # get the package; if we get here we can assume it will import correctly because we now
        # check that archives has the runtime support they need
        import earthaccess

        # collect my filters
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

        # get the data
        for granule in earthaccess.search_data(**config):
            # get the name of the granule
            name = granule["meta"]["native-id"]
            # and its size
            size = granule.size()
            # form the file name
            filename = f"{name}.h5"
            # look up all the direct access links
            links = granule.data_links(access="direct")
            # go through them
            for link in links:
                # if this link ends with the granule filename
                if link.startswith("s3://") and link.endswith(filename):
                    # show me
                    channel.line(f"granule:")
                    channel.indent()
                    channel.line(f"name: {name}")
                    channel.line(f"size: {size}")
                    channel.line(f"link: {link}")
                    channel.outdent()
                    # convert it into a uri
                    uri = qed.primitives.uri(
                        scheme="s3", authority="daac@us-west-2", address=link[4:]
                    )
                    # make it available
                    yield name, str(uri), False
                    # and bail
                    break

        # outdent
        channel.outdent()
        # and flush
        channel.log()

        # all done
        return

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
