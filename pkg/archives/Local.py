# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# superclass
from .Archive import Archive


# a local data archive
class Local(Archive, family="qed.archives.local"):
    """
    A data archive that resides on local disk
    """

    # user configurable state
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="file", address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"

    all = qed.properties.bool()
    all.default = False
    all.doc = "do not ignore entries that start with '.'"

    # constants
    readers = "nisar", "isce2", "gdal", "native"

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve my contents at {uri}, a location expected to belong within the archive document
        space
        """
        # get my root, mounting my filesystem on first contact
        root = self.fs if self.fs is not None else self.mount()
        # and the filter state
        all = self.all
        # get the target address, resolved the way the root was when the filesystem was
        # mounted, so a request spelled through a symbolic link still lands within it
        path = qed.primitives.path(uri.address).resolve()
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
            (name, f"file:{node.uri}", node.isFolder)
            for name, node in sorted(root.contents.items())
            if not node.isFolder and (all or not name.startswith("."))
        ]
        # and a pile of directories
        folders = [
            (name, f"file:{node.uri}", node.isFolder)
            for name, node in sorted(root.contents.items())
            if node.isFolder and (all or not name.startswith("."))
        ]
        # present them in this order
        return folders + datasets

    def mount(self):
        """
        Mount the local filesystem at my location
        """
        # build the filesystem
        fs = qed.filesystem.local(root=self.uri.address)
        # attach it
        self.fs = fs
        # and hand it back
        return fs

    # naming
    @classmethod
    def nicknames(cls, uri: str, collection: str | None = None) -> list:
        """
        Propose the nicknames of an archive at {uri}: the name of its folder, then more and more
        of the path that leads to it, until all of it is in
        """
        # the folders on the way to the archive
        levels = [level for level in qed.primitives.uri.parse(uri).address.split("/") if level]
        # the last one, then the last two, and so on, each joined into a single level
        return ["_".join(levels[-count:]) for count in range(1, len(levels) + 1)]

    # hooks
    @classmethod
    def isSupported(cls):
        """
        Check whether there is runtime support for this archive type
        """
        # always available...
        return True

    # constants
    tag = "local"
    label = "local"

    # private data
    # my filesystem, mounted on first contact
    fs = None


# end of file
