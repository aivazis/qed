# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Chore import Chore


# a picklable request to build a run of tiles of one pyramid level
class Decimate(Chore):
    """
    A picklable request to build a run of tiles of one level of a dataset's pyramid

    The level below must exist already: level one reads the product, and every level after
    it reads the level beneath, which whoever handed out this work committed before asking
    for anything above it. The tiles named here belong to this task alone, so the worker
    writes their slots and nothing else; which of them turned out to hold anything travels
    back in the records, one per tile, and the server keeps the occupancy from those
    """

    # interface - worker side
    def execute(self, readers, **kwds):
        """
        Decimate my tiles into the draft of my level, for my dataset and for my partners, and
        report what each tile of each of them held

        The rasters are visited tile by tile, so the pages of the product that a tile needs
        are fetched once for all of them, while they are in the page buffer
        """
        # carefully, since failures here should not poison the crew member
        try:
            # locate my reader, building it on first contact; the records i return are
            # the measurement, so the datasets need not sample themselves as they open
            reader = self._locateReader(readers=readers, measure=False)
            # the rasters to decimate: my dataset first, then my partners, in their order
            rasters = [
                self._prepare(reader=reader, selector=selector, name=name)
                for name, selector in ((self.dataset, self.selector), *self.partners)
            ]
            # the layout of the level, which the rasters share
            extent, tile, _ = rasters[0][1].layout(exponent=self.exponent)
            # the pages the reader's file has fetched so far, if it can tell
            before = self._fetched(reader=reader)
            # the records, one pile per raster, one entry per tile
            records = [[] for _ in rasters]
            # go through my tiles
            for row, col in self.tiles:
                # where each one starts, in the coordinates of the level
                origin = (row * tile[0], col * tile[1])
                # and how far it reaches, clipped to the extent at the edges
                shape = tuple(
                    min(width, axis - start) for width, axis, start in zip(tile, extent, origin)
                )
                # go through the rasters
                for pile, (dataset, pyramid, source, draft) in zip(records, rasters):
                    # decimate the level below into the tile; a tile of pure fill is skipped,
                    # so the level stays as sparse as the product it came from
                    record = dataset.kernels.decimate(
                        source=source,
                        destination=draft,
                        datatype=dataset.datatype.htype,
                        origin=origin,
                        shape=shape,
                        stride=(2, 2),
                    )
                    # record what it held
                    pile.append(((row, col), record))
            # let go of the writable mappings
            rasters.clear()
            # the pages my tiles cost, if the reader's file can tell
            after = self._fetched(reader=reader)
            fetched = after - before if after is not None and before is not None else 0
        # any failure at all
        except Exception as error:
            # is reported as a task failure that leaves the crew member healthy
            raise self.RecoverableError(description=str(error)) from None
        # hand back the records of each raster, and the pages fetched to make them
        return records, fetched

    def _prepare(self, reader, selector, name):
        """
        Find the dataset of {reader} with {selector}, called {name} on the team side, and take
        hold of what decimating it needs: its pyramid, the raster its level is built from, and
        the draft of the level
        """
        # find the dataset
        dataset = self._locateDataset(reader=reader, selector=selector)
        # a dataset no kernel can read gets no levels, and whoever asked should know
        if dataset.kernels is None:
            # so complain
            raise self.RecoverableError(
                description=f"'{name}' has no kernels: its cells are encoded"
            )
        # take hold of the pyramid, with whatever levels exist by now
        pyramid = self._attachPyramid(reader=reader, dataset=dataset)
        # the raster this level is built from: the product for the first level, and the level
        # beneath for every other, which must have been committed already
        source = (
            dataset.data.dataset if self.exponent == 1 else pyramid.at(exponent=self.exponent - 1)
        )
        # if it is not there
        if source is None:
            # the work was handed out too early, and that is a bug
            raise self.RecoverableError(
                description=(
                    f"level {self.exponent - 1} of '{name}' is not there, "
                    f"so level {self.exponent} cannot be built"
                )
            )
        # take hold of the level being built, for writing
        draft = pyramid.draft(exponent=self.exponent)
        # hand it all off
        return dataset, pyramid, source, draft

    # metamethods
    def __init__(self, reader, dataset, workspace, exponent, tiles, partners=(), **kwds):
        # chain up
        super().__init__(**kwds)
        # the reader recipe
        self.reader = reader.pyre_name
        self.factory = reader.pyre_family()
        self.config = self._harvestReader(reader=reader)
        # the dataset, by its selector
        self.selector = dict(dataset.selector)
        self.dataset = dataset.pyre_name
        # the rasters whose same tiles are built along with mine, by name and selector
        self.partners = tuple((partner.pyre_name, dict(partner.selector)) for partner in partners)
        # where the levels live
        self.workspace = str(workspace.path)
        # the level being built, and the tiles of it that are mine
        self.exponent = exponent
        self.tiles = tuple(tuple(tile) for tile in tiles)
        # my identity: the reader, the dataset, the level, and the tiles; the credentials
        # are left out, since they do not change what the work is
        spec = {name: value for name, value in self.config.items() if name != "credentials"}
        self.identity = self._freeze(
            value=(
                self.reader,
                self.factory,
                spec,
                self.selector,
                self.exponent,
                self.tiles,
                tuple((name, tuple(sorted(selector.items()))) for name, selector in self.partners),
            )
        )
        # all done
        return

    # implementation details
    def _fetched(self, reader):
        """
        Report the pages the file of {reader} has fetched so far, or {None} if it cannot tell
        """
        # a reader whose file has a page buffer knows
        paging = getattr(reader, "paging", None)
        # ask it, if it can be asked
        seen = paging() if paging is not None else None
        # the misses are the pages fetched
        return seen[2] if seen is not None else None

    def _attachPyramid(self, reader, dataset):
        """
        Take hold of the pyramid of {dataset}, with every level that exists by now
        """
        # the pyramid a render attached earlier, if any
        pyramid = getattr(dataset, "pyramid", None)
        # if there is none
        if pyramid is None:
            # point a workspace at where the server keeps what it derives
            workspace = qed.workspaces.local(name=f"{self.reader}.crew.workspace")
            workspace.path = self.workspace
            # make one
            pyramid = qed.readers.nisar.pyramid(reader=reader, dataset=dataset, workspace=workspace)
            # and hand it to the dataset, so the renders find it
            dataset.pyramid = pyramid
        # attaching is idempotent: it picks up the levels that have appeared since
        pyramid.attach()
        # hand it back
        return pyramid


# end of file
