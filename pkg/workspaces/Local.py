# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import os

# support
import journal
import qed


# a workspace rooted in a directory on local disk
class Local(qed.component, family="qed.workspaces.local", implements=qed.protocols.workspace):
    """
    The local directory qed works out of, and the keeper of everything it derives

    Products are read-only, and often not even local, so anything qed computes and wants to
    keep -- decimated pyramid levels today, whatever comes next -- has to live somewhere
    else. That somewhere is here, and it defaults to the directory the user launched from,
    which is the one that holds their configuration file: derived state then sits beside the
    work it belongs to, travels with it, and is thrown away by deleting a directory the user
    already knows about, rather than accumulating out of sight under a home directory
    """

    # user configurable state
    path = qed.properties.path()
    path.default = "."
    path.doc = "the directory that holds whatever qed derives from its data products"

    caches = qed.properties.str()
    caches.default = ".qed"
    caches.doc = "the name of the folder, within my path, that holds derived data"

    # interface
    def describe(self) -> dict:
        """
        Describe where i am and what i hold: each product that has derived data here, the kind
        of data, and the bytes it occupies on disk, counting only the blocks that were written,
        since the levels of a pyramid are sparse files
        """
        # the folder that gathers everything qed derives
        root = self.path / self.caches
        # the products, by kind
        products = []
        # if the folder is there
        if root.isDirectory():
            # go through the kinds of derived data, e.g. the pyramids
            for kind in sorted(os.scandir(str(root)), key=lambda entry: entry.name):
                # skipping anything that is not a folder
                if not kind.is_dir():
                    continue
                # and the products within each
                for product in sorted(os.scandir(kind.path), key=lambda entry: entry.name):
                    # skipping anything that is not a folder
                    if not product.is_dir():
                        continue
                    # measure it
                    products.append(
                        {"kind": kind.name, "name": product.name, "bytes": self._size(product.path)}
                    )
        # assemble the description
        return {"path": str(self.path), "products": products}

    # obligations
    @qed.export
    def cache(self, name: str):
        """
        Retrieve the directory that holds derived data of the given {name}, making it on
        first use
        """
        # my directory belongs to the user: it is where they are working, and the default
        # is wherever they launched from, so it exists. one that does not is a mistake in
        # the configuration, and making it silently would turn a typo into a tree
        if not self.path.isDirectory():
            # make a channel
            channel = journal.error("qed.workspace")
            # complain
            channel.line(f"the workspace at '{self.path}' is not a directory")
            channel.line(f"so there is nowhere to keep the '{name}' cache")
            channel.line(f"make it, or point '{self.pyre_family()}.path' somewhere else")
            # flush
            channel.log()
            # and report that there is nowhere to keep anything
            return None
        # what lies below is mine to make: the folder that gathers everything qed derives,
        # and the one within it that holds this kind of derived data
        location = self.path / self.caches / name
        # carefully, since the workspace may not be writable
        try:
            # make sure it is there
            location.mkdir(parents=True, exist_ok=True)
        # if it cannot be made
        except OSError as error:
            # make a channel
            channel = journal.warning("qed.workspace")
            # complain
            channel.line(f"could not make the '{name}' cache")
            channel.line(f"at '{location}'")
            channel.line(f"got: {error}")
            channel.line(f"whatever would have been kept there will be recomputed")
            # flush
            channel.log()
            # and report that there is nowhere to keep anything
            return None
        # hand off the location
        return location

    # implementation details
    def _size(self, folder: str) -> int:
        """
        Measure the bytes the files under {folder} occupy on disk
        """
        # the total
        total = 0
        # go through the files
        for directory, _, names in os.walk(folder):
            for name in names:
                # carefully, since a build may replace a file while it is being counted
                try:
                    # add its blocks, in the units the system reports them in
                    total += os.stat(os.path.join(directory, name)).st_blocks * 512
                # a file that is gone
                except FileNotFoundError:
                    # occupies nothing
                    continue
        # all done
        return total


# end of file
