# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal


# a local data archive
class Archive(qed.component, family="qed.archives.base", implements=qed.protocols.archive):
    """
    The base data archive
    """

    # user configurable state
    uri = qed.properties.uri()
    uri.default = qed.primitives.uri(scheme="file", address=qed.primitives.path.cwd())
    uri.doc = "the location of the archive"

    expanded = qed.properties.list(schema=qed.properties.str())
    expanded.default = []
    expanded.doc = "the folders on display, by uri"

    # constants
    readers = ()

    # interface
    @qed.export
    def contents(self, uri):
        """
        Retrieve my contents at {uri}, a location expected to belong within the archive document
        space
        """
        # i got nothing
        return []

    def credentials(self):
        """
        Generate the credentials necessary to access my contents
        """
        # nothing, by default
        return {}

    # the tree: the folders on display and their listings
    def expand(self, uri):
        """
        Put the folder at {uri} on display and mark its listing as under way
        """
        # normalize
        uri = str(uri)
        # if the folder is not on display yet
        if uri not in self.expanded:
            # add it
            self.expanded = [*self.expanded, uri]
        # a fresh attempt carries no error
        self._errors.pop(uri, None)
        # the listing is under way
        self._pending.add(uri)
        # all done
        return self

    def collapse(self, uri):
        """
        Take the folder at {uri} off display, along with every folder beneath it
        """
        # normalize
        uri = str(uri)
        # the folders beneath it are the folder entries of its listing
        manifest = self._manifests.get(uri)
        # if there is one
        if manifest is not None:
            # go through the entries
            for _, child, isFolder in manifest.entries:
                # the folders
                if isFolder:
                    # get collapsed first
                    self.collapse(uri=child)
        # forget the listing
        self._manifests.pop(uri, None)
        # any attempt under way
        self._pending.discard(uri)
        # and any failure
        self._errors.pop(uri, None)
        # take the folder off display
        self.expanded = [folder for folder in self.expanded if folder != uri]
        # all done
        return self

    def record(self, manifest):
        """
        Take delivery of the {manifest} of one of my folders
        """
        # get the folder
        uri = manifest.uri
        # the listing is no longer under way
        self._pending.discard(uri)
        # a folder taken off display while its listing ran has nowhere to put it
        if uri not in self.expanded:
            # so drop it
            return self
        # otherwise, keep it
        self._manifests[uri] = manifest
        # and clear any earlier failure
        self._errors.pop(uri, None)
        # all done
        return self

    def fail(self, uri, error):
        """
        Record that the listing of the folder at {uri} failed, retaining {error} as the reason
        """
        # normalize
        uri = str(uri)
        # the listing is no longer under way
        self._pending.discard(uri)
        # keep the reason, since the client displays it
        self._errors[uri] = str(error)
        # all done
        return self

    def orphans(self, manifest):
        """
        Find the folders on display that belong beneath the folder that {manifest} lists, but
        are neither among the folders it holds nor beneath one of them

        The folders on display may be a record of what was there in an earlier session, and an
        archive changes shape on its own schedule. A fresh listing of a folder is the authority
        on what it holds, so it settles the fate of everything that claims to live beneath it.
        A listing that could not be taken settles nothing: a folder that cannot be reached
        today says nothing about whether its contents still exist
        """
        # everything beneath the folder starts with its location, as a folder
        stem = manifest.uri.rstrip("/") + "/"
        # the folders it holds
        heirs = [uri.rstrip("/") for _, uri, isFolder in manifest.entries if isFolder]
        # make a pile
        orphans = []
        # go through the folders on display
        for folder in self.expanded:
            # the ones that live elsewhere
            if not folder.startswith(stem):
                # are none of this listing's business
                continue
            # normalize
            location = folder.rstrip("/")
            # a folder that the listing holds, or one that lives beneath such a folder
            if any(location == heir or location.startswith(heir + "/") for heir in heirs):
                # is accounted for, at least as far as this listing can tell
                continue
            # the rest are gone
            orphans.append(folder)
        # hand them off
        return orphans

    def strays(self):
        """
        Find the folders on display that do not belong to me at all
        """
        # my root, and everything beneath it
        root = str(self.uri).rstrip("/")
        stem = root + "/"
        # anything else does not belong
        return [
            folder
            for folder in self.expanded
            if folder.rstrip("/") != root and not folder.startswith(stem)
        ]

    def awaiting(self, manifest):
        """
        Find the folders that {manifest} holds that are on display but have no listing, and
        none under way
        """
        # go through the folders of the listing
        return [
            uri
            for _, uri, isFolder in manifest.entries
            if isFolder
            and uri in self.expanded
            and uri not in self._manifests
            and uri not in self._pending
        ]

    @property
    def dirty(self):
        """
        Check whether saving me would change what the configuration files say about me
        """
        # an archive that was never saved has everything to say
        if self._saved is None:
            # so it is
            return True
        # otherwise, the only thing about me that a session changes is what i have on display;
        # the order in which the folders were opened is not worth a save
        return set(self.expanded) != self._saved

    def saved(self):
        """
        Record that the configuration files say what i say, as of right now: because they were
        just read, or because they were just written
        """
        # remember what i have on display
        self._saved = frozenset(self.expanded)
        # all done
        return self

    def forgotten(self, folders):
        """
        Record that {folders} were taken out of what the configuration files say i have on
        display, e.g. because they are no longer there
        """
        # if there is a record to correct
        if self._saved is not None:
            # take them out
            self._saved = self._saved - set(folders)
        # all done
        return self

    def listing(self, uri):
        """
        Retrieve the manifest of the folder at {uri}, if it has one
        """
        # look it up
        return self._manifests.get(str(uri))

    def isExpanded(self, uri):
        """
        Check whether the folder at {uri} is on display
        """
        # easy enough
        return str(uri) in self.expanded

    def isPending(self, uri):
        """
        Check whether the listing of the folder at {uri} is under way
        """
        # easy enough
        return str(uri) in self._pending

    def failure(self, uri):
        """
        Retrieve the reason the listing of the folder at {uri} failed, if it did
        """
        # look it up
        return self._errors.get(str(uri))

    def items(self):
        """
        Generate the entries of every folder on display, each with the folder that holds it
        """
        # go through the folders on display, in the order they were expanded
        for folder in self.expanded:
            # get the listing
            manifest = self._manifests.get(folder)
            # a folder whose listing has not landed contributes nothing yet
            if manifest is None:
                # so move on
                continue
            # go through the entries
            for name, uri, isFolder in manifest.entries:
                # and describe each one
                yield self.item(
                    name=name,
                    uri=uri,
                    isFolder=isFolder,
                    parent=folder,
                    expanded=isFolder and uri in self.expanded,
                    pending=uri in self._pending,
                    error=self._errors.get(uri),
                )
        # all done
        return

    @staticmethod
    def item(name, uri, isFolder, parent=None, expanded=False, pending=False, error=None):
        """
        Describe an archive entry the way the query layer resolves it
        """
        # pack the description
        return {
            "name": name,
            "uri": uri,
            "isFolder": isFolder,
            "parent": parent,
            "expanded": expanded,
            "pending": pending,
            "error": error,
        }

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the listings of the folders on display, keyed by uri
        self._manifests = {}
        # the folders whose listing is under way
        self._pending = set()
        # what the configuration files say i have on display; nothing, until somebody tells me
        self._saved = None
        # the folders whose listing failed, with the reason
        self._errors = {}
        # all done
        return

    # constants
    tag = "<base>"
    label = "<base>"


# end of file
