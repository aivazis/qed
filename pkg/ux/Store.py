# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal
import uuid

# my parts
from .DataArchives import DataArchives
from .DataSources import DataSources
from .Viewport import Viewport


# the server side of the application store
class Store(qed.shells.command, family="qed.cli.ux"):
    """
    The application state as known to the server
    """

    # interface
    # archives
    @property
    def archives(self):
        """
        Retrieve the sequence of registered archives
        """
        # delegate
        return self._dataArchives.archives()

    def archive(self, uri):
        """
        Retrieve an archive given its {uri}
        """
        # easy enough
        return self._dataArchives.archive(uri=uri)

    def nArchives(self):
        """
        Return the number of connected archives
        """
        # easy enough
        return len(self._dataArchives)

    def connectArchive(self, archive):
        """
        Connect a new archive
        """
        # delegate to my archive store
        return self._dataArchives.addArchive(archive=archive)

    def disconnectArchive(self, uri):
        """
        Disconnect an archive
        """
        # delegate to my archive store
        return self._dataArchives.removeArchive(uri=uri)

    # readers
    @property
    def sources(self):
        """
        Retrieve the sequence of registered readers
        """
        # delegate
        yield from self._dataSources.sources()
        # all done
        return

    def source(self, name):
        """
        Retrieve an reader given its {name}
        """
        # easy enough
        return self._dataSources.source(name=name)

    def nSources(self):
        """
        Return the number of connected readers
        """
        # easy enough
        return len(self._dataSources)

    def connectSource(self, source):
        """
        Connect a new data source
        """
        # delegate to my source store
        return self._dataSources.addSource(source=source)

    def disconnectSource(self, name):
        """
        Disconnect a data source
        """
        # delegate to my source store
        return self._dataSources.removeSource(name=name)

    # datasets
    def dataset(self, name):
        """
        Retrieve a dataset given its {name}
        """
        # delegate to my source catalog
        return self._dataSources.dataset(name=name)

    # views
    @property
    def viewports(self):
        """
        Retrieve the sequence of current views
        """
        # go through my pile of views
        yield from self._viewports
        # all done
        return

    def collapseViewport(self, viewport):
        """
        Collapse the indicated {viewport}
        """
        # get my viewports
        viewports = self._viewports
        # pop the indicated one
        port = viewports.pop(viewport)
        # if the pile of viewports is now empty
        if not viewports:
            # make a new onw
            port = Viewport(name=str(uuid.uuid1()))
            # add it to the pile
            viewports.append(port)
        # all done
        return port.view()

    def splitViewport(self, viewport):
        """
        Split the indicated {viewport}
        """
        # get my viewports
        viewports = self._viewports
        # grab the view in {viewport}
        view = viewports[viewport]
        # make a copy of it
        clone = view.clone()
        # add it to the pile
        viewports.insert(viewport + 1, clone)
        # and return it
        return clone.view()

    def selectSource(self, viewport, name):
        """
        Prepare {viewport} to display the source given its {name}
        """
        # locate the source
        source = self.source(name=name)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and ask it to select the named reader
        return port.selectSource(source=source)

    def toggleChannel(self, viewport, source, tag):
        """
        Toggle the value of {channel}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        return port.toggleChannel(source=source, tag=tag)

    def toggleCoordinate(self, viewport, source, axis, coordinate):
        """
        Toggle the value of {coordinate}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        return port.toggleCoordinate(source=source, axis=axis, coordinate=coordinate)

    def toggleMeasure(self, viewport, source):
        """
        Toggle the measure layer state on {viewport}
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        view = port.toggleMeasure(source=source)
        # return the measure configuration
        return view.measure

    def setSync(self, viewport, aspect):
        """
        Toggle the scroll flag of the sync table
        """
        # get the value from the viewport
        value = getattr(self._viewports[viewport].view().sync, aspect)
        # go through all my viewports
        for port in self._viewports:
            # and ask each one to set its {aspect} flag to the reference value
            view = port.setSync(aspect=aspect, value=value)
            # hand off its scroll table
            yield view.sync
        # all done
        return

    def toggleScrollSync(self, viewport, source):
        """
        Toggle the scroll flag of the sync table
        """
        # locate the source
        source = self.source(name=source)
        # get the viewport configuration
        port = self._viewports[viewport]
        # and delegate
        view = port.toggleScrollSync(source=source)
        # return the measure configuration
        return view.sync

    # metamethods
    def __init__(self, plexus, docroot, **kwds):
        # chain up
        super().__init__(plexus=plexus, spec="store", **kwds)
        # save the root of the document
        self._docroot = docroot
        # map: name -> data archive
        self._dataArchives = self._loadPersistentArchives(plexus)
        # map: name -> data source
        self._dataSources = self._loadPersistentSources(plexus)
        # my viewports: start out with one
        self._viewports = [Viewport(name=str(uuid.uuid1()))]
        # all done
        return

    # implementation details
    def _loadPersistentArchives(self, plexus):
        """
        Transfer the persistent data sources and their datasets from the plexus
        """
        # build the map
        archives = DataArchives()
        # go through the plexus sources
        for archive in plexus.archives:
            # and connect them
            archives.addArchive(archive=archive)
        # clear out the plexus pile
        plexus.archives = []
        # all done
        return archives

    def _loadPersistentSources(self, plexus):
        """
        Transfer the persistent data sources and their datasets from the plexus
        """
        # build the map
        sources = DataSources()
        # go through the plexus sources
        for reader in plexus.datasets:
            # and connect them
            sources.addSource(source=reader)
        # clear out the plexus pile
        plexus.datasets = []
        # all done
        return sources

    # debugging support
    def pyre_dump(self):
        """
        Generate a report with my contents
        """
        # make a channel
        channel = journal.info("qed.ux")
        # sign on
        channel.line("qed store:")
        channel.indent()
        # show me the static assets
        channel.line("static assets:")
        channel.indent()
        channel.report(self._docroot.dump())
        channel.outdent()

        # my archives
        channel.line("archives:")
        channel.indent()
        channel.report(archive.uri for archive in self._dataArchives.archives())
        channel.outdent()

        # my readers
        channel.line("readers:")
        channel.indent()
        channel.report(reader.uri for reader in self._dataSources.sources())
        channel.outdent()

        # flush
        channel.log()
        # all done
        return


# end of file
