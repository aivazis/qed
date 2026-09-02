# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import journal
import qed

# the shared task core
from .Chore import Chore

# the parking place for the rendered payload
from .Spool import Spool


# the unit of work handed to the tile rendering crews
class Tile(Chore):
    """
    A picklable description of a tile rendering request

    Instances are built on the team side by harvesting the live view state, and executed on
    the worker side, where they rebuild the reader from scratch so each crew member owns its
    file handles
    """

    # interface - worker side
    def execute(self, readers, **kwds):
        """
        Render my tile using {readers}, the registry of data sources owned by my crew member
        """
        # carefully, since failures here should not poison the crew member
        try:
            # locate my reader, building it on first contact; a render installs the
            # client's controller state below, so measuring the datasets here would buy
            # numbers that are overwritten before a single pixel is produced
            reader = self._locateReader(readers=readers, measure=False)
            # find the dataset i'm after
            dataset = self._locateDataset(reader=reader)
            # and make sure it knows about its decimated levels, if there are any; the
            # reader registry is persistent, so this happens once per worker per product
            self._attachPyramid(reader=reader, dataset=dataset)
            # get its channel pipeline and mirror the controller state of the client view
            pipeline = self._configure(
                component=dataset.channel(name=self.tag), config=self.controllers
            )
            # aggregates render over the participating members
            extra = {"mask": self.mask} if self.stacked else {}
            # render the tile
            tile = dataset.render(
                channel=pipeline,
                zoom=self.zoom,
                origin=self.origin,
                shape=self.shape,
                **extra,
            )
        # any failure at all
        except Exception as error:
            # is reported as a task failure that leaves the crew member healthy
            raise self.RecoverableError(description=str(error)) from None
        # on success, park the encoded tile in a spool; its descriptor travels as ancillary
        # data on the crew channel, so the payload itself never crosses the wire
        spool = Spool.stash(data=memoryview(tile))
        # datasets that know how to measure themselves contribute source statistics
        sample = getattr(dataset, "sample", None)
        # if this one does
        if sample is not None:
            # carefully, since the render is the deliverable and the sample is a bonus
            try:
                # revisit the footprint this render saw and attach the mergeable record to
                # the report, so the team side can accumulate whole-dataset statistics
                spool.stats = sample(
                    zoom=self.zoom, origin=self.origin, shape=self.shape
                )
            # let the sample die quietly on any failure
            except Exception:
                # the tile is still good; it just doesn't contribute statistics
                pass
        # hand off the report
        return spool

    # implementation details - worker side
    def _attachPyramid(self, reader, dataset):
        """
        Give {dataset} the decimated levels of its product, when they exist

        The rasters it is read alongside get theirs at the same time: the kernel reads all
        of them with one origin and one stride, so a mask that arrived without its levels
        would hold the data at full resolution however deep its own pyramid went
        """
        # a dataset whose flavor knows nothing of levels, or a task built before the
        # server had a workspace, renders the way it always did
        if self.workspace is None or not hasattr(dataset, "resolve"):
            # straight off the product
            return dataset
        # go through the rasters this one is read alongside
        for companion in dataset.companions().values():
            # and give each of them their levels first, so they are in hand by the time the
            # data resolves a zoom and asks whether they can match it
            self._attachPyramid(reader=reader, dataset=companion)
        # the pyramid a render attached earlier, if any
        pyramid = getattr(dataset, "pyramid", None)
        # if there is one
        if pyramid is not None:
            # a pyramid that is still being built may have grown since; looking costs a
            # few checks for the records of the missing levels, and nothing at all once
            # every level is there
            if pyramid.reach() < pyramid.depth():
                # so pick up whatever appeared
                pyramid.attach()
            # either way, it is in hand
            return dataset
        # carefully, since a cache that cannot be opened must not cost us the tile
        try:
            # point a workspace at where the server keeps what it derives
            workspace = qed.workspaces.local(name=f"{self.reader}.crew.workspace")
            workspace.path = self.workspace
            # take hold of the pyramid and find out which levels it holds
            pyramid = qed.readers.nisar.pyramid(
                reader=reader, dataset=dataset, workspace=workspace
            )
            # take hold of whatever levels are there; a pyramid that finds none answers
            # every request with the base, which is what this dataset did anyway
            pyramid.attach()
        # if anything goes wrong
        except Exception as error:
            # the tile is the deliverable, so render it off the product; but say so where
            # somebody looking for the reason can find it, since a pyramid that silently
            # fails to attach is indistinguishable from one that was never built
            channel = journal.debug("qed.nexus.pyramid")
            # explain
            channel.log(f"{self.dataset}: no levels attached: {error}")
            # and render the way this dataset always did
            return dataset
        # show me what came back
        channel = journal.debug("qed.nexus.pyramid")
        # naming the levels, since that is what decides whether a zoomed out tile is cheap
        channel.log(f"{self.dataset}: levels {sorted(pyramid._levels)}")
        # hand it over
        dataset.pyramid = pyramid
        # all done
        return dataset

    # metamethods
    def __init__(self, view, channel, zoom, origin, shape, workspace=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # record the tile specification
        self.zoom = zoom
        self.origin = origin
        self.shape = shape
        # the channel tag is the last level of the {channel} spec
        self.tag = channel.split(".")[-1]
        # get the data source of the view
        reader = view.reader
        # record its name; it keys the worker side reader registry
        self.reader = reader.pyre_name
        # and its family, so workers can rebuild it
        self.factory = reader.pyre_family()
        # harvest the reader configuration needed to reopen the data source
        self.config = self._harvestReader(reader=reader)
        # the dataset is identified by its selector, which is stable across reader rebuilds
        self.selector = dict(view.dataset.selector)
        # record the dataset name as well; it keys the statistics accumulator on the team
        # side, and is deliberately not part of the identity, being derived state
        self.dataset = view.dataset.pyre_name
        # locate the visualization pipeline that carries the live controller state
        pipeline = view.pipeline(channel=channel)
        # and harvest its configuration
        self.controllers = self._harvestComponent(component=pipeline)
        # where the decimated levels of this product live, if any have been built; a
        # worker cannot be left to decide that for itself, or it would look somewhere the
        # server never wrote. deliberately not part of my identity: a level is cell for
        # cell what striding the base gives, so a tile served from one is the same tile
        self.workspace = str(workspace.path) if workspace is not None else None
        # aggregates render over a member participation mask
        self.stacked = isinstance(view.dataset, qed.stacks.dataset)
        # which travels with the request when there is one
        members = getattr(view, "members", None)
        self.mask = list(members) if self.stacked and members is not None else None
        # my identity is the complete request specification: two tiles are the same work
        # only when everything that shapes the render agrees, controller state included, so
        # equal tasks can share a single execution
        # access credentials are not part of what is rendered: a rotated token must not
        # invalidate cached work
        spec = {
            name: value for name, value in self.config.items() if name != "credentials"
        }
        self.identity = self._freeze(
            value=(
                self.reader,
                self.factory,
                spec,
                self.selector,
                self.tag,
                self.zoom,
                self.origin,
                self.shape,
                self.controllers,
                self.stacked,
                self.mask,
            )
        )
        # all done
        return


# end of file
