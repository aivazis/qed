# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import time


# the report a listing ships back
class Manifest:
    """
    The listing of one folder of a data archive: what the folder held the moment it was
    listed, taken where the archive is mounted and shipped to where its tree is kept

    The record is a nest of plain values, so it pickles cleanly and carries no file handles
    or sessions; the tree side stores it as is and resolves the archive items from it
    """

    # interface - worker side
    @classmethod
    def compose(cls, archive, uri):
        """
        List the folder at {uri} of {archive} and record what it holds
        """
        # ask the archive for the folder contents, normalizing each entry to wire form
        entries = tuple(
            (str(name), str(location), bool(isFolder))
            for name, location, isFolder in archive.contents(uri=uri)
        )
        # a query backed archive knows how many entries the catalog holds in all
        hits = getattr(getattr(archive, "fs", None), "hits", None)
        # build the record and hand it off
        return cls(uri=str(uri), entries=entries, sync=time.time(), hits=hits)

    # metamethods
    def __init__(self, uri, entries, sync, hits=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # the folder that was listed
        self.uri = uri
        # its contents, as (name, uri, isFolder) triples
        self.entries = entries
        # the moment the listing was taken
        self.sync = sync
        # and the size of the whole, when the archive can tell
        self.hits = hits
        # all done
        return


# end of file
