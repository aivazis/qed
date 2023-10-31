# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# support
import qed
import journal


# a local data archive
class Local(
    qed.component, family="qed.archives.local", implements=qed.protocols.archive
):
    """
    A data archive that resides on local disk
    """

    # the location
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="file", address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"

    # interface
    def getContents(self, uri):
        """
        Retrieve my contents at {path}
        """
        # get my root
        root = self.fs
        # get the target address
        path = qed.primitives.path(uri.address)
        # project the {address} onto my {root}
        rel = path.relativeTo(root.uri)
        # starting at the top, descend as many levels as necessary
        for crumb in rel:
            # sync with the file
            root.discover(levels=1)
            # point to the new folder
            root = root[crumb]
        # sync it with the filesystem
        root.discover(levels=1)
        # make a pile of datasets
        datasets = [
            (name, node.uri, node.isFolder)
            for name, node in sorted(root.contents.items())
            if not node.isFolder
        ]
        # and a pile of directories
        folders = [
            (name, node.uri, node.isFolder)
            for name, node in sorted(root.contents.items())
            if node.isFolder
        ]
        # present them in this order
        return folders + datasets

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # mount my local filesystem
        self.fs = qed.filesystem.local(root=self.uri.address)
        # all done
        return


# end of file
