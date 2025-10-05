# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal

# superclass
from .Archive import Archive


# a S3 data archive
class S3(Archive, family="qed.archives.s3"):
    """
    A data archive that resides in an S3 bucket
    """

    # the location
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="file", address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"

    # constants
    readers = ("nisar",)

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve the archive contents at {uri}, a location expected to belong within the archive
        document space
        """
        # get my root
        root = self.fs
        # lookup its location
        location = root.location()
        # get the target address
        path = qed.primitives.path(uri.address)
        # project it onto my prefix
        rel = path.relativeTo(location.address)

        # attempt to
        try:
            # get the folder
            folder = root[rel]
        # if it doesn't exist
        except root.NotFoundError as error:
            # make a channel
            channel = journal.error("qed.archives.s3")
            # complain
            channel.line(f"could not find '{uri}'")
            channel.line(f"while exploring '{location}'")
            channel.line(f"error: {error}")
            # flush
            channel.log()
            # and bail
            return []
        # get its contents
        contents = tuple(sorted(folder.contents.items()))

        # make a pile of files
        files = [
            (name, location.clone(address=location.address / node.uri), node.isFolder)
            for name, node in contents
            if not node.isFolder
        ]
        # and a pile of directories
        folders = [
            (name, location.clone(address=location.address / node.uri), node.isFolder)
            for name, node in contents
            if node.isFolder
        ]
        # present them in this order
        return folders + files

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # mount my s3 filesystem
        self.fs = qed.filesystem.s3(root=self.uri).discover()

        # make an explorer
        explorer = qed.filesystem.treeExplorer()
        # make a channel
        channel = journal.debug("qed.archives.s3")
        # if the channel is active
        if channel:
            # show me
            channel.report(
                report=explorer.explore(node=self.fs, label=self.fs.location().address)
            )
            # flush
            channel.log()

        # all done
        return

    # visitor support
    def identify(self, visitor, **kwds):
        """
        Let {visitor} know i'm an S3 archive
        """
        # attempt to
        try:
            # ask {visitor} for it's base handler
            handler = visitor.onS3
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
            import boto3
        # if anything goes wrong
        except ImportError as error:
            # no dice
            return False
        # otherwise, chances are good the runtime support is present
        return True

    # constants
    tag = "s3"
    label = "s3"


# end of file
