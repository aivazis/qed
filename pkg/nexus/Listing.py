# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Chore import Chore

# what a listing reports
from .Manifest import Manifest


# the unit of work that lists a folder of a data archive
class Listing(Chore):
    """
    A picklable request to list one folder of a data archive

    The archive is mounted where the listing runs: a crew member rebuilds it from its recipe,
    keeps it mounted so later folders of the same archive are answered from what it already
    knows, and ships back a manifest of the folder. Listing is sequential work, so the
    request employs exactly one worker; what the arrangement buys is placement, since a slow
    bucket or a remote catalog never blocks the event loop
    """

    # interface - worker side
    def execute(self, archives, **kwds):
        """
        List my folder using {archives}, the registry of archives owned by my crew member
        """
        # carefully, since an unreachable archive should not poison the crew member
        try:
            # locate my archive, mounting it on first contact
            archive = self._locateArchive(archives=archives)
            # and take the listing
            manifest = Manifest.compose(archive=archive, uri=qed.primitives.uri.parse(self.uri))
        # any failure at all
        except Exception as error:
            # is reported as a task failure that leaves the crew member healthy; the tree
            # side records the reason against the folder
            raise self.RecoverableError(description=str(error)) from None
        # hand off the report
        return manifest

    # metamethods
    def __init__(self, archive, uri, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the archive name; it keys the worker side archive registry
        self.archive = archive.pyre_name
        # and its family, so workers can rebuild it
        self.factory = archive.pyre_family()
        # harvest the archive configuration needed to mount it
        self.config = self._harvestReader(reader=archive)
        # the folder to list
        self.uri = str(uri)
        # my identity is the folder and the archive that holds it; what is on display does
        # not change what a folder holds, so two requests for the same folder are the same
        # work and a repeat joins the one in flight
        spec = {name: value for name, value in self.config.items() if name != "expanded"}
        self.identity = self._freeze(value=(self.archive, self.factory, spec, self.uri))
        # all done
        return

    # implementation details - worker side
    def _locateArchive(self, archives):
        """
        Retrieve my archive from the {archives} registry, mounting it on first contact
        """
        # if my archive is already in the registry
        if self.archive in archives:
            # use it
            return archives[self.archive]
        # otherwise, resolve my factory
        factory = qed.protocols.archive.pyre_resolveSpecification(spec=self.factory)
        # build a fresh instance so this process owns its sessions and handles; the derived
        # name avoids clashing with the tree side instance this process may have inherited
        archive = factory(name=f"{self.archive}.crew", **self.config)
        # register it
        archives[self.archive] = archive
        # and hand it off
        return archive


# end of file
