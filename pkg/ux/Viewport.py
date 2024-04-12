# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal
import uuid

# my parts
from .View import View


# information about the contents of a viewport
class Viewport(
    qed.component,
    family="qed.ux.viewports.viewport",
    implements=qed.protocols.ux.viewport,
):

    # interface
    def tile(self, **kwds):
        """
        Extract a tile of data from my view
        """
        # get my view
        view = self._view
        # and delegate
        return view.tile(**kwds)

    def view(self):
        """
        Return the current source selection
        """
        # easy enough
        return self._view

    def selectSource(self, source):
        """
        Select the view associated with the reader with the given {name}
        """
        # activate the {source}
        self._selectSource(source=source)
        # all done
        return self.view()

    def setChannel(self, source, tag):
        """
        Set the channel to the one with the given {tag}
        """
        # activate the {source}
        view = self._selectSource(source=source)
        # and delegate
        return view.setChannel(tag=tag)

    def toggleCoordinate(self, source, axis, coordinate):
        """
        Toggle {coordinate}
        """
        # activate the {source}
        view = self._selectSource(source=source)
        # and delegate
        view.toggleSelection(key=axis, value=coordinate)
        # all done
        return self.view()

    def toggleMeasure(self, source):
        """
        Toggle {coordinate}
        """
        # activate the {source}
        view = self._selectSource(source=source)
        # and delegate
        view.toggleMeasure()
        # all done
        return self.view()

    def measureAddAnchor(self, x, y, index):
        """
        Add an anchor to my measure path
        """
        # get my active view
        view = self._view
        # and delegate
        view.measureAddAnchor(x=x, y=y, index=index)
        # all done
        return view

    def measureAnchorPlace(self, handle, x, y):
        """
        Place an existing anchor at the specific ({x}, {y}) location
        """
        # get my active view
        view = self._view
        # and delegate
        return view.measureAnchorPlace(handle=handle, x=x, y=y)

    def measureAnchorMove(self, handle, dx, dy):
        """
        Displace the anchor selection by ({dx}, {dy})
        """
        # get my active view
        view = self._view
        # and delegate
        return view.measureAnchorMove(handle=handle, dx=dx, dy=dy)

    def measureAnchorRemove(self, anchor):
        """
        Remove an anchor from the pile
        """
        # get my active view
        view = self._view
        # and delegate
        return view.measureAnchorRemove(anchor=anchor)

    def measureAnchorSplit(self, anchor):
        """
        Split in two the leg that starts at {anchor}
        """
        # get my active view
        view = self._view
        # and delegate
        return view.measureAnchorSplit(anchor=anchor)

    def measureAnchorExtendSelection(self, index):
        """
        Extend the anchor selection to the given {index}
        """
        # get my active view
        view = self._view
        # delegate
        view.measureAnchorExtendSelection(index=index)
        # all done
        return view

    def measureAnchorToggleSelection(self, index):
        """
        Toggle {index} in the anchor selection in single node mode
        """
        # get my active view
        view = self._view
        # delegate
        view.measureAnchorToggleSelection(index=index)
        # all done
        return view

    def measureAnchorToggleSelectionMulti(self, index):
        """
        Toggle {index} in the anchor selection in multinode mode
        """
        # get my active view
        view = self._view
        # delegate
        view.measureAnchorToggleSelectionMulti(index=index)
        # all done
        return view

    def measureSetClosedPath(self, closed):
        """
        Set the {closed} path flag
        """
        # get my active view
        view = self._view
        # delegate
        view.measureSetClosedPath(closed=closed)
        # all done
        return view

    def measureReset(self):
        """
        Reset the state of the {measure} layer
        """
        # get my active view
        view = self._view
        # and delegate
        return view.measureReset()

    def syncSetAspect(self, aspect, value):
        """
        Set the {aspect} flag of my sync table to {value}
        """
        # activate the {source}
        view = self.view()
        # and delegate
        return view.syncSetAspect(aspect=aspect, value=value)

    def syncToggleAspect(self, aspect):
        """
        Toggle the {aspect} flag of my sync table
        """
        # activate the {source}
        view = self.view()
        # and delegate
        return view.syncToggleAspect(aspect=aspect)

    def syncReset(self):
        """
        Reset the state of the {sync} table
        """
        # get my active view
        view = self._view
        # and delegate
        return view.syncReset()

    def vizResetController(self, **kwds):
        """
        Reset a controller of my active visualization pipeline
        """
        # get my active view
        view = self._view
        # update the controller
        controller = view.vizResetController(**kwds)
        # and hand off the pair
        return view, controller

    def vizUpdateController(self, **kwds):
        """
        Update a controller of my active visualization pipeline
        """
        # get my active view
        view = self._view
        # update the controller
        controller = view.vizUpdateController(**kwds)
        # and hand off the pair
        return view, controller

    def zoomSetLevel(self, horizontal, vertical):
        """
        Set the zoom levels
        """
        # get the view
        view = self._view
        # and delegate
        return view.zoomSetLevel(horizontal=horizontal, vertical=vertical)

    def zoomSetCoupled(self, flag):
        """
        Set the lock flag
        """
        # get the view
        view = self._view
        # and delegate
        return view.zoomSetCoupled(flag)

    def zoomReset(self):
        """
        Reset the state of the {zoom} info
        """
        # get my active view
        view = self._view
        # and delegate
        return view.zoomReset()

    def clone(self):
        """
        Make a copy of me
        """
        # get my view
        view = self._view
        # make a name for the clone
        name = str(uuid.uuid1())
        # build the new instance
        clone = type(self)(name=name, view=view.clone())
        # select my reader
        clone.selectSource(source=view.reader)
        # and return the clone
        return clone

    # metamethods
    def __init__(self, view=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # normalize the view
        view = view or View(name=str(uuid.uuid1()))
        # initialize my view
        self._view = view
        # my cache of views
        self._views = {view.reader and view.reader.pyre_name: view}
        # and my cache of visualization pipeline configurations
        self._viz = {}
        # all done
        return

    # implementation details
    def _selectSource(self, source):
        """
        Select the source with the given {name} to be the active one
        """
        # get the source name
        name = source.pyre_name
        # get my cache
        cache = self._views
        # look through my cache for stored settings
        view = cache.get(name)
        # if its not there
        if not view:
            # build a view
            view = View(name=str(uuid.uuid1()), reader=source)
            # add it to my cache
            cache[name] = view
        # install it
        self._view = view
        # and return its source selection
        return view


# end of file
