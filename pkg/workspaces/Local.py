# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import journal
import qed


# a workspace rooted in a directory on local disk
class Local(
    qed.component, family="qed.workspaces.local", implements=qed.protocols.workspace
):
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

    # obligations
    @qed.export
    def cache(self, name: str):
        """
        Retrieve the directory that holds derived data of the given {name}, making it on
        first use
        """
        # assemble the location
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


# end of file
