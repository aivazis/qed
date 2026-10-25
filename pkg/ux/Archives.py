# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# catalog of known data archives
class Archives:
    """
    A catalog of known data archives and their datasets
    """

    # interface
    def archive(self, uri):
        """
        Retrieve a data archive given its {uri}
        """
        # look up the data archive safely
        return self._archives.get(str(uri))

    def archives(self):
        """
        Retrieve my archives
        """
        # easy enough
        return self._archives.values()

    def addArchive(self, archive):
        """
        Add a data {archive}
        """
        # get the uri of the archive
        uri = str(archive.uri)
        # check whether there is an existing archive with the same uri
        current = self.archive(uri=uri)
        # if there is one
        if current:
            # remove it
            self._removeArchive(archive=current)
        # add the new archive to the pile
        return self._addArchive(archive=archive)

    def relocateArchive(self, archive, uri):
        """
        File {archive}, which used to live at {uri}, under its current location, in the place it
        had in the catalog
        """
        # rebuild the catalog in its current order, swapping the old location for the new one
        self._archives = {
            (str(archive.uri) if location == str(uri) else location): entry
            for location, entry in self._archives.items()
        }
        # all done
        return archive

    def replaceArchive(self, archive, replacement):
        """
        Put {replacement} in the place {archive} has in the catalog
        """
        # the location of the archive
        location = str(archive.uri)
        # rebuild the catalog in its current order, swapping the archive for its replacement
        self._archives = {
            (str(replacement.uri) if key == location else key): (
                replacement if key == location else entry
            )
            for key, entry in self._archives.items()
        }
        # all done
        return replacement

    def removeArchive(self, uri):
        """
        Remove a archive given its {uri}
        """
        # look it up
        archive = self.archive(uri=str(uri))
        # if present
        if archive:
            # remove it
            self._removeArchive(archive=archive)
        # all done
        return archive

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # map: uri -> data archive
        self._archives = {}
        # all done
        return

    def __len__(self):
        """
        Compute the number of registered archives
        """
        # easy enough
        return len(self._archives)

    def __iter__(self):
        """
        Iterate over my values
        """
        # easy enough
        return self._archives.values()

    # implementation details
    def _addArchive(self, archive):
        """
        Add {archive}
        """
        # get its uri
        uri = str(archive.uri)
        # add it to the pile
        self._archives[uri] = archive
        # all done
        return archive

    def _removeArchive(self, archive):
        """
        Remove a archive and its datasets
        """
        # get the uri of the archive
        uri = str(archive.uri)
        # remove it from the pile
        del self._archives[uri]
        # all done
        return archive


# end of file
