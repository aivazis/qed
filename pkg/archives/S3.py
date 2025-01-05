# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal


# a S3 data archive
class S3(qed.component, family="qed.archives.s3", implements=qed.protocols.archive):
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
    def contents(self, uri, **kwds):
        """
        Retrieve my contents at {uri}
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
        channel = journal.info("qed.archives.s3")
        # show me
        channel.report(
            report=explorer.explore(node=self.fs, label=self.fs.location().address)
        )
        # flush
        channel.log()

        # all done
        return


# end of file
