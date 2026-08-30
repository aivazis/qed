# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# the shared task core
from .Chore import Chore


# the unit of work that makes a dataset ready to be looked at
class Prepare(Chore):
    """
    A picklable request to build everything a dataset needs before it is worth viewing

    The work is one pass and three results. Building the first pyramid level reads every
    allocated cell of the dataset, which is the only expensive thing here; the statistics of
    the whole raster fall out of that pass rather than costing one of their own, and every
    level above the first is built from the one below at a quarter the size. What the user
    gets for it is a zoomed out view that reads a small dataset at unit stride instead of
    striding a large one, a display range measured over everything rather than guessed from
    a corner, and a thumbnail that is a cheap read of a level that already exists
    """

    # interface - worker side
    def execute(self, readers, **kwds):
        """
        Build the pyramid of my dataset and report what the pass measured
        """
        # carefully, since a malformed or unreachable product should not poison the worker
        try:
            # locate my reader, building it on first contact; nothing here needs the
            # legacy sample, since this task measures the whole raster
            reader = self._locateReader(readers=readers, measure=False)
            # find the dataset i am preparing
            dataset = self._locateDataset(reader=reader)
            # a workspace rooted where the server said, so the levels land in the same
            # place whichever process built them
            workspace = qed.workspaces.local(name=f"{self.reader}.crew.workspace")
            workspace.path = self.workspace
            # take hold of the pyramid
            pyramid = qed.readers.nisar.pyramid(
                reader=reader, dataset=dataset, workspace=workspace
            )
            # build it, all the way to the level whose raster fits in a single tile
            pyramid.build(depth=self.depth)
            # collect what the pass measured
            statistics = pyramid.statistics
            # how deep it actually went, which is the depth its companions must reach
            reach = pyramid.reach()
            # and let the file go, so the levels are on disk before anybody is told
            pyramid.close()
            # the rasters a render of this dataset reads alongside its payload -- the mask
            # of a masked channel -- are decimated too, and to exactly the same depth: the
            # kernel reads all of them with one origin and one stride, so a level the mask
            # lacks is a level the data cannot use either
            self._prepareCompanions(
                reader=reader, dataset=dataset, workspace=workspace, depth=reach
            )
        # any failure at all
        except Exception as error:
            # is reported as a task failure that leaves the worker healthy
            raise self.RecoverableError(description=str(error)) from None
        # hand back the record of what the raster holds, which is the part the server
        # cannot get any other way
        return statistics

    # implementation details - worker side
    def _prepareCompanions(self, reader, dataset, workspace, depth: int) -> None:
        """
        Decimate the rasters {dataset} is read alongside, to a depth of {depth}
        """
        # a payload that got no levels of its own has nothing for its companions to match
        if depth == 0:
            # so leave them alone
            return
        # go through them
        for companion in dataset.companions().values():
            # each gets its own levels, in its own group of the same cache; they are built
            # one after another rather than together, so the file is opened once at a time
            pyramid = qed.readers.nisar.pyramid(
                reader=reader, dataset=companion, workspace=workspace
            )
            # to exactly the depth the payload reached, whatever its own extent would have
            # supported: a companion that stopped short would cost the data its deepest
            # levels, and one that went further would hold levels nobody can pair with
            pyramid.build(depth=depth)
            # its statistics describe the mask rather than the data, so they are not
            # reported; let the file go
            pyramid.close()
        # all done
        return

    # metamethods
    def __init__(self, reader, dataset, workspace, depth=0, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the reader name; it keys the worker side reader registry
        self.reader = reader.pyre_name
        # and its family, so workers can rebuild it
        self.factory = reader.pyre_family()
        # harvest the reader configuration needed to open the data source
        self.config = self._harvestReader(reader=reader)
        # the dataset is identified by its selector, which is stable across rebuilds
        self.selector = dict(dataset.selector)
        # its name keys the preparation record on the server side
        self.dataset = dataset.pyre_name
        # where the derived data goes; the server owns the workspace, and a worker cannot
        # be left to decide for itself, or the levels would land somewhere nobody looks
        self.workspace = str(workspace.path)
        # how far up to build; zero means as far as the extent allows
        self.depth = depth
        # my identity is the dataset i am preparing: two requests to prepare the same
        # dataset are the same work, so the second joins the first rather than building
        # the same levels twice
        spec = {
            name: value for name, value in self.config.items() if name != "credentials"
        }
        self.identity = self._freeze(
            value=(self.reader, self.factory, spec, self.selector, self.depth)
        )
        # all done
        return


# end of file
