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

    def toggleChannel(self, source, tag):
        """
        Toggle {coordinate}
        """
        # activate the {source}
        view = self._selectSource(source=source)
        # and delegate
        view.toggleChannel(tag=tag)
        # all done
        return self.view()

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

    def setSync(self, aspect, value):
        """
        Toggle the scroll flag of my sync table
        """
        # delegate to my active view
        return self._view.setSync(aspect=aspect, value=value)

    def toggleSync(self, source, aspect):
        """
        Toggle the scroll flag of my sync table
        """
        # activate the {source}
        view = self._selectSource(source=source)
        # and delegate
        view.toggleSync(aspect=aspect)
        # all done
        return self.view()

    def toggleScrollSync(self, source):
        """
        Toggle the scroll flag of my sync table
        """
        # activate the {source}
        view = self._selectSource(source=source)
        # and delegate
        view.toggleScrollSync()
        # all done
        return view

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
        # and my selection cache
        self._cache = {view.reader and view.reader.pyre_name: view}
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
        cache = self._cache
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
