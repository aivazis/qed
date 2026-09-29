# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the zoom a view is shown at
class EffectiveZoom:
    """
    The zoom of a view as it is shown: the zoom the view keeps, but no further out than the
    levels of its dataset that exist, so that nothing asks for a level still being built

    The zoom the view keeps is left alone, so a view that is shown at a shallower level while its
    pyramid is built moves to its own level as soon as that level exists
    """

    # the zoom levels, as they are shown
    @property
    def horizontal(self) -> float:
        """
        The horizontal zoom level, no further out than my floor
        """
        # clamp the level the view keeps
        return max(self._zoom.horizontal, self._floor)

    @property
    def vertical(self) -> float:
        """
        The vertical zoom level, no further out than my floor
        """
        # clamp the level the view keeps
        return max(self._zoom.vertical, self._floor)

    # everything else is the view's own
    @property
    def pyre_name(self) -> str:
        """
        The name of the zoom of the view
        """
        # easy enough
        return self._zoom.pyre_name

    def pyre_family(self) -> str:
        """
        The family of the zoom of the view
        """
        # easy enough
        return self._zoom.pyre_family()

    @property
    def coupled(self) -> bool:
        """
        Whether the two levels change together
        """
        # easy enough
        return self._zoom.coupled

    @property
    def dirty(self) -> bool:
        """
        Whether the zoom of the view differs from its defaults
        """
        # easy enough
        return self._zoom.dirty

    # metamethods
    def __init__(self, zoom, floor: int, **kwds):
        # chain up
        super().__init__(**kwds)
        # the zoom the view keeps
        self._zoom = zoom
        # and the furthest out level that can be shown, as a zoom level
        self._floor = floor
        # all done
        return


# end of file
