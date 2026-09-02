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
        Decimate my tiles into the draft of my level, and report what each one held
        """
        # carefully, since failures here should not poison the crew member
        try:
            # locate my reader, building it on first contact; the records i return are
            # the measurement, so the datasets need not sample themselves as they open
            reader = self._locateReader(readers=readers, measure=False)
            # find the dataset i'm after
            dataset = self._locateDataset(reader=reader)
            # the kernels that read its cells
            kernels = dataset.kernels
            # a dataset no kernel can read gets no levels, and whoever asked should know
            if kernels is None:
                # so complain
                raise self.RecoverableError(
                    description=f"'{self.dataset}' has no kernels: its cells are encoded"
                )
            # take hold of the pyramid, with whatever levels exist by now
            pyramid = self._attachPyramid(reader=reader, dataset=dataset)
            # the raster this level is built from: the product for the first level
            if self.exponent == 1:
                # which is the payload of the dataset
                source = dataset.data.dataset
            # and the level beneath for every other
            else:
                # which must have been committed already
                source = pyramid.at(exponent=self.exponent - 1)
            # if it is not there
            if source is None:
                # the work was handed out too early, and that is a bug
                raise self.RecoverableError(
                    description=(
                        f"level {self.exponent - 1} of '{self.dataset}' is not there, "
                        f"so level {self.exponent} cannot be built"
                    )
                )
            # take hold of the level being built, for writing
            draft = pyramid.draft(exponent=self.exponent)
            # and its layout
            extent, tile, _ = pyramid.layout(exponent=self.exponent)
            # the records, one per tile
            records = []
            # go through my tiles
            for row, col in self.tiles:
                # where each one starts, in the coordinates of the level
                origin = (row * tile[0], col * tile[1])
                # and how far it reaches, clipped to the extent at the edges
                shape = tuple(
                    min(width, axis - start)
                    for width, axis, start in zip(tile, extent, origin)
                )
                # decimate the level below into it; a tile of pure fill is skipped, so
                # the level stays as sparse as the product it came from
                record = kernels.decimate(
                    source=source,
                    destination=draft,
                    datatype=dataset.datatype.htype,
                    origin=origin,
                    shape=shape,
                    stride=(2, 2),
                )
                # record what it held
                records.append(((row, col), record))
            # let go of the writable mapping
            del draft
        # any failure at all
        except Exception as error:
            # is reported as a task failure that leaves the crew member healthy
            raise self.RecoverableError(description=str(error)) from None
        # hand back the records
        return records

    # metamethods
    def __init__(self, reader, dataset, workspace, exponent, tiles, **kwds):
        # chain up
        super().__init__(**kwds)
        # the reader recipe
        self.reader = reader.pyre_name
        self.factory = reader.pyre_family()
        self.config = self._harvestReader(reader=reader)
        # the dataset, by its selector
        self.selector = dict(dataset.selector)
        self.dataset = dataset.pyre_name
        # where the levels live
        self.workspace = str(workspace.path)
        # the level being built, and the tiles of it that are mine
        self.exponent = exponent
        self.tiles = tuple(tuple(tile) for tile in tiles)
        # my identity: the reader, the dataset, the level, and the tiles; the credentials
        # are left out, since they do not change what the work is
        spec = {
            name: value for name, value in self.config.items() if name != "credentials"
        }
        self.identity = self._freeze(
            value=(
                self.reader,
                self.factory,
                spec,
                self.selector,
                self.exponent,
                self.tiles,
            )
        )
        # all done
        return

    # implementation details
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
            pyramid = qed.readers.nisar.pyramid(
                reader=reader, dataset=dataset, workspace=workspace
            )
            # and hand it to the dataset, so the renders find it
            dataset.pyramid = pyramid
        # attaching is idempotent: it picks up the levels that have appeared since
        pyramid.attach()
        # hand it back
        return pyramid


# end of file
