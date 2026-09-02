# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# what a survey learned about one dataset
class Finding:
    """
    The metadata of a single dataset, as measured by the crew member that performed first
    contact with its product

    Findings are plain picklable values authored by the dataset flavor itself: they carry
    the factory and the trait settings that let the team side materialize a metadata-only
    twin, along with the seed statistics in exactly the shape that flavor's channels
    expect, which is what dissolves the shape hazard of a uniform seed
    """

    # metamethods
    def __init__(
        self,
        factory,
        cell,
        shape,
        origin,
        tile,
        channels,
        stats,
        suffix=None,
        selector=None,
        companions=None,
        **kwds,
    ):
        # chain up
        super().__init__(**kwds)
        # the family name of the dataset class, so hydration can resolve the factory
        self.factory = factory
        # the family name of the cell type
        self.cell = cell
        # the layout
        self.shape = shape
        self.origin = origin
        self.tile = tile
        # the tags of the supported visualization channels
        self.channels = channels
        # the seed statistics, in whatever shape my flavor produced them
        self.stats = stats
        # where my name sits relative to my owner's, so my twin can be named the same way
        self.suffix = suffix
        # the selector that identifies me to my reader
        self.selector = selector
        # the rasters i am read alongside, by role, as name suffixes relative to my owner's,
        # so my twin can be wired to theirs
        self.companions = companions or {}
        # all done
        return


# end of file
