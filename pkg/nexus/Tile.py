# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
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

    # metamethods
    def __init__(self, view, channel, zoom, origin, shape, **kwds):
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
