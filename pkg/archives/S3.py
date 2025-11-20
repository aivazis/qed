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
        # normalize {uri}
        # MGA: FIXME: remove the normalization after {uri} has {path} in {address}
        uri.address = qed.primitives.path(uri.address)
        # get my root
        root = self.fs
        # project it onto the root of my filesystem
        rel = uri.address.relativeTo(root.uri.address)
        # ask for the folder at {uri}
        folder = root[rel]
        # look down one level
        folder.discover(levels=1)
        # make a pile of files
        files = [
            (name, node.uri, node.isFolder)
            for name, node in folder.contents.items()
            if not node.isFolder
        ]
        # and a pile of directories
        folders = [
            (name, node.uri, node.isFolder)
            for name, node in folder.contents.items()
            if node.isFolder
        ]
        # and present them in this order
        return folders + files

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # mount my s3 filesystem
        self.fs = qed.filesystem.s3(root=self.uri).discover(levels=1)

        # make a channel
        channel = journal.debug("qed.archives.s3")
        # if the channel is active
        if channel:
            # make an explorer
            explorer = qed.filesystem.treeExplorer()
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
