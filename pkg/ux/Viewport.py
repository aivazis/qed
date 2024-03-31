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

    def clone(self):
        """
        Make a copy of me
        """
        # make a name for the clone
        name = str(uuid.uuid1())
        # easy enough
        return type(self)(name=name, view=self._view.clone())

    # metamethods
    def __init__(self, view=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # initialize my view
        self._view = view or View(name=str(uuid.uuid1()))
        # and my cache of other selections
        self._cache = {}
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
